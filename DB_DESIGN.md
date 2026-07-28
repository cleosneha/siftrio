# Siftrio Database Design

## Technology Stack

| Component | Technology |
|---|---|
| Database | PostgreSQL 17 |
| ORM | SQLAlchemy 2.0+ (async, mapped-column) |
| Driver | asyncpg |
| Migrations | Alembic |
| Vector Search | pgvector (HNSW, cosine distance) |
| Embeddings | Mistral AI mistral-embed (1024 dimensions) |
| Container | Docker (pgvector/pgvector:pg17) |

---

## Schema Overview (21 Tables)

```
users
├── workspaces (created_by)
│   ├── workspace_members
│   ├── workspace_integrations
│   └── external_users
├── clients (created_by)
│   ├── client_members
│   └── projects (client_id)
│       ├── project_members
│       ├── project_integrations
│       ├── requirements
│       ├── action_items
│       ├── decisions
│       ├── risks
│       └── questions
├── meetings (created_by, client_id, project_id)
│   ├── meeting_chunks (embedding vector)
│   ├── meeting_analysis (1:1)
│   └── meeting_suggestions
├── user_integrations
├── member_invitations
└── api_keys

entity_integrations (polymorphic: entity_type + entity_id)
```

---

## Table Definitions

### users

| Column | Type | Constraints |
|---|---|---|
| id | UUID | PK |
| email | VARCHAR(255) | UNIQUE, NOT NULL, indexed |
| full_name | VARCHAR(255) | nullable |
| profile_picture | TEXT | nullable |
| google_id | VARCHAR(255) | UNIQUE, nullable |
| last_login_at | TIMESTAMPTZ | nullable |
| created_at | TIMESTAMPTZ | NOT NULL, server_default now() |
| updated_at | TIMESTAMPTZ | NOT NULL, server_default now() |

### workspaces

| Column | Type | Constraints |
|---|---|---|
| id | UUID | PK |
| created_by | UUID | FK -> users.id (SET NULL), nullable, indexed |
| name | VARCHAR(255) | NOT NULL, indexed |
| description | TEXT | nullable |
| created_at | TIMESTAMPTZ | NOT NULL |
| updated_at | TIMESTAMPTZ | NOT NULL |

### workspace_members

| Column | Type | Constraints |
|---|---|---|
| id | UUID | PK |
| workspace_id | UUID | FK -> workspaces.id (CASCADE), NOT NULL, indexed |
| user_id | UUID | FK -> users.id (CASCADE), NOT NULL, indexed |
| role | ENUM(owner, member) | NOT NULL, default MEMBER |
| created_at / updated_at | TIMESTAMPTZ | NOT NULL |
| **Unique** | `(workspace_id, user_id)` | |

### workspace_integrations

| Column | Type | Constraints |
|---|---|---|
| id | UUID | PK |
| workspace_id | UUID | FK -> workspaces.id (CASCADE), NOT NULL |
| provider | VARCHAR(50) | NOT NULL |
| access_token | TEXT | NOT NULL |
| refresh_token | TEXT | nullable |
| token_expires_at | TIMESTAMPTZ | nullable |
| config | JSONB | nullable |
| connected_by | UUID | FK -> users.id (SET NULL), nullable |
| connected_at | TIMESTAMPTZ | nullable |
| created_at / updated_at | TIMESTAMPTZ | NOT NULL |
| **Unique** | `(workspace_id, provider)` | |

### clients

| Column | Type | Constraints |
|---|---|---|
| id | UUID | PK |
| created_by | UUID | FK -> users.id (SET NULL), nullable, indexed |
| workspace_id | UUID | FK -> workspaces.id (CASCADE), NOT NULL, indexed |
| name | VARCHAR(255) | NOT NULL, indexed |
| description | TEXT | nullable |
| created_at / updated_at | TIMESTAMPTZ | NOT NULL |

### client_members

| Column | Type | Constraints |
|---|---|---|
| id | UUID | PK |
| client_id | UUID | FK -> clients.id (CASCADE), NOT NULL, indexed |
| user_id | UUID | FK -> users.id (CASCADE), NOT NULL, indexed |
| role | ENUM(owner, member) | NOT NULL, default MEMBER |
| created_at / updated_at | TIMESTAMPTZ | NOT NULL |
| **Unique** | `(client_id, user_id)` | |

### projects

| Column | Type | Constraints |
|---|---|---|
| id | UUID | PK |
| created_by | UUID | FK -> users.id (SET NULL), nullable, indexed |
| client_id | UUID | FK -> clients.id (CASCADE), NOT NULL, indexed |
| name | VARCHAR(255) | NOT NULL, indexed |
| description | TEXT | nullable |
| status | ENUM(active, completed, archived) | NOT NULL, default ACTIVE |
| created_at / updated_at | TIMESTAMPTZ | NOT NULL |

### project_members

