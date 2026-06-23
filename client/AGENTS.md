# Client Development Guidelines

## Tech Stack

- Next.js (App Router)
- TypeScript
- Tailwind CSS
- shadcn/ui
- React Hooks

---

## Core Principles

### DRY (Don't Repeat Yourself)

- Reusable logic belongs in hooks.
- Reusable UI belongs in components.
- Avoid duplicating API calls, validation logic, or state management.
- Create abstractions only when duplication appears multiple times.

### Simplicity First

- Build for current requirements.
- Avoid premature abstractions.
- Avoid unnecessary wrapper components.
- Avoid complex state management unless genuinely needed.

### Modular Architecture

Every feature should remain isolated and self-contained.

Example:

src/features/meetings

- components
- hooks
- services
- types
- utils

Keep feature-specific code inside its feature folder whenever possible.

---

## Folder Responsibilities

### app/

Contains:

- Pages
- Layouts
- Route groups
- Server Components

Rules:

- Keep business logic outside pages.
- Pages should compose features and components.
- Avoid large page files.

---

### components/

Contains shared reusable UI components.

Examples:

- Navbar
- Sidebar
- Dialogs
- Tables
- Empty States
- Loaders

Rules:

- Must remain presentation focused.
- No API logic.
- No business logic.

---

### features/

Contains feature modules.

Examples:

- workspace
- projects
- meetings
- approval-queue

Each feature may contain:

- components
- hooks
- services
- types
- utils

Features should be independent whenever possible.

---

### hooks/

Contains reusable custom hooks.

Examples:

- useProjects
- useMeetings
- useDebounce
- useLocalStorage

Rules:

- Business logic belongs here.
- Data fetching logic belongs here.
- Avoid writing large logic blocks inside components.

---

### lib/

Contains:

- API client
- constants
- utility functions
- configuration

Examples:

- axios client
- query client
- environment helpers

---

## UI Guidelines

### Responsive Design

All screens must support:

- Mobile
- Tablet
- Desktop

Always build mobile-first.

Avoid fixed widths.

Use responsive utility classes consistently.

---

### Clean and Functional UI

Focus on:

- Clarity
- Readability
- Accessibility
- Performance

Avoid excessive animations.

Avoid visual clutter.

Prioritize functionality over decoration.

---

### Color Management

Never hardcode colors.

Bad:

bg-blue-500
text-red-500

Good:

bg-primary
text-primary
border-border

All colors must originate from:

globals.css

Color system should be controlled from a single source.

---

### Typography

Maintain a consistent typography scale.

Use semantic headings:

- h1
- h2
- h3

Avoid arbitrary font sizes.

---

## Data Fetching

Centralize API calls.

Preferred structure:

features/meetings/services

Rules:

- Do not call APIs directly inside components.
- Components consume hooks.
- Hooks consume services.

Flow:

Component
→ Hook
→ Service
→ API

---

## Naming Conventions

Components:

ProjectCard.tsx

Hooks:

useProjects.ts

Types:

project.types.ts

Utilities:

project.utils.ts

Services:

project.service.ts

---

## Code Quality

- TypeScript strict mode.
- Avoid any.
- Prefer interfaces for API contracts.
- Keep functions small and focused.
- One responsibility per function.
- Remove dead code immediately.

---

## Performance

- Prefer Server Components by default.
- Use Client Components only when needed.
- Lazy load heavy components.
- Minimize unnecessary re-renders.

---

##

Focus on shipping features quickly while maintaining clean architecture.
