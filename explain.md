# Campus Event Management Platform - Detailed Explanation

## 1. Project Overview

### What is it?
A web-based application that allows a college/university to manage all aspects of campus events — from creating and scheduling events, managing venues, handling participant registrations, to generating summary reports. The system provides a clean web interface for both regular users (students, faculty) and administrators.

### Why did we build it?
Managing campus events manually (spreadsheets, emails, notice boards) is error-prone and inefficient. Events get double-booked, registrations overflow, and there's no centralized place to track what's happening on campus. This platform solves all of that with a proper database-backed web application.

### Core Problem Statement
Design and implement a system that can:
- Store and manage events with their schedules, venues, and organizer information
- Handle participant registrations with automatic waitlisting when events are full
- Detect and prevent venue scheduling conflicts
- Provide search and filtering capabilities
- Generate summary reports and analytics
- Expose a REST API for programmatic access

---

## 2. Architecture & Design

### High-Level Architecture

```
┌──────────────┐     HTTP      ┌──────────────┐     SQL      ┌──────────────┐
│   Browser    │ ◄──────────►  │  Flask App   │ ◄──────────► │   SQLite     │
│  (HTML/CSS/  │               │  (app.py)    │              │  (events.db) │
│   JavaScript)│               │              │              │              │
└──────────────┘               └──────────────┘              └──────────────┘
                                     │
                                     │ imports
                                     ▼
                               ┌──────────────┐
                               │ database.py  │
                               │ (Data Layer) │
                               └──────────────┘
```

### Design Pattern: MVC (Model-View-Controller)

We follow the MVC pattern, adapted for Flask:

- **Model** (`database.py`): Defines the database schema (4 tables), handles all SQL queries, and provides clean Python functions for CRUD operations. The rest of the app never writes raw SQL — it calls functions like `get_all_events()` or `register_participant()`.

- **View** (`templates/*.html`): Jinja2 HTML templates that render the user interface. They receive data from the controller and display it. Template inheritance (`base.html` → child templates) avoids repetition.

- **Controller** (`app.py`): Flask routes that handle HTTP requests. Each route function receives user input (URL params, form data), calls the appropriate database functions, and renders the right template with the results.

### Why Flask?
- Lightweight — doesn't force unnecessary abstractions
- Easy to understand the request/response flow
- Jinja2 templating is powerful yet simple
- Built-in development server for testing
- Good enough for our scale (campus-level, not millions of users)

### Why SQLite?
- Zero configuration — no need to install a database server
- Single file storage — easy to back up and distribute
- Full SQL support (joins, aggregations, foreign keys)
- Perfect for applications with moderate concurrent access
- Ships with Python's standard library

---

## 3. Database Design

### Entity-Relationship Model

```
┌─────────────┐       ┌──────────────┐       ┌───────────────┐
│   venues    │       │    events    │       │ participants  │
├─────────────┤       ├──────────────┤       ├───────────────┤
│ id (PK)     │◄──────│ venue_id(FK) │       │ id (PK)       │
│ name        │  1:N  │ id (PK)      │       │ name          │
│ location    │       │ title        │       │ email         │
│ capacity    │       │ description  │       │ phone         │
│ has_projector│      │ event_date   │       │ department    │
│ has_ac      │       │ start_time   │       │ role          │
└─────────────┘       │ end_time     │       └───────┬───────┘
                      │ organizer    │               │
                      │ category     │               │
                      │ max_participants│             │
                      │ created_at   │               │
                      └──────┬───────┘               │
                             │                       │
                             │    ┌───────────────┐  │
                             └────│ registrations │──┘
                              N:M ├───────────────┤
                                  │ id (PK)       │
                                  │ event_id (FK) │
                                  │ participant_id│
                                  │ registered_at │
                                  │ status        │
                                  └───────────────┘
```

### Table Details

**venues** (6 records seeded)
- Stores physical locations where events can be held
- `capacity` helps determine if a venue suits an event
- Boolean flags for amenities (projector, AC)

**events** (8 records seeded)
- Central table — each row is one event
- `venue_id` is a foreign key linking to the venues table
- `category` enables filtering (technical, cultural, workshop, etc.)
- `max_participants` controls when waitlisting kicks in

**participants** (10 records seeded)
- People who register for events
- `email` is used as a unique identifier to prevent duplicate accounts
- `role` distinguishes attendees, volunteers, and organizers

**registrations** (15 records seeded)
- Junction/bridge table implementing the many-to-many relationship between events and participants
- `status` can be 'confirmed', 'waitlisted', or 'cancelled'
- `UNIQUE(event_id, participant_id)` constraint prevents duplicate registrations
- `registered_at` tracks when someone signed up