| Column | Type | Constraints |
|---|---|---|
| id | UUID | PK |
| project_id | UUID | FK -> projects.id (CASCADE), NOT NULL, indexed |
| user_id | UUID | FK -> users.id (CASCADE), NOT NULL, indexed |
| role | ENUM(owner, member) | NOT NULL, default MEMBER |
| created_at / updated_at | TIMESTAMPTZ | NOT NULL |
| **Unique** | `(project_id, user_id)` | |

### project_integrations

| Column | Type | Constraints |
|---|---|---|
| id | UUID | PK |
| project_id | UUID | FK -> projects.id (CASCADE), NOT NULL |
| provider | VARCHAR(50) | NOT NULL |
| external_project_id | VARCHAR(255) | NOT NULL |
| external_project_key | VARCHAR(50) | nullable |
| external_project_name | VARCHAR(255) | nullable |
| config | JSONB | nullable |
| created_at / updated_at | TIMESTAMPTZ | NOT NULL |
| **Unique** | `(project_id, provider)` | |

### meetings

| Column | Type | Constraints |
|---|---|---|
| id | UUID | PK |
| created_by | UUID | FK -> users.id (SET NULL), nullable, indexed |
| client_id | UUID | FK -> clients.id (CASCADE), NOT NULL, indexed |
| project_id | UUID | FK -> projects.id (SET NULL), nullable, indexed |
| title | VARCHAR(255) | NOT NULL |
| meeting_type | ENUM(project, miscellaneous) | NOT NULL, default PROJECT |
| tags | ARRAY(TEXT) | NOT NULL, default [] |
| transcript | TEXT | nullable |
| meeting_date | TIMESTAMPTZ | nullable, indexed |
| start_time | TIMESTAMPTZ | nullable |
| end_time | TIMESTAMPTZ | nullable |
| meeting_provider | ENUM(manual, google_meet) | NOT NULL, default MANUAL |
| meeting_url | TEXT | nullable |
| google_calendar_event_id | VARCHAR(255) | nullable, indexed |
| google_meet_url | TEXT | nullable |
| google_meet_code | VARCHAR(255) | nullable, indexed |
| fireflies_meeting_id | VARCHAR(255) | nullable, indexed |
| transcript_status | ENUM(pending, processing, completed, failed) | nullable |
| guest_emails | ARRAY(TEXT) | nullable |
| created_at / updated_at | TIMESTAMPTZ | NOT NULL |

### meeting_chunks

| Column | Type | Constraints |
|---|---|---|
| id | UUID | PK |
| meeting_id | UUID | FK -> meetings.id (CASCADE), NOT NULL, indexed |
| chunk_index | INTEGER | NOT NULL |
| chunk_text | TEXT | NOT NULL |
| embedding | VECTOR(1024) | NOT NULL |
| chunk_metadata | JSONB | nullable |
| created_at / updated_at | TIMESTAMPTZ | NOT NULL |
| **Unique** | `(meeting_id, chunk_index)` | |
| **HNSW Index** | `idx_chunk_embedding_hnsw` | m=16, ef_construction=200, vector_cosine_ops |

### meeting_analysis

| Column | Type | Constraints |
|---|---|---|
| id | UUID | PK |
| meeting_id | UUID | FK -> meetings.id (CASCADE), UNIQUE, NOT NULL |
| summary | TEXT | nullable |
| goal | TEXT | nullable |
| outcomes | JSONB | NOT NULL, default [] |
| blockers | JSONB | NOT NULL, default [] |
| confidence | FLOAT | nullable |
| raw_ai_response | JSONB | nullable |
| created_at / updated_at | TIMESTAMPTZ | NOT NULL |

### meeting_suggestions

| Column | Type | Constraints |
|---|---|---|
| id | UUID | PK |
| meeting_id | UUID | FK -> meetings.id (CASCADE), NOT NULL, indexed |
| title | VARCHAR(255) | NOT NULL |
| description | TEXT | nullable |
| suggested_date | DATE | nullable |
| start_time | TIME | nullable |
| end_time | TIME | nullable |
| confidence | FLOAT | NOT NULL, default 0.0 |
| reason | TEXT | NOT NULL |
| status | ENUM(pending, scheduled, dismissed) | NOT NULL, default PENDING |
| created_at / updated_at | TIMESTAMPTZ | NOT NULL |
| **Indexes** | `idx_suggestion_meeting_id`, `idx_suggestion_status` | |

### user_integrations

| Column | Type | Constraints |
|---|---|---|
| id | UUID | PK |
| user_id | UUID | FK -> users.id (CASCADE), NOT NULL, indexed |
| provider | VARCHAR(50) | NOT NULL |
| access_token | TEXT | NOT NULL |
| refresh_token | TEXT | nullable |
| token_expires_at | TIMESTAMPTZ | nullable |
| scopes | TEXT | nullable |
| created_at / updated_at | TIMESTAMPTZ | NOT NULL |
| **Unique** | `(user_id, provider)` | |

### external_users

