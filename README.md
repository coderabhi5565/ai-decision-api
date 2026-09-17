# AI Decision API

A small end-to-end AI support-ticket decision system built with FastAPI,
Streamlit, SQLite, JWT authentication, Gemini, and local RAG.

The system takes a customer support message, retrieves relevant policy
information from a local knowledge base, and uses Gemini to produce a
structured decision with a reason, confidence score, and policy sources.

## Features

- User registration and login
- Password hashing with Argon2
- JWT-based authentication
- User-level ticket authorization
- Support ticket creation and history
- SQLite database with SQLAlchemy
- Local RAG using Gemini embeddings and NumPy
- Structured Gemini decision output
- Policy source tracking
- Streamlit frontend
- Automated API tests
- Sample test-case evaluation

## Architecture

```text
                    Streamlit
                        |
                     HTTP/REST
                        |
                     FastAPI
                        |
        +---------------+---------------+
        |               |               |
     JWT Auth        SQLite         AI Pipeline
                        |               |
                    Tickets +          |
                    Decisions          |
                                        |
                              +---------+---------+
                              |                   |
                            RAG               Gemini
                              |                   |
                       Policy Retrieval      Decision
                              |                   |
                              +---------+---------+
                                        |
                                   Structured
                                    Decision
Project Structure
ai-decision-api/
│
├── data/
│   ├── tickets.csv
│   └── vector_store/
│
├── knowledge_base/
│   ├── cancellations.md
│   ├── damaged_goods.md
│   ├── defective_products.md
│   ├── returns.md
│   ├── shipping.md
│   └── wrong_item.md
│
├── src/
│   ├── api.py
│   ├── auth.py
│   ├── database.py
│   ├── decision.py
│   ├── models.py
│   ├── retrieval.py
│   └── schemas.py
│
├── tests/
│   ├── test_api.py
│   ├── test_decision_manual.py
│   ├── test_retrieval_manual.py
│   └── evaluate.py
│
├── .env.example
├── .gitignore
├── DEVELOPMENT.md
├── DATA_NOTES.md
├── README.md
├── requirements.txt
├── sample_test_cases.json
└── streamlit_app.py
Tech Stack
Python
FastAPI
Streamlit
SQLite
SQLAlchemy
Pydantic
JWT
Argon2 password hashing
Google Gemini API
NumPy
Pytest
Setup
1. Clone the repository
git clone <your-repository-url>
cd ai-decision-api
2. Create a virtual environment
python -m venv .venv

Activate it on Windows:

.venv\Scripts\activate
3. Install dependencies
pip install -r requirements.txt
4. Configure environment variables

Create a .env file:

GEMINI_API_KEY=your_gemini_api_key
JWT_SECRET=your_jwt_secret

Do not commit .env.

The repository contains .env.example as a template.

Knowledge Base Ingestion

Before using the AI decision pipeline, generate the local vector store:

python -m src.retrieval

This:

Loads the policy documents.
Splits them into chunks.
Generates Gemini embeddings.
Stores embeddings locally.
Stores chunk metadata locally.

The generated vector store is ignored by Git.

Run the Backend

Start FastAPI:

uvicorn src.api:app --reload

API:

http://127.0.0.1:8000

Swagger documentation:

http://127.0.0.1:8000/docs
Run the Frontend

In another terminal:

streamlit run streamlit_app.py

The Streamlit application normally runs at:

http://localhost:8501

The frontend communicates with the backend through HTTP and does not access
the database directly.

AI Decision Flow
Customer Ticket
      |
      v
Query Embedding
      |
      v
Cosine Similarity
      |
      v
Top Relevant Policy Chunks
      |
      v
Gemini
      |
      v
Structured Decision
      |
      +---- Action
      +---- Confidence
      +---- Reason
      +---- Sources
      |
      v
SQLite

The model is instructed to use only the supplied policy context. If the
available information is insufficient, it can return NEEDS_MORE_INFORMATION.

API Endpoints
Method	Endpoint	Description	Auth
POST	/register	Create a user	No
POST	/login	Login and receive JWT	No
GET	/me	Get current user	Yes
POST	/tickets	Create and analyze a ticket	Yes
GET	/tickets	Get current user's tickets	Yes
GET	/tickets/{id}	Get one of current user's tickets	Yes

Protected endpoints use:

Authorization: Bearer <JWT>

Users can only access their own tickets.

Testing

Run the automated tests:

pytest -v

The tests use an in-memory SQLite database and mock the Gemini decision
function, so the test suite does not depend on the Gemini API.

Evaluation

The supplied sample cases can be evaluated with:

python -m tests.evaluate

The evaluation runner compares the model's predicted action with the
expected action from sample_test_cases.json.

Security
Passwords are hashed using Argon2.
JWT is used for authentication.
JWT secrets and Gemini API keys are stored in environment variables.
.env is excluded from Git.
Ticket queries are restricted to the authenticated user.
Design Notes

The knowledge base is currently small, so a local NumPy-based vector store
is sufficient. A hosted vector database is not necessary for this scope.

The application keeps the retrieval layer separate from the decision layer,
so the retrieval implementation can be changed later without changing the
API structure.

Limitations
SQLite is used for simplicity and assignment scope.
The local vector store needs to be regenerated when policy documents change.
Gemini availability and API limits can affect live AI requests.
The current retrieval implementation is intentionally lightweight.
License

This project was built as part of an internship assignment.