### Key SQL Concepts Used
- **Foreign keys** with `PRAGMA foreign_keys = ON` enforcement
- **JOIN queries** (LEFT JOIN for events + venues, JOIN for registrations + participants)
- **Aggregate functions** (COUNT, GROUP BY) for reports
- **Subqueries** (counting registrations within event listings)
- **Parameterized queries** to prevent SQL injection
- **UNIQUE constraints** for data integrity
- **Dynamic query building** (search filters appended conditionally)

---

## 4. Backend Implementation (Python/Flask)

### Application Structure (`app.py`)

The Flask app defines these route groups:

**Public Routes:**
| Route | Method | Purpose |
|-------|--------|---------|
| `/` | GET | Home page with stats and featured events |
| `/events` | GET | Event listing with search, filter by category/date |
| `/events/<id>` | GET | Single event detail page |
| `/events/<id>/register` | GET, POST | Registration form and submission |
| `/events/<id>/cancel/<pid>` | POST | Cancel a registration |
| `/reports` | GET | Summary reports and analytics |
| `/api/events` | GET | JSON API endpoint |

**Admin Routes:**
| Route | Method | Purpose |
|-------|--------|---------|
| `/admin` | GET | Admin dashboard |
| `/admin/events/new` | GET, POST | Create new event |
| `/admin/events/<id>/edit` | GET, POST | Edit existing event |
| `/admin/events/<id>/delete` | POST | Delete event |
| `/admin/venues/new` | GET, POST | Add new venue |

### Key Backend Logic

**Registration with Waitlisting:**
When a user registers, the system checks if the event has reached `max_participants`. If yes, the registration status is set to 'waitlisted' instead of 'confirmed'. If the participant's email already exists, we reuse that record instead of creating a duplicate.

**Venue Conflict Detection:**
Before creating or editing an event, we query the database for any existing events at the same venue on the same date with overlapping times. The time overlap check uses: `NOT (existing_end <= new_start OR existing_start >= new_end)`.

**Search & Filtering:**
The `get_all_events()` function dynamically builds the SQL query based on which filters are provided. It uses parameterized queries with `LIKE` for text search and exact matching for category/date filters.

**Flash Messages:**
Flask's built-in flash messaging system provides user feedback (success, error, warning, info) that's displayed and auto-dismissed after 5 seconds via JavaScript.

### Data Layer (`database.py`)

All database interaction is isolated in `database.py`. This separation means:
- The Flask routes never contain SQL
- We can switch databases (e.g., to PostgreSQL) by only changing this file
- Testing is easier — we can point `DB_PATH` to a temp file
- Connection management is centralized (`get_connection()`)

---

## 5. Frontend Implementation (HTML/CSS/JS)

### Template Inheritance

We use Jinja2's template inheritance to keep things DRY:

```
base.html (navbar, flash messages, footer, CSS/JS imports)
    ├── index.html (home page)
    ├── events.html (event listing)
    ├── event_detail.html (single event)
    ├── register.html (registration form)
    ├── admin.html (admin panel)
    ├── event_form.html (create/edit event)
    ├── venue_form.html (add venue)
    └── reports.html (summary reports)
```

Every child template extends `base.html` and only defines its unique `{% block content %}`.

### CSS Design System

The stylesheet (`style.css`) implements:
- **CSS Grid** for responsive layouts (events grid, stats bar, reports grid)
- **Card-based UI** for events and statistics
- **Color-coded category badges** (technical=blue, cultural=purple, workshop=green, etc.)
- **Mobile responsiveness** via media queries at 768px breakpoint
- **Consistent spacing** and typography scale
- **Hover effects** and transitions for interactive elements

### JavaScript Features (`main.js`)

- **Auto-dismissing alerts**: Flash messages fade out after 5 seconds
- **Live search**: Client-side filtering of event cards as you type (debounced at 300ms)
- **Form validation**: Highlights required fields that are empty before submission

---

## 6. Testing Strategy

### Test Framework: pytest

We chose pytest for its:
- Minimal boilerplate (plain functions or classes, no unittest inheritance)
- `tmp_path` fixture for isolated test databases
- Descriptive assertion error messages
- Easy fixture composition

### Test Coverage

**`test_database.py`** — 14 test cases covering the data layer:
- Seed data verification (venues loaded, events loaded)
- CRUD operations (create/read/update/delete for events and venues)
- Search and filtering (keyword, category, date range)
- Registration logic (new participant, duplicate detection, cancellation)
- Venue conflict detection (overlapping, non-overlapping, different dates)
- Summary report generation

**`test_app.py`** — 17 test cases covering the web layer:
- All GET routes return 200
- Event not found returns redirect (302)
- Form submissions (POST) return redirect on success
- API endpoints return valid JSON
- Admin operations (create, delete) work correctly

### Test Isolation

Each test gets its own SQLite database via `tmp_path`:
```python
@pytest.fixture(autouse=True)
def setup_test_db(tmp_path):
    db.DB_PATH = str(tmp_path / 'test_events.db')
    db.init_db()
    db.seed_data()
```