| Column | Type | Constraints |
|---|---|---|
| id | UUID | PK |
| external_id | VARCHAR(255) | NOT NULL |
| provider | VARCHAR(50) | NOT NULL |
| display_name | VARCHAR(255) | nullable |
| email_address | VARCHAR(255) | nullable |
| workspace_id | UUID | FK -> workspaces.id (CASCADE), NOT NULL |
| last_refreshed_at | TIMESTAMPTZ | NOT NULL |
| created_at / updated_at | TIMESTAMPTZ | NOT NULL |
| **Unique** | `(workspace_id, provider, external_id)` | |

### entity_integrations

| Column | Type | Constraints |
|---|---|---|
| id | UUID | PK |
| entity_type | VARCHAR(50) | NOT NULL |
| entity_id | UUID | NOT NULL (no FK) |
| provider | VARCHAR(50) | NOT NULL |
| external_id | VARCHAR(255) | nullable |
| external_key | VARCHAR(50) | nullable |
| external_url | TEXT | nullable |
| external_type | VARCHAR(50) | nullable |
| sync_status | ENUM(pending, synced, failed, conflict) | nullable |
| synced_at | TIMESTAMPTZ | nullable |
| external_assignee_id | VARCHAR(255) | nullable |
| metadata | JSONB | nullable |
| created_at / updated_at | TIMESTAMPTZ | NOT NULL |
| **Unique** | `(entity_type, entity_id, provider)` | |
| **Index** | `idx_entity_integration_entity` | `(entity_type, entity_id)` |

### requirements

| Column | Type | Constraints |
|---|---|---|
| id | UUID | PK |
| project_id | UUID | FK -> projects.id (CASCADE), NOT NULL, indexed |
| meeting_id | UUID | FK -> meetings.id (CASCADE), NOT NULL, indexed |
| source_chunk_id | UUID | FK -> meeting_chunks.id (SET NULL), nullable |
| title | VARCHAR(255) | NOT NULL |
| description | TEXT | nullable |
| status | ENUM(proposed, approved, implemented, rejected) | NOT NULL, default PROPOSED, indexed |
| priority | ENUM(low, medium, high, critical) | nullable, indexed |
| approved_by | UUID | FK -> users.id (SET NULL), nullable |
| approved_at | TIMESTAMPTZ | nullable |
| created_at / updated_at | TIMESTAMPTZ | NOT NULL |
| **Composite Indexes** | `(project_id, status)`, `(meeting_id, status)` | |

### action_items

| Column | Type | Constraints |
|---|---|---|
| id | UUID | PK |
| project_id | UUID | FK -> projects.id (CASCADE), NOT NULL, indexed |
| meeting_id | UUID | FK -> meetings.id (CASCADE), NOT NULL, indexed |
| source_chunk_id | UUID | FK -> meeting_chunks.id (SET NULL), nullable |
| title | VARCHAR(255) | NOT NULL |
| description | TEXT | nullable |
| status | ENUM(todo, in_progress, blocked, done) | NOT NULL, default TODO, indexed |
| assignee_id | UUID | FK -> users.id (SET NULL), nullable, indexed |
| assignee_name | VARCHAR(255) | nullable |
| priority | ENUM(low, medium, high, critical) | nullable |
| due_date | TIMESTAMPTZ | nullable, indexed |
| created_at / updated_at | TIMESTAMPTZ | NOT NULL |
| **Composite Indexes** | `(project_id, status)`, `(meeting_id, status)` | |

### decisions

| Column | Type | Constraints |
|---|---|---|
| id | UUID | PK |
| project_id | UUID | FK -> projects.id (CASCADE), NOT NULL, indexed |
| meeting_id | UUID | FK -> meetings.id (CASCADE), NOT NULL, indexed |
| source_chunk_id | UUID | FK -> meeting_chunks.id (SET NULL), nullable |
| title | VARCHAR(255) | NOT NULL |
| description | TEXT | nullable |
| status | ENUM(proposed, accepted, rejected) | NOT NULL, default PROPOSED, indexed |
| decision_date | TIMESTAMPTZ | nullable |
| created_at / updated_at | TIMESTAMPTZ | NOT NULL |
| **Composite Indexes** | `(project_id, status)`, `(meeting_id, status)` | |

### risks

| Column | Type | Constraints |
|---|---|---|
| id | UUID | PK |
| project_id | UUID | FK -> projects.id (CASCADE), NOT NULL, indexed |
| meeting_id | UUID | FK -> meetings.id (CASCADE), NOT NULL, indexed |
| source_chunk_id | UUID | FK -> meeting_chunks.id (SET NULL), nullable |
| title | VARCHAR(255) | NOT NULL |
| description | TEXT | nullable |
| status | ENUM(open, mitigated, closed, accepted) | NOT NULL, default OPEN, indexed |
| severity | ENUM(low, medium, high, critical) | nullable, indexed |
| mitigation | TEXT | nullable |
| created_at / updated_at | TIMESTAMPTZ | NOT NULL |
| **Composite Indexes** | `(project_id, status)`, `(meeting_id, status)` | |

### questions

