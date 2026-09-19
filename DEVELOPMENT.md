# Development Notes

This project was developed by implementing and understanding the
requirements step by step.

AI assistance was used as a learning and debugging aid during development.
It was mainly used to understand unfamiliar concepts, troubleshoot issues,
and understand implementation details. Suggested solutions were reviewed,
tested, and modified when required.

The application was implemented incrementally based on the assignment
requirements rather than blindly accepting generated solutions.


## AI Assistance

AI assistance was used to help understand and debug:

- FastAPI authentication and JWT
- Streamlit and HTTP communication
- Gemini structured output
- Automated testing and mocking

The final implementation was tested locally and verified using the
automated test suite and the supplied evaluation cases.


## Design Principles

### 1. Separation of Concerns

Different responsibilities are kept in separate modules.

- `api.py` handles HTTP endpoints.
- `auth.py` handles password hashing and JWT authentication.
- `database.py` manages database sessions.
- `models.py` defines database entities.
- `schemas.py` handles API validation.
- `retrieval.py` handles knowledge-base retrieval.
- `decision.py` handles LLM decision generation and validation.
- `policy_guard.py` handles deterministic business-rule checks.

This keeps unrelated responsibilities separate.

### 2. Single Responsibility Principle

Each major module has a focused responsibility.

For example, `retrieval.py` is responsible for finding relevant policy
context, while `decision.py` uses that context to generate the structured
AI decision.

The Policy Guard is kept separate because deterministic business rules
have a different responsibility from LLM-based interpretation.

### 3. Dependency Injection

FastAPI dependency injection is used for database sessions and the
authenticated user.

For example:

```python
db: Session = Depends(get_db)

The database dependency can be replaced during testing with an in-memory
SQLite database.

4. Keep It Simple (KISS)

The project avoids unnecessary infrastructure because of the small scope.

The RAG pipeline uses Gemini embeddings, NumPy, and cosine similarity
instead of introducing a hosted vector database.

Similarly, a single FastAPI backend and SQLite are sufficient for this
assignment.

AI Decision Pipeline

The main decision flow is:

Customer Ticket
      |
      v
Query Embedding
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

The LLM interprets the customer's natural-language request using the
retrieved policy context.

The Policy Guard then enforces a small set of high-confidence deterministic
business constraints before the decision is persisted.

Engineering Decisions
Top-K Retrieval

The retrieval layer selects the top 3 relevant policy chunks instead of
sending the complete knowledge base to Gemini.

A similarity threshold was considered, but valid and incomplete cases had
overlapping similarity scores. An arbitrary threshold could therefore
reject useful policy context.

Structured LLM Output

Gemini returns a structured response matching the DecisionOutput
Pydantic model:

action
confidence
reason
sources

The response is validated before being used by the application.

The returned sources are also checked against the policy chunks that were
actually retrieved.

Atomic Persistence

Ticket creation and decision persistence happen in the same database
transaction.

The ticket is flushed to obtain its ID, the AI decision is generated, and
both records are committed together.

If the AI or database operation fails, the transaction is rolled back.

Policy Guard

The LLM is not treated as the final authority for deterministic business
rules.

The Policy Guard currently enforces:

Damaged orders above ₹2,000 require photos before approval.
Defective orders above ₹3,000 require evidence before replacement.
Orders cannot be cancelled after dispatch.
Orders not received 8–10 days after dispatch require a shipping
investigation.

The guard intentionally does not duplicate the entire policy knowledge base.
Encoding every policy rule using regex would make the implementation
brittle.

Instead, only rules that can be extracted from the ticket with relatively
high confidence are enforced deterministically.

The LLM handles broader natural-language interpretation using the retrieved
policy context.

Testing

The API tests use an in-memory SQLite database and mock the Gemini decision
function.

This makes the main test suite deterministic and independent of Gemini
availability.

The Policy Guard has separate unit tests for its deterministic rules.

Run all tests with:

pytest -q

Current result:

17 passed

The separate evaluation runner uses the actual Gemini API and the supplied
sample cases:

python -m tests.evaluate

Latest evaluation:

Correct    : 5/5
Incorrect  : 0/5
Failed     : 0/5
Evaluated  : 5/5
Accuracy   : 100.00%

This result is specific to the five supplied sample cases and is not a
production accuracy measurement.

Security

The application uses:

Argon2 password hashing
JWT authentication
User-level authorization
Pydantic request validation
Environment variables for secrets

The .env file is excluded from Git and .env.example is provided as a
configuration template.

Ticket queries are restricted to the authenticated user.

Limitations
SQLite is used for simplicity and assignment scope.
The local vector store needs to be regenerated when policy documents
change.
The retrieval implementation is intentionally lightweight.
Gemini availability and API limits can affect live requests.
Policy Guard extraction uses simple text patterns and does not cover
every possible natural-language variation.
The evaluation dataset contains only five supplied sample cases.