# Development Notes

This project was developed by implementing and understanding the
requirements step by step.

AI assistance was used as a learning and debugging aid during development.
It was mainly used to understand unfamiliar concepts, troubleshoot issues,
and understand Streamlit implementation details. The suggested solutions
were tested and modified when required.

## AI Assistance

AI assistance was used to help understand and debug:

- FastAPI authentication and JWT
- Streamlit and HTTP communication
- Automated testing and mocking

The application was implemented incrementally based on the assignment
requirements rather than blindly accepting generated solutions.

---

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

This keeps unrelated responsibilities from being mixed together.

### 2. Single Responsibility Principle

Each major module has a focused responsibility.

For example, `retrieval.py` is responsible for finding relevant policy
context, while `decision.py` uses that context to generate the final
structured AI decision.

This makes individual components easier to understand, test, and modify.

### 3. Dependency Injection

FastAPI dependency injection is used for database sessions and the
authenticated user.

For example:

```python
db: Session = Depends(get_db)

The database dependency can also be replaced during testing with an
in-memory SQLite database. This allows API tests to run independently
of the actual application database.

4. Keep It Simple (KISS)

The project avoids unnecessary infrastructure because the assignment
has a small scope.

The RAG pipeline uses Gemini embeddings, NumPy, and cosine similarity
instead of introducing a hosted vector database.

Similarly, the application uses a single FastAPI backend and SQLite
instead of introducing microservices, Redis, Kafka, or other unnecessary
components.

Engineering Decisions
Top-K Retrieval

The retrieval layer selects the top 3 most relevant policy chunks instead
of sending the complete knowledge base to Gemini for every ticket.

A similarity threshold was considered, but it was not used because the
observed similarity scores of valid and incomplete cases overlapped.

Atomic Persistence

Ticket creation and decision persistence are handled in the same database
transaction.

The ticket is flushed to obtain its ID, the AI decision is generated,
and both are committed together. If the AI or database operation fails,
the transaction is rolled back.

This prevents a ticket from being stored without its corresponding
decision.

Testing

The API test suite uses an in-memory SQLite database and mocks the Gemini
decision function.

This makes the tests deterministic and prevents them from depending on
Gemini API availability or consuming API quota.

The separate evaluation script uses the actual Gemini API and the supplied
sample test cases to evaluate the AI decision pipeline.

Security

The application uses:

Argon2 password hashing
JWT authentication
User-level authorization
Pydantic request validation
Environment variables for secrets

The .env file is excluded from Git, while .env.example is included
for configuration reference.