# Development Notes

This project was developed primarily by implementing and understanding
the requirements step by step.

AI assistance was used as a learning and debugging aid during development,
rather than as a replacement for writing the application.

## How AI Assistance Was Used

AI assistance was mainly used in the following situations:

- When I encountered a concept that I had not worked with before, I first
  used AI to understand the concept, its purpose, and how it fits into the
  application. I then implemented it in the project.

- When I encountered implementation or debugging issues, I used AI to
  understand the cause of the problem and possible solutions, and then
  applied the required changes.

- AI was used to help understand and debug issues related to:
  - FastAPI authentication and JWT
  - SQLAlchemy database interactions
  - Streamlit and HTTP communication
  - Automated testing and mocking

- AI assistance was also used during the Streamlit implementation,
  particularly for understanding the Streamlit APIs and connecting the
  frontend to the FastAPI backend.

## Coding Approach

The application code was written and implemented incrementally based on
the assignment requirements.

The development process generally followed this pattern:

1. Understand the requirement.
2. Identify any unfamiliar concept.
3. Learn the concept with the help of AI when necessary.
4. Implement the concept in the project.
5. Run and test the implementation.
6. Debug issues when they occurred.
7. Review the final implementation against the assignment requirements.

AI suggestions were not treated as automatically correct. Implementations
were tested locally and modified when required.

## Engineering Decisions

### 1. Retrieve Only the Most Relevant Policy Chunks

Instead of sending the complete knowledge base to Gemini for every ticket,
the retrieval layer selects the top 3 most relevant policy chunks using
embedding similarity.

I checked the retrieval results on the supplied sample cases. The correct
policy document was ranked first for the concrete cases, including damaged
goods, returns, shipping, and wrong-item tickets.

I chose top-k retrieval because it keeps the amount of policy context sent
to the model focused on the current ticket. It also avoids introducing
unnecessary context as the knowledge base grows.

I considered adding a similarity-score threshold that would reject low
scoring retrievals. However, the observed scores for the intentionally
incomplete case overlapped with scores from valid cases, so I did not add
a hard threshold based only on similarity.

### 2. Keep Ticket and Decision Persistence Atomic

Creating a ticket and storing its AI decision are treated as one database
transaction.

The ticket is added to the database first, but the transaction is not
committed until the AI decision has been generated and the corresponding
decision record has also been added.

If the AI service or database operation fails, the transaction is rolled
back.

This prevents the database from containing a ticket that appears in the
user's history without its corresponding decision.

### Separate Retrieval and Decision Layers

The retrieval and decision-generation logic are kept separate.

The retrieval layer is responsible for finding relevant policy chunks,
while the decision layer uses the retrieved context to generate and
validate
the structured AI decision.

This keeps the components easier to understand, test, and modify
independently.

## Testing Approach

Automated API tests use an in-memory SQLite database.

The Gemini decision function is mocked in API tests so that the automated
test suite does not depend on network availability or consume Gemini API
quota.

The separate evaluation script uses the actual Gemini API to evaluate
the AI decision pipeline against the supplied sample test cases.

## Security

The application uses:

- Argon2 password hashing
- JWT authentication
- User-level authorization
- Pydantic request validation
- Environment variables for API keys and secrets
- .env excluded from Git

## Development Summary

AI assistance was used primarily as a learning, debugging, and
implementation-support tool.

The goal was to understand the concepts involved and then implement and
test them as part of the project, rather than blindly accepting generated
code.