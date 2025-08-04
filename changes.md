## Major Issues Identified

The original code mixed concerns with global DB connections and bootstrap logic tangled with route handlers, making it hard to maintain or extend. It was vulnerable to SQL injection because it used string interpolation for queries with user input. Passwords were stored and compared in plaintext, which is a critical security flaw. Responses were inconsistent (raw tuples or strings) with no proper HTTP status codes, and there was no input validation or structured error handling, leading to brittle and unsafe behavior.

## Changes Made and Why

I refactored the code into `init_db.py` and `app.py` to separate database management from routing, enabling cleaner lifecycle handling and easier future swaps (e.g., to another DB). All SQL queries were converted to parameterized form to eliminate SQL injection risks, and password handling was upgraded to use proper hashing/verification to secure credentials. The API was normalized to return structured JSON with appropriate HTTP status codes, and input validation was added to surface bad requests early. Environment configuration support was introduced (via `.env`), and database initialization was centralized to ensure schema existence and optional seeding without ad hoc scripts.

## Assumptions or Trade-offs

I assumed that sticking with SQLite was acceptable for the current scope, trading off scalability for simplicity and speed of setup; the abstraction still allows swapping to a more robust DB later. Instead of pulling in a full schema-validation library (e.g., Marshmallow), I implemented lightweight manual validation to avoid over-engineering under the time constraint. Seeding of sample data uses unhashed passwords in the development/demo initializer—this was a conscious temporary convenience with the understanding it must be removed or replaced before production. Error messages were kept informative but not overly detailed to balance debuggability with not leaking internal state.

## What I Would Do With More Time

Given more time, I’d introduce comprehensive automated tests covering edge cases, input fuzzing, and security regressions, and integrate CI to run them on each push. I would replace SQLite with a production-grade database (PostgreSQL or similar), add migrations, and abstract the persistence layer further to support multi-environment deployments. Authentication would be extended to token-based (JWT or session) flows, with rate limiting and account lockout to mitigate brute-force attacks, plus email verification. Finally, I’d add observability: structured logging, metrics, and error reporting to monitor health and quickly diagnose issues in real deployments.