| Column | Type | Constraints |
|---|---|---|
| id | UUID | PK |
| project_id | UUID | FK -> projects.id (CASCADE), NOT NULL, indexed |
| meeting_id | UUID | FK -> meetings.id (CASCADE), NOT NULL, indexed |
| source_chunk_id | UUID | FK -> meeting_chunks.id (SET NULL), nullable |
| title | VARCHAR(255) | NOT NULL |
| description | TEXT | nullable |
| status | ENUM(open, answered, closed) | NOT NULL, default OPEN, indexed |
| answer | TEXT | nullable |
| created_at / updated_at | TIMESTAMPTZ | NOT NULL |
| **Composite Indexes** | `(project_id, status)`, `(meeting_id, status)` | |

### member_invitations

| Column | Type | Constraints |
|---|---|---|
| id | UUID | PK |
| email | VARCHAR(255) | NOT NULL, indexed |
| user_id | UUID | FK -> users.id (SET NULL), nullable |
| resource_type | ENUM(workspace, client, project) | NOT NULL |
| resource_id | UUID | NOT NULL (no FK) |
| invited_by | UUID | FK -> users.id (SET NULL), nullable |
| token | VARCHAR(255) | UNIQUE, NOT NULL, indexed |
| status | ENUM(pending, accepted, expired, revoked) | NOT NULL, default PENDING |
| expires_at | TIMESTAMPTZ | NOT NULL |
| accepted_at | TIMESTAMPTZ | nullable |
| created_at / updated_at | TIMESTAMPTZ | NOT NULL |
| **Unique** | `(email, resource_type, resource_id)` | |
| **Index** | `idx_invitation_email_resource` | `(email, resource_type, resource_id)` |

### api_keys

| Column | Type | Constraints |
|---|---|---|
| id | UUID | PK |
| user_id | UUID | FK -> users.id (CASCADE), NOT NULL, indexed |
| name | VARCHAR(255) | NOT NULL |
| key_prefix | VARCHAR(16) | NOT NULL |
| hashed_secret | VARCHAR(255) | UNIQUE, NOT NULL |
| last_used_at | TIMESTAMPTZ | nullable |
| revoked_at | TIMESTAMPTZ | nullable |
| created_at / updated_at | TIMESTAMPTZ | NOT NULL |

---

## Indexes Summary

| Table | Index | Columns | Type |
|---|---|---|---|
| users | users_email_idx | email | B-tree (unique) |
| users | users_google_id_idx | google_id | B-tree (unique) |
| workspaces | workspaces_name_idx | name | B-tree |
| workspaces | fk_workspaces_created_by | created_by | B-tree |
| workspace_members | uq_workspace_member_user | workspace_id, user_id | Unique |
| workspace_integrations | uq_workspace_integration | workspace_id, provider | Unique |
| clients | clients_name_idx | name | B-tree |
| clients | idx_client_workspace_id | workspace_id | B-tree |
| client_members | uq_client_member_user | client_id, user_id | Unique |
| projects | projects_name_idx | name | B-tree |
| projects | idx_project_client_id | client_id | B-tree |
| project_members | uq_project_member_user | project_id, user_id | Unique |
| project_integrations | uq_project_integration | project_id, provider | Unique |
| meetings | idx_meeting_client_id | client_id | B-tree |
| meetings | idx_meeting_project_id | project_id | B-tree |
| meetings | idx_meeting_meeting_date | meeting_date | B-tree |
| meetings | idx_meeting_google_calendar_event_id | google_calendar_event_id | B-tree |
| meetings | idx_meeting_google_meet_code | google_meet_code | B-tree |
| meetings | idx_meeting_fireflies_meeting_id | fireflies_meeting_id | B-tree |
| meeting_chunks | uq_chunk_meeting_index | meeting_id, chunk_index | Unique |
| meeting_chunks | idx_chunk_embedding_hnsw | embedding | HNSW (vector_cosine_ops) |
| meeting_analysis | meeting_analysis_meeting_id_idx | meeting_id | B-tree (unique) |
| meeting_suggestions | idx_suggestion_meeting_id | meeting_id | B-tree |
| meeting_suggestions | idx_suggestion_status | status | B-tree |
| meeting_suggestions | idx_suggestion_suggested_date | suggested_date | B-tree |
| user_integrations | uq_user_integration_user_provider | user_id, provider | Unique |
| external_users | uq_external_user | workspace_id, provider, external_id | Unique |
| external_users | idx_external_user_workspace_id | workspace_id | B-tree |
| workspace_integrations | idx_workspace_integration_workspace_id | workspace_id | B-tree |
| project_integrations | idx_project_integration_project_id | project_id | B-tree |
| entity_integrations | uq_entity_integration | entity_type, entity_id, provider | Unique |
| entity_integrations | idx_entity_integration_entity | entity_type, entity_id | B-tree |
| requirements | idx_requirement_project_status | project_id, status | Composite |
| requirements | idx_requirement_meeting_status | meeting_id, status | Composite |
| action_items | idx_action_item_project_status | project_id, status | Composite |
| action_items | idx_action_item_meeting_status | meeting_id, status | Composite |
| decisions | idx_decision_project_status | project_id, status | Composite |
| decisions | idx_decision_meeting_status | meeting_id, status | Composite |
| risks | idx_risk_project_status | project_id, status | Composite |
| risks | idx_risk_meeting_status | meeting_id, status | Composite |
| questions | idx_question_project_status | project_id, status | Composite |
| questions | idx_question_meeting_status | meeting_id, status | Composite |
| member_invitations | uq_invitation_email_resource | email, resource_type, resource_id | Unique |
| api_keys | api_keys_hashed_secret_idx | hashed_secret | B-tree (unique) |
| api_keys | idx_api_keys_active | user_id WHERE revoked_at IS NULL | Partial B-tree |

