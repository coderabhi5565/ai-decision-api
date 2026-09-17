import json

from fastapi import Depends, FastAPI, HTTPException, status
from google.genai.errors import APIError
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from .auth import (
    create_access_token,
    get_current_user,
    hash_password,
    verify_password,
)
from .database import Base, engine, get_db
from .decision import make_decision
from .models import Decision, Ticket, User
from .retrieval import ingest_knowledge_base, vector_store_exists
from .schemas import (
    LoginRequest,
    TicketCreate,
    TicketResponse,
    TokenResponse,
    UserCreate,
    UserResponse,
)


Base.metadata.create_all(bind=engine)


if not vector_store_exists():
    ingest_knowledge_base()


app = FastAPI(
    title="AI Decision API",
    version="1.0.0"
)


@app.get("/")
def root():
    return {"message": "AI Decision API is running"}


@app.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED
)
def register(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    existing_user = db.query(User).filter(
        User.email == user_data.email
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered"
        )

    user = User(
        email=user_data.email,
        password_hash=hash_password(user_data.password)
    )

    try:
        db.add(user)
        db.commit()
        db.refresh(user)

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered"
        )

    except SQLAlchemyError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error while creating user"
        )

    return user


@app.post(
    "/login",
    response_model=TokenResponse
)
def login(
    login_data: LoginRequest,
    db: Session = Depends(get_db)
):
    try:
        user = db.query(User).filter(
            User.email == login_data.email
        ).first()

    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error while logging in"
        )

    if user is None or not verify_password(
        login_data.password,
        user.password_hash
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    access_token = create_access_token(user.id)

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


@app.get(
    "/me",
    response_model=UserResponse
)
def get_me(
    current_user: User = Depends(get_current_user)
):
    return current_user


@app.post(
    "/tickets",
    response_model=TicketResponse,
    status_code=status.HTTP_201_CREATED
)
def create_ticket(
    ticket_data: TicketCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    ticket = Ticket(
        user_id=current_user.id,
        message=ticket_data.message
    )

    try:
        db.add(ticket)
        db.flush()

        decision = make_decision(ticket_data.message)

        ticket_decision = Decision(
            ticket_id=ticket.id,
            action=decision.action,
            reason=decision.reason,
            confidence=decision.confidence,
            sources=json.dumps(decision.sources)
        )

        db.add(ticket_decision)
        db.commit()
        db.refresh(ticket)

        return {
            "id": ticket.id,
            "message": ticket.message,
            "created_at": ticket.created_at,
            "decision": {
                "action": decision.action,
                "reason": decision.reason,
                "confidence": decision.confidence,
                "sources": decision.sources
            }
        }

    except APIError as exc:
       db.rollback()

       print("GEMINI API ERROR:")
       print(type(exc).__name__, exc)

       raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail="AI service is temporarily unavailable"
      )

    except SQLAlchemyError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error while processing ticket"
        )

    except Exception:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process ticket"
        )


@app.get(
    "/tickets",
    response_model=list[TicketResponse]
)
def get_tickets(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        tickets = db.query(Ticket).filter(
            Ticket.user_id == current_user.id
        ).all()

    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error while fetching tickets"
        )

    results = []

    for ticket in tickets:
        decision = None

        if ticket.decision:
            decision = {
                "action": ticket.decision.action,
                "reason": ticket.decision.reason,
                "confidence": ticket.decision.confidence,
                "sources": json.loads(ticket.decision.sources)
            }

        results.append({
            "id": ticket.id,
            "message": ticket.message,
            "created_at": ticket.created_at,
            "decision": decision
        })

    return results


@app.get(
    "/tickets/{ticket_id}",
    response_model=TicketResponse
)
def get_ticket(
    ticket_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        ticket = db.query(Ticket).filter(
            Ticket.id == ticket_id,
            Ticket.user_id == current_user.id
        ).first()

    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error while fetching ticket"
        )

    if ticket is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found"
        )

    decision = None

    if ticket.decision:
        decision = {
            "action": ticket.decision.action,
            "reason": ticket.decision.reason,
            "confidence": ticket.decision.confidence,
            "sources": json.loads(ticket.decision.sources)
        }

    return {
        "id": ticket.id,
        "message": ticket.message,
        "created_at": ticket.created_at,
        "decision": decision
    }