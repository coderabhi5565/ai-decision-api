# AI Decision API

An end-to-end AI-powered support ticket decision assistant built as part of the Maxsor Labs internship assignment.

The application accepts customer support tickets, retrieves relevant information from a local policy knowledge base, and uses Gemini to generate a structured decision with a reason, confidence score, and supporting sources.

## Features

- User registration and login
- JWT-based authentication
- Password hashing
- Protected REST APIs
- User-specific ticket authorization
- SQLite database
- Support ticket creation and history
- Local RAG-based policy retrieval
- Gemini-powered decision generation
- Structured and validated AI responses
- Streamlit frontend
- Evaluation script for testing AI decisions
- Automated tests for core API functionality

## Architecture

```text
                    ┌──────────────────┐
                    │    Streamlit     │
                    │    Frontend      │
                    └────────┬─────────┘
                             │ HTTP
                             ▼
                    ┌──────────────────┐
                    │     FastAPI      │
                    │      Backend     │
                    └───────┬──────────┘
                            │
              ┌─────────────┼─────────────┐
              │             │             │
              ▼             ▼             ▼
        ┌──────────┐  ┌──────────┐  ┌─────────────┐
        │  SQLite  │  │   RAG    │  │    Gemini   │
        │ Database │  │ Retrieval│  │     LLM     │
        └──────────┘  └──────────┘  └─────────────┘
Tech Stack
Python
FastAPI
Streamlit
SQLite
SQLAlchemy
JWT
Pydantic
NumPy
Gemini API
pytest
Project Structure
ai-decision-api/
│
├── README.md
├── DEVELOPMENT.md
├── requirements.txt
├── .env.example
├── .gitignore
│
├── data/
│
├── knowledge_base/
│
├── src/
│   ├── __init__.py
│   ├── api.py
│   ├── auth.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   ├── retrieval.py
│   └── decision.py
│
├── streamlit_app.py
│
└── tests/
Setup
1. Clone the repository
git clone <repository-url>
cd ai-decision-api
2. Create a virtual environment
python -m venv .venv

Activate it on Windows:

.venv\Scripts\activate
3. Install dependencies
pip install -r requirements.txt
4. Configure environment variables

Create a .env file based on .env.example.

GEMINI_API_KEY=your_gemini_api_key
JWT_SECRET=your_random_secret

Never commit .env or API keys to the repository.

Running the Application
Start the FastAPI backend
uvicorn src.api:app --reload

The API will be available at:

http://127.0.0.1:8000

Interactive API documentation:

http://127.0.0.1:8000/docs
Start the Streamlit frontend

In another terminal:

streamlit run streamlit_app.py
API Endpoints
Method	Endpoint	Description
POST	/register	Register a new user
POST	/login	Authenticate a user and receive JWT
GET	/me	Get authenticated user information
POST	/tickets	Create a support ticket and generate a decision
GET	/tickets	Get the authenticated user's tickets
GET	/tickets/{id}	Get a specific ticket

Protected endpoints require:

Authorization: Bearer <JWT>

Users can only access their own tickets and decisions.

RAG Pipeline

The knowledge base is processed locally.

Policy Documents
       │
       ▼
    Chunking
       │
       ▼
   Embeddings
       │
       ▼
 Local Storage
       │
       │
Incoming Ticket
       │
       ▼
 Ticket Embedding
       │
       ▼
Similarity Search
       │
       ▼
Relevant Policy Chunks
       │
       ▼
 Gemini
       │
       ▼
Structured Decision

The retrieved policy context is provided to Gemini so that decisions are grounded in the supplied policies.

Decision Output

The AI produces a structured decision containing:

Action
Confidence
Reason
Sources

Example:

{
  "action": "REQUEST_PHOTOS",
  "confidence": 0.91,
  "reason": "The order is above ₹2,000 and the damaged goods policy requires photographs.",
  "sources": [
    "damaged_goods.md"
  ]
}

When the available policy information is insufficient, the system can return:

NEEDS_MORE_INFORMATION

rather than inventing an answer.

Testing

Run the test suite with:

pytest

The project also includes an evaluation runner for the supplied test cases.

Security
Passwords are stored as hashes rather than plaintext.
JWTs are required for protected endpoints.
JWTs are validated by the backend.
Ticket ownership is checked before returning protected resources.
Secrets are loaded from environment variables.
.env is excluded from version control.