---

## Relationships

```
User
 ├── 1:N Workspace (created_by)
 ├── 1:N Client (created_by)
 ├── 1:N Project (created_by)
 ├── 1:N Meeting (created_by)
 ├── 1:N WorkspaceMember
 ├── 1:N ClientMember
 ├── 1:N ProjectMember
 ├── 1:N UserIntegration
 ├── 1:N MemberInvitation (invited_by)
 └── 1:N ApiKey

Workspace
 ├── 1:N Client
 ├── 1:N WorkspaceMember
 ├── 1:N WorkspaceIntegration
 └── 1:N ExternalUser

Client
 ├── N:1 Workspace
 ├── 1:N Project
 ├── 1:N Meeting
 └── 1:N ClientMember

Project
 ├── N:1 Client
 ├── 1:N Meeting
 ├── 1:N ProjectMember
 └── 1:N ProjectIntegration

Meeting
 ├── N:1 Client
 ├── N:1 Project (optional)
 ├── 1:1 MeetingAnalysis
 ├── 1:N MeetingChunk
 └── 1:N MeetingSuggestion

MeetingChunk
 └── Referenced by: requirements, action_items, decisions, risks, questions (source_chunk_id)

Knowledge Entities (requirements, action_items, decisions, risks, questions)
 ├── N:1 Project
 ├── N:1 Meeting
 ├── N:1 MeetingChunk (optional)
 └── requirements: N:1 User (approved_by)
```

---

## Migration History

| Revision | Date | Description |
|---|---|---|
| `854f803a7e40` | 2026-07-23 | Initial schema: all 21 tables, indexes, HNSW vector index |
| `3c6687066a97` | 2026-07-23 | P1-P3: composite indexes on knowledge entities, NOT NULL on created_by, unique constraints |
| `7a98f4c2954c` | 2026-07-23 | Refinements: revert created_by to nullable, fix external_users/invitation unique constraints |

---

## Deletion Strategy

### Principle

> Resources with active members are NEVER deleted as a side effect of user deletion. Only truly orphaned resources (zero remaining members) are cleaned up.

### ON DELETE Behavior (PostgreSQL FK Constraints)

| Table | Column | FK Target | ON DELETE |
|---|---|---|---|
| workspaces | created_by | users.id | **SET NULL** |
| clients | created_by | users.id | **SET NULL** |
| projects | created_by | users.id | **SET NULL** |
| meetings | created_by | users.id | **SET NULL** |
| meetings | client_id | clients.id | CASCADE |
| meetings | project_id | projects.id | SET NULL |
| workspace_members | workspace_id | workspaces.id | CASCADE |
| workspace_members | user_id | users.id | CASCADE |
| client_members | client_id | clients.id | CASCADE |
| client_members | user_id | users.id | CASCADE |
| project_members | project_id | projects.id | CASCADE |
| project_members | user_id | users.id | CASCADE |
| knowledge_entities | project_id | projects.id | CASCADE |
| knowledge_entities | meeting_id | meetings.id | CASCADE |
| meeting_chunks | meeting_id | meetings.id | CASCADE |
| meeting_analysis | meeting_id | meetings.id | CASCADE |
| meeting_suggestions | meeting_id | meetings.id | CASCADE |
| api_keys | user_id | users.id | CASCADE |
| user_integrations | user_id | users.id | CASCADE |
| workspace_integrations | workspace_id | workspaces.id | CASCADE |
| project_integrations | project_id | projects.id | CASCADE |
| external_users | workspace_id | workspaces.id | CASCADE |

### Deletion Scenarios

#### User Deletion Flow

```
1. QUERY: Find sole-member workspaces (user is the ONLY member)
   → Delete these workspaces (cascade cleans clients, projects, meetings, etc.)

2. QUERY: Find sole-member clients NOT in already-deleted workspaces
   → Delete these clients (cascade cleans projects, meetings)

3. QUERY: Find sole-member projects NOT in already-deleted clients
   → Delete these projects (meetings become project_id=NULL orphans)

4. DELETE user record:
   - created_by FKs → SET NULL (workspaces/clients/projects/meetings survive)
   - workspace_members → CASCADE (user's memberships removed)
   - client_members → CASCADE
   - project_members → CASCADE
   - api_keys → CASCADE
   - user_integrations → CASCADE
   - sent_invitations → CASCADE
```

