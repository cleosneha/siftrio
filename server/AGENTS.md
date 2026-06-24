# Server Development Guidelines

## Tech Stack

- FastAPI
- PostgreSQL
- SQLAlchemy
- Alembic
- pgvector

---

## Architecture Principles

### Clean Architecture

Flow:

API
→ Controller
→ Service
→ Repository
→ Database

Each layer has one responsibility.

---

### DRY Principle

Avoid duplicated:

- Queries
- Validation logic
- Error handling
- Response formatting

Create reusable abstractions only when repetition is real.

---

### No Overengineering

Do not introduce:

- Microservices
- Event buses
- Kafka
- Complex CQRS
- Distributed systems

Build only what the project currently needs.

---

## Folder Responsibilities

### api/

Contains route registration.

Responsibilities:

- Register routers
- Version APIs
- Organize endpoints

No business logic.

---

### controllers/

Responsibilities:

- Receive requests
- Validate input
- Call services
- Return responses

Controllers should remain thin.

---

### services/

Contains business logic.

Examples:

- meeting_service
- project_service
- approval_service

Responsibilities:

- Coordinate workflows
- Execute business rules
- Interact with repositories

---

### repositories/

Contains database operations.

Examples:

- meeting_repository
- project_repository

Responsibilities:

- Queries
- Inserts
- Updates
- Deletes

No business logic.

---

### models/

Database models.

Responsibilities:

- SQLAlchemy entities
- Relationships
- Database structure

---

### schemas/

Pydantic models.

Responsibilities:

- Request schemas
- Response schemas
- Validation

---

### agents/

AI reasoning layer.

Examples:

- meeting_agent
- knowledge_agent
- approval_agent

Responsibilities:

- Prompt orchestration
- Tool usage
- Structured outputs

Agents must not directly access the database.

Agents return structured data.

---

### tools/

External integrations.

Examples:

- github_tool
- jira_tool
- calendar_tool

Responsibilities:

- Third-party API communication

Keep integrations isolated.

---

### middleware/

Responsibilities:

- Logging
- Authentication
- Request tracking

Keep middleware lightweight.

---

### utils/

Reusable helper functions.

Examples:

- date utilities
- formatting
- common helpers

Avoid placing business logic here.

---

## API Standards

### Unified Response Format

Success

{
"success": true,
"message": "Meeting created successfully",
"data": {}
}

Error

{
"success": false,
"message": "Meeting not found",
"errors": []
}

Every endpoint should follow a consistent structure.

---

## Error Handling

Never expose internal exceptions.

Use:

- Global exception handlers
- Structured error responses
- Meaningful messages

Log internal details.

Return safe responses.

---

## Database Guidelines

Prefer normalized relational design.

Core tables:

- workspaces
- clients
- projects
- meetings
- meeting_chunks
- insights
- approval_queue

Future tables:

- github_integrations
- github_issues
- timeline_events

---

## Avoid Unnecessary Indirection

When modifying or generating code, prefer simplicity over abstraction.

### Remove Pass-Through Functions

Do not create or keep functions that only:

- Call another function and immediately return the result.
- Forward parameters without adding logic.
- Wrap a single line of code without providing value.
- Exist solely to move logic into another file.

Example of what to avoid:

```python
async def get_projects():
    return await project_service.get_projects()
```

when the route can directly call:

```python
await project_service.get_projects()
```

### Keep Abstractions Only When They Provide Value

Retain a separate function, service, helper, or module only if it provides one or more of the following:

- Business logic
- Validation
- Authorization
- Error handling
- Data transformation
- External API integration
- Shared reusable behavior
- Meaningful domain separation

### Refactoring Rules

When editing existing code:

1. Identify pass-through functions and inline them into the caller.
2. Remove unnecessary helper layers.
3. Reduce file hopping and indirection.
4. Preserve existing functionality and API behavior.
5. Prefer direct implementation when logic is simple and used only once.
6. Do not introduce abstractions preemptively for hypothetical future use cases.

### Decision Rule

Before creating a new function, ask:

> Does this function provide meaningful logic or reuse?

If the answer is no, implement the logic directly at the call site.

Optimize for maintainability, readability, and developer productivity rather than architectural purity.

---

## AI Guidelines

Agents should return structured outputs.

Prefer:

{
"requirements": [],
"decisions": [],
"risks": []
}

Avoid free-form text whenever data will be persisted.
No need to add API_VERSION

---

## Logging

Log:

- Errors
- External API failures
- Critical workflow events

Avoid excessive logging.

---

## Naming Conventions

Controllers:

meeting_controller.py

Services:

meeting_service.py

Repositories:

meeting_repository.py

Schemas:

meeting_schema.py

Models:

meeting_model.py

Agents:

meeting_agent.py

Tools:

github_tool.py

---

## Code Quality

- Type hints everywhere.
- Small focused functions.
- Async where beneficial, all the db operations need to be async.
- Single responsibility principle.
- Consistent naming.
- Remove dead code immediately.
- Use Pydantic wherever required, don't miss it anyhow.

##

Ship fast.
Refactor only when necessary.

## STRICT NOTE:

Don't run migrations yourself or create migration file on your own. The user will manually run all the migrations and upgrade head command.
