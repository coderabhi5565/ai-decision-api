# AI Decision API

A small end-to-end AI support-ticket decision system built with FastAPI, Streamlit, SQLite, JWT authentication, Gemini, and local RAG.

The system takes a customer support message, retrieves relevant policy information from a local knowledge base, and uses Gemini to produce a structured decision with a reason, confidence score, and policy sources.

The LLM output is then passed through a small deterministic Policy Guard before the final decision is persisted.

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
- Deterministic policy guardrails
- Atomic ticket and decision persistence
- Streamlit frontend
- Automated API and policy-guard tests
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
                       Policy Retrieval      Structured
                              |               Decision
                              |                   |
                              +---------+---------+
                                        |
                                 Source Validation
                                        |
                                 Policy Guard
                                        |
                                  Final Decision
                                        |
                                     SQLite
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
│   ├── policy_guard.py
│   ├── retrieval.py
│   └── schemas.py
│
├── tests/
│   ├── test_api.py
│   ├── test_policy_guard.py
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

The application uses the policy documents in knowledge_base/ as its retrieval source.

To generate the local vector store manually:

python -m src.retrieval

This:

Loads the policy documents.
Splits them into chunks.
Generates Gemini embeddings.
Stores embeddings locally.
Stores chunk metadata locally.

The generated vector store is ignored by Git.

When the application starts, it can reuse the existing vector store instead of regenerating embeddings on every startup.

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

The frontend communicates with the backend through HTTP and does not access the database directly.

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
Top 3 Relevant Policy Chunks
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
Source Validation
      |
      v
Policy Guard
      |
      v
Final Decision
      |
      v
SQLite

The model is instructed to use only the supplied policy context. If the available information is insufficient, it should return NEEDS_MORE_INFORMATION.

Policy Guard

The LLM is not treated as the final authority for business rules.

After Gemini produces a structured decision, a small deterministic Policy Guard checks a few high-confidence constraints before the decision is persisted.

Current guardrails include:

Damaged orders above ₹2,000 require photos before refund or replacement approval.
Defective orders above ₹3,000 require evidence before replacement approval.
Orders cannot be cancelled through the cancellation flow after dispatch.
Orders that have not arrived 8–10 days after dispatch require a shipping investigation.

The guard intentionally does not duplicate the entire policy knowledge base using regular expressions. The goal is to enforce a small number of high-confidence rules without creating a brittle rule engine.

Conceptually:

Natural Language
      |
      v
     RAG
      |
      v
    Gemini
      |
      v
AI Proposed Decision
      |
      v
Policy Guard
      |
      v
Final Decision

This separates two responsibilities:

LLM: interpret the customer's natural-language request using retrieved policy context.
Policy Guard: enforce deterministic business constraints that can be extracted reliably from the ticket.
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

Database

The application uses three main tables:

users
  |
  | 1-to-many
  v
tickets
  |
  | 1-to-1
  v
decisions

A ticket belongs to one authenticated user and can have one persisted AI decision.

Ticket creation and decision persistence happen within the same database transaction. If the AI decision fails, the transaction is rolled back instead of leaving an incomplete ticket record.

Testing

Run the automated tests:

pytest -q

The tests use an in-memory SQLite database and mock the Gemini decision function for API tests, so the main test suite does not depend on Gemini availability.

The Policy Guard also has dedicated unit tests covering:

expensive damaged orders
evidence-present cases
expensive defective orders
cancellation after dispatch
shipping delays
already-correct decisions

Current test result:

17 passed
Evaluation

The supplied sample cases can be evaluated with:

python -m tests.evaluate

The evaluation runner compares the model's predicted action with the expected action from sample_test_cases.json.

Latest evaluation on the provided 5 sample cases:

Correct    : 5/5
Incorrect  : 0/5
Failed     : 0/5
Evaluated  : 5/5
Accuracy   : 100.00%

This result is specific to the provided 5-case evaluation set and should not be interpreted as a production accuracy measurement.

Security
Passwords are hashed using Argon2.
JWT is used for authentication.
JWT secrets and Gemini API keys are stored in environment variables.
.env is excluded from Git.
Ticket queries are restricted to the authenticated user.
JWT expiry is enforced.
Structured LLM output is validated using Pydantic.
Returned policy sources are validated against the retrieved context.
Design Notes
Local Retrieval

The knowledge base is currently small, so a local NumPy-based vector store is sufficient. A hosted vector database is not necessary for this scope.

Embeddings are generated using Gemini's embedding model and compared using cosine similarity.

Retrieval and Decision Separation

The retrieval layer is kept separate from the decision layer so that the retrieval implementation can be changed later without changing the API structure.

Structured LLM Output

Gemini is configured to return a structured response matching the DecisionOutput Pydantic schema.

This avoids relying on free-form text parsing for the final decision.

Policy Guard

The Policy Guard was kept intentionally small.

Instead of encoding every policy rule into regular expressions, only rules that can be checked with relatively high confidence from the raw ticket text are enforced deterministically.

This reduces the risk of creating a large and brittle rule engine while still preventing some high-impact LLM decision errors.

Limitations
SQLite is used for simplicity and assignment scope.
The local vector store needs to be regenerated when policy documents change.
Gemini availability and API limits can affect live AI requests.
The current retrieval implementation is intentionally lightweight.
Policy Guard extraction is based on simple text patterns and therefore does not cover every possible way a customer may describe an issue.
The evaluation dataset contains only five provided sample cases and is not representative of production traffic.
The deployed SQLite database uses ephemeral storage on the free deployment environment.
License

This project was built as part of an internship assignment.