#### Workspace Deletion

| Scenario | Behavior |
|---|---|
| Delete workspace | Everything cascades: clients → projects → knowledge entities, meetings (via client_id CASCADE), members, integrations, external_users |

#### Client Deletion

| Scenario | Behavior |
|---|---|
| Delete client | Projects cascade (knowledge entities cascade, integrations cascade). Members cascade. Meetings cascade via client_id CASCADE. |

#### Project Deletion

| Scenario | Behavior |
|---|---|
| Delete project | Knowledge entities cascade (FK project_id CASCADE). Members cascade. Integrations cascade. Meetings become orphans (project_id → NULL). |

#### Member Removal

| Scenario | Behavior |
|---|---|
| Remove last member from workspace | Workspace is deleted (cascade everything) |
| Remove last member from client | Client is deleted (cascade projects, meetings via CASCADE) |
| Remove last member from project | Project is deleted (knowledge entities cascade, meetings become orphans) |
| Remove non-last member | Only membership row removed |

### Implementation Files

| File | Purpose |
|---|---|
| `src/services/user_deletion_service.py` | Orchestrates user deletion with sole-member checks |
| `src/services/membership_service.py` | Handles member removal with last-member deletion |
| `src/repositories/workspace_member_repository.py` | `count_by_workspace()`, `list_workspace_ids_by_user()` |
| `src/repositories/client_member_repository.py` | `count_by_client()`, `list_client_ids_by_user()` |
| `src/repositories/project_member_repository.py` | `count_by_project()`, `list_project_ids_by_user()` |
| `src/models/user.py` | No cascade on created_* relationships |
| `src/models/workspace.py` | FK users.id SET NULL |
| `src/models/client.py` | FK users.id SET NULL |
| `src/models/project.py` | FK users.id SET NULL |
| `src/models/meeting.py` | FK users.id SET NULL |

---

## Deep Review

### CRITICAL Issues

#### C1. Duplicate Indexes on FK Columns

`meeting_chunks.meeting_id` has both `index=True` on the column AND `Index("idx_chunk_meeting_id", "meeting_id")` in `__table_args__`. This creates two separate B-tree indexes on the same column, wasting disk space and slowing writes.

**Affected tables**: `meeting_chunks`, `meeting_suggestions`, and potentially others where `index=True` on a FK column AND an explicit index is defined in `__table_args__`.

**Fix**: Remove `index=True` from FK columns that already have an explicit index in `__table_args__`, or remove the explicit index if the auto-generated one suffices. Pick one approach consistently.

#### C2. Dangerous CASCADE Chain on User Delete [FIXED]

`User.created_workspaces` had `cascade="all, delete-orphan"`. A single user deletion could destroy an entire organization's data including other members' workspaces.

**Changes made:**
1. Removed `cascade="all, delete-orphan"` from `User.created_workspaces`, `User.created_clients`, `User.created_projects`, `User.created_meetings`
2. Changed FK `ON DELETE` from `CASCADE` to `SET NULL` on `created_by` columns in `workspaces`, `clients`, `projects`, `meetings`
3. Created `UserDeletionService` (`src/services/user_deletion_service.py`) that:
   - Queries sole-member workspaces/clients/projects BEFORE deletion
   - Deletes only orphaned resources (zero remaining members)
   - Preserves shared resources (transfers ownership implicitly by leaving memberships intact)
4. Updated `MembershipService` to delete resources when the last member is removed