This means tests don't interfere with each other and don't touch the production database.

---

## 7. Profiling & Performance Analysis

### Tool: cProfile + pstats

Python's built-in `cProfile` is a deterministic profiler that tracks every function call, its count, and time spent. We wrap our database operations in a profiling session and analyze the results.

### What We Profile

The profiling script simulates realistic load:
- 50 calls to `get_all_events()` (full listing)
- 50 calls with search filters
- 30 calls with category filters
- 30 calls with date range filters
- 160 calls to `get_event_by_id()` (8 events × 20 each)
- 40 calls to `get_all_venues()`
- 20 calls to `get_summary_report()` (most expensive — multiple aggregate queries)
- 80 calls to `get_event_registrations()`
- 20 venue conflict checks

### Benchmark Output

The script prints:
1. **cProfile stats**: Top 20 functions sorted by cumulative time — shows where the application spends the most time
2. **Individual benchmarks**: Each operation timed over 100 runs, reporting avg/min/max in milliseconds

### Findings & Bottlenecks

Typical findings from profiling:
- `get_summary_report()` is the slowest function because it runs 4 separate aggregate queries
- `sqlite3.connect()` appears frequently — connection pooling could help at scale
- String formatting in LIKE queries adds overhead to search operations
- Most individual operations complete in < 1ms with SQLite, which is well within acceptable range for a campus-scale application

---

## 8. Bash Automation Script

### What `setup.sh` Does

The script (`scripts/setup.sh`) automates the entire project setup:

1. **Environment check**: Verifies Python 3 is installed
2. **Virtual environment**: Creates an isolated Python environment (avoids polluting global packages)
3. **Dependencies**: Installs Flask and its dependencies from `requirements.txt`
4. **Database**: Initializes the SQLite database and loads seed data
5. **Tests**: Runs the full test suite and reports results
6. **Profiling**: Runs the performance profiler

### Bash Concepts Used
- Shebang (`#!/bin/bash`) and `set -e` (exit on error)
- Variable substitution and path manipulation
- Command substitution `$(...)` for getting the project directory
- Conditional execution with `||` for non-critical failures
- `source` for virtual environment activation
- Cross-platform venv activation (Linux/Windows paths)

---

## 9. Key Design Decisions

### No ORM — Raw SQL
We deliberately avoided SQLAlchemy or any ORM. Writing raw SQL gives us:
- Full control over query optimization
- Better understanding of what the database actually does
- Simpler debugging (the SQL is right there in the code)
- Lighter dependency footprint

### SQLite over MySQL/PostgreSQL
For a campus-scale app (hundreds of users, not millions), SQLite is the right choice:
- No server setup or configuration
- The entire database is one portable file
- Supports everything we need (joins, constraints, aggregation)
- Faster for read-heavy workloads on a single server

### Server-Side Rendering
We chose Flask with Jinja2 templates (server-side rendering) instead of a SPA framework (React/Vue) because:
- Simpler to understand and debug
- No build step required
- Works without JavaScript for core functionality
- Better for a project focused on backend concepts

### Seed Data
The database is pre-loaded with realistic sample data (6 venues, 8 events, 10 participants, 15 registrations) so the application is immediately usable for demos without manual data entry.

---

## 10. How to Run / Quick Start

```bash
# Clone
git clone https://github.com/swasti-sj/ssl_project.git
cd ssl_project

# Setup (automated)
bash scripts/setup.sh

# Or manual
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
python app.py

# Tests
python -m pytest tests/ -v

# Profiling
python profiling/profile_app.py
```

Open `http://localhost:5000` in a browser.

---

## 11. Future Improvements

Things we'd add given more time:
- User authentication (login/signup with password hashing)
- Email notifications on registration confirmation
- Calendar view for events (full month grid)
- Export registrations to CSV
- Event image uploads
- QR code generation for event check-in
- WebSocket-based real-time seat availability
- Rate limiting on the API endpoint

---

## 12. Summary Table

| Requirement | Implementation | Files |
|------------|---------------|-------|
| Web interface | Flask + HTML/CSS/JS | app.py, templates/, static/ |
| Database | SQLite with 4 tables, foreign keys, joins | database.py |
| Search/Filtering | Keyword search, category filter, date range | database.py, events.html |
| Registration | Register, waitlist, cancel | database.py, register.html |
| Admin controls | CRUD for events and venues | admin.html, event_form.html |
| Reports | Aggregated statistics | reports.html, database.py |
| Bash script | Automated setup, test, profile | scripts/setup.sh |
| Test cases | 31 tests (pytest) | tests/ |
| Profiling | cProfile + benchmarks | profiling/profile_app.py |
| Version control | Git with meaningful commits | .git/ |
| Documentation | README + explain.md | README.md, explain.md |