**See [Deletion Strategy](#deletion-strategy) section below for full details.**

#### C3. Polymorphic FK Without Validation [FIXED]

`entity_integrations.entity_type` and `member_invitations.resource_type` are VARCHAR/ENUM columns that implicitly reference different tables via `entity_id`/`resource_id`, but there are:
- No FK constraints (impossible with polymorphic, but still a risk)
- No CHECK constraints to validate allowed values
- No application-level guarantee that the referenced row exists

**Changes made:** Added `CheckConstraint("entity_type IN ('action_item', 'requirement', 'decision', 'risk', 'question')")` to `entity_integrations` model.

#### C4. `action_items.assignee` is a VARCHAR, Not a FK [FIXED]

`assignee` stores a free-text name string. No referential integrity. If a user changes their name, all their assigned action items become stale. Cannot query "all action items assigned to user X" reliably.

**Changes made:** Replaced `assignee VARCHAR(255)` with `assignee_id UUID FK -> users.id (SET NULL)` for internal users and `assignee_name VARCHAR(255)` for display/external assignees. Updated `knowledge_repository.py`, `knowledge_service.py`, `action_item_jira_service.py`, and `knowledge_schema.py`.

---

### HIGH Issues

#### H1. Missing Indexes on FK Columns [FIXED]

These FK columns lacked indexes, causing slow JOIN/WHERE queries:

| Table | Column | Issue |
|---|---|---|
| `external_users` | `workspace_id` | No index at all |
| `workspace_integrations` | `workspace_id` | No index at all |
| `project_integrations` | `project_id` | No index at all |

**Changes made:** Added `index=True` to `workspace_id` on `external_users` and `workspace_integrations`, and `project_id` on `project_integrations`.

#### H2. Provider-Specific Columns on `meetings`

`google_calendar_event_id`, `google_meet_url`, `google_meet_code`, `fireflies_meeting_id` are Google/Fireflies-specific columns on the core meetings table. Every new provider adds more columns. The table already has 20 columns.

**Fix**: Move provider-specific data to `entity_integrations` (already exists for this purpose) or a dedicated `meeting_external_data` table. Keep `meeting_provider` and `meeting_url` on the core table, move the rest.

#### H3. Inconsistent ENUM vs VARCHAR for `priority` [FIXED]

`requirements.priority` and `action_items.priority` were `VARCHAR(50)` but `risks.severity` uses a proper `ENUM`. Free-text priority meant inconsistent data ("high", "High", "HIGH", "P1" all coexist).

**Changes made:** Created shared `Priority` enum in `src/models/base.py`. Updated `requirements.priority` and `action_items.priority` to use `ENUM(Priority)`.

#### H4. `sync_status` on `entity_integrations` is VARCHAR(20) [FIXED]

No validation on allowed values. Could store anything.

**Changes made:** Created `SyncStatus` enum in `src/models/base.py`. Updated `entity_integrations.sync_status` to use `ENUM(SyncStatus)`.

#### H5. No Soft-Delete on Critical Tables

Only `api_keys` has `revoked_at`. All other tables use hard CASCADE deletes. Deleting a workspace permanently destroys all clients, projects, meetings, analysis, chunks, and knowledge entities. Recovery is impossible.

**Fix**: Add `deleted_at TIMESTAMPTZ` (nullable) to `workspaces`, `clients`, `projects`, `meetings`. Use application-level filtering (`WHERE deleted_at IS NULL`) instead of hard deletes. Consider partial indexes for performance.

---

### MEDIUM Issues

#### M1. `AIEntityBase` Doesn't Use Shared Mixins [FIXED]

`AIEntityBase` manually defined `id`, `created_at`, `updated_at` instead of using `UUIDMixin` and `TimestampMixin`.

**Changes made:** Made `AIEntityBase` inherit from `UUIDMixin` and `TimestampMixin`, removed duplicated columns.

#### M2. `entity_integrations.metadata` Column Name Conflict [FIXED]

The DB column was named `metadata` but the Python attribute was `extra_data`. This disconnect made queries confusing.

**Changes made:** Renamed DB column to `metadata` using `mapped_column("metadata", JSONB)`. Python attribute stays `extra_data` to avoid SQLAlchemy reserved name conflict.

#### M3. Missing Denormalized `workspace_id` on Knowledge Entities

To query "all requirements across a workspace", you must join: `requirements -> projects -> clients -> workspaces`. This is 3 JOINs for a common query pattern.

**Fix**: Add `workspace_id UUID FK -> workspaces.id` to `requirements`, `action_items`, `decisions`, `risks`, `questions`. Populate it from the project's client's workspace at write time.

#### M4. Missing `client_id` on Knowledge Entities

Same issue as M3. To filter knowledge entities by client, you must join through project.

**Fix**: Add `client_id UUID FK -> clients.id` to knowledge entity tables.

#### M5. Missing `workspace_id` on `meetings`

To get all meetings for a workspace, you must join `meetings -> clients -> workspaces`. Adding `workspace_id` enables direct workspace-scoped queries.

**Fix**: Add `workspace_id UUID FK -> workspaces.id` (SET NULL, indexed) to `meetings`.

#### M6. `MemberRole` Enum Defined in Wrong File [FIXED]

`MemberRole` was defined in `workspace_member.py` but imported by `client_member.py` and `project_member.py`. This created a circular-ish dependency.

**Changes made:** Moved `MemberRole` to `src/models/base.py`. Updated imports in all 7 files that referenced it.

#### M7. No CHECK Constraints for Temporal Validity

`meetings.start_time` and `meetings.end_time` have no constraint ensuring `start_time < end_time`. `member_invitations.expires_at` has no constraint ensuring it's in the future at creation.

**Fix**: Add CHECK constraints:
```sql
ALTER TABLE meetings ADD CONSTRAINT chk_meeting_time_order
  CHECK (start_time IS NULL OR end_time IS NULL OR start_time < end_time);
```

#### M8. `meeting.raw_ai_response` Unbounded JSONB

`meeting_analysis.raw_ai_response` stores the full AI response as JSONB with no size limit. Over time this could accumulate MBs per meeting.

**Fix**: Consider truncating or storing a reference to object storage instead. Or add a practical CHECK constraint on JSONB size.

#### M9. `ARRAY(Text)` for `tags` and `guest_emails`

PostgreSQL ARRAY types don't support foreign keys, are harder to query efficiently (any element match requires `ANY()`), and can't enforce uniqueness within the array.

**Fix**: If tags need to be queryable or shared, use a `meeting_tags` junction table. For `guest_emails`, a `meeting_guests` table with an FK to `external_users` would enable proper joins.

---

### LOW Issues

#### L1. Redundant Composite Index on `member_invitations` [FIXED]

`idx_invitation_email_resource(email, resource_type, resource_id)` and `uq_invitation_email_resource(email, resource_type, resource_id)` were on the same columns. The UNIQUE constraint already creates an index.

**Changes made:** Removed redundant `idx_invitation_email_resource` from model.

#### L2. `api_keys` Has No Active/Revoked Filter Index [FIXED]

Queries like "list all active API keys for user" must filter `WHERE revoked_at IS NULL`.

**Changes made:** Added partial index `idx_api_keys_active ON api_keys(user_id) WHERE revoked_at IS NULL`.

#### L3. No Index on `meeting_suggestions.suggested_date` [FIXED]

If the UI needs to show "upcoming suggestions", queries filtering on `suggested_date` will scan the full table.

**Changes made:** Added `Index("idx_suggestion_suggested_date", "suggested_date")`.

#### L4. `transcript` Column on `meetings` is Unbounded TEXT

Meeting transcripts can be very large (10K+ words). Storing in the main table increases row size and slows scans on non-transcript queries.

**Fix**: Move `transcript` to a separate `meeting_transcripts` table with 1:1 relationship. The main meetings table stays lean for list queries.

---

### SCALABILITY Considerations

#### S1. No Partitioning Strategy for `meeting_chunks`

`meeting_chunks` is the fastest-growing table (each meeting produces 10-50+ chunks with 1024-dimension vectors). At scale:
- 1000 meetings/day * 30 chunks = 30K rows/day * 1024 floats = ~100MB/day in vectors alone
- HNSW index grows proportionally

**Future consideration**: Partition by workspace_id or date range. pgvector supports HNSW on partitioned tables since PostgreSQL 12+.

#### S2. Connection Pool Configuration

Current: `pool_pre_ping=True`, `statement_cache_size=0`. No explicit pool size limits configured. For multi-tenant scale, consider:
- `pool_size` and `max_overflow` limits
- Connection timeout settings
- Read replica routing for read-heavy operations (vector search, FTS)

#### S3. Vector Search Performance

HNSW parameters `m=16, ef_construction=200` are reasonable for <1M vectors. At scale:
- Monitor recall vs speed tradeoff
- Consider `ef_search` tuning at query time
- Evaluate IVFFlat as alternative if data distribution changes

#### S4. No Materialized Views for Dashboard Queries

Workspace-level dashboards (total meetings, open action items, risks by severity) will require expensive aggregation queries. Consider materialized views refreshed on a schedule.

#### S5. JSONB Growth Without Archival

`meeting_analysis.raw_ai_response`, `entity_integrations.metadata`, `meeting_chunks.chunk_metadata` are JSONB columns that grow without bounds. No archival or compaction strategy exists.

**Future consideration**: Archive old meeting analysis raw responses to cold storage. Set practical JSONB size limits.

---

### Recommendations Summary

| Priority | ID | Issue | Effort |
|---|---|---|---|
| CRITICAL | C1 | Remove duplicate indexes on FK columns | **DONE** |
| CRITICAL | C2 | Fix dangerous CASCADE chain on user delete | **DONE** |
| CRITICAL | C3 | Add CHECK constraints on polymorphic type columns | **DONE** |
| CRITICAL | C4 | Change action_items.assignee from VARCHAR to FK | **DONE** |
| HIGH | H1 | Add missing FK indexes (external_users, integrations) | **DONE** |
| HIGH | H2 | Move provider-specific columns out of meetings | High |
| HIGH | H3 | Convert priority VARCHAR to shared ENUM | **DONE** |
| HIGH | H4 | Convert sync_status VARCHAR to ENUM | **DONE** |
| HIGH | H5 | Add soft-delete to core tables | Medium |
| MEDIUM | M1 | Make AIEntityBase use shared mixins | **DONE** |
| MEDIUM | M2 | Fix entity_integrations metadata naming | **DONE** |
| MEDIUM | M3 | Add workspace_id to knowledge entities | Medium |
| MEDIUM | M4 | Add client_id to knowledge entities | Medium |
| MEDIUM | M5 | Add workspace_id to meetings | Medium |
| MEDIUM | M6 | Move MemberRole to shared location | **DONE** |
| MEDIUM | M7 | Add temporal CHECK constraints | Low |
| MEDIUM | M8 | Bound raw_ai_response JSONB size | Low |
| MEDIUM | M9 | Replace ARRAY columns with junction tables | Medium |
| LOW | L1 | Remove redundant composite index on invitations | **DONE** |
| LOW | L2 | Add partial index for active API keys | **DONE** |
| LOW | L3 | Add index on meeting_suggestions.suggested_date | **DONE** |
| LOW | L4 | Move transcript to separate table | Medium |
