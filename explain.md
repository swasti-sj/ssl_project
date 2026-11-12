# Campus Event Management Platform - Complete Project Explanation

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

### Team
- Swasti (Lead Developer)
- Shivtej
- Sai
- Aditya
- Sumit

---

## 2. Complete Project Structure (File Tree)

```
ssl_project/
├── .gitignore              # tells git which files to ignore
├── requirements.txt        # python package dependencies
├── app.py                  # main flask web application (controller)
├── database.py             # all database logic and SQL (model)
├── export_csv.py           # CSV export utility (by Shivtej)
├── statistics_helper.py    # analytics and stats functions (by Sai)
├── notifications.py        # email notification templates (by Aditya)
├── validators.py           # input validation module (by Sumit)
├── README.md               # project overview and setup instructions
├── explain.md              # this file - detailed explanation
├── templates/              # HTML templates (views)
│   ├── base.html           # base layout all pages inherit from
│   ├── index.html          # home page with stats dashboard
│   ├── events.html         # event listing with search/filter
│   ├── event_detail.html   # single event page with registrations
│   ├── register.html       # participant registration form
│   ├── admin.html          # admin dashboard for managing everything
│   ├── event_form.html     # create/edit event form
│   ├── venue_form.html     # add venue form
│   └── reports.html        # summary reports and analytics
├── static/                 # static assets served directly
│   ├── css/
│   │   └── style.css       # all CSS styling
│   └── js/
│       └── main.js         # client-side JavaScript
├── tests/                  # automated test suite
│   ├── test_database.py    # unit tests for database layer
│   └── test_app.py         # integration tests for web routes
├── scripts/
│   └── setup.sh            # bash automation script
└── profiling/
    └── profile_app.py      # performance profiling script
```

---

## 3. Architecture & Design

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

### How it all connects (the big picture)

1. A user opens their browser and goes to `http://localhost:5000`
2. The browser sends an HTTP GET request to Flask (`app.py`)
3. Flask's route decorator matches the URL to a Python function (e.g. `/events` maps to `events_list()`)
4. That function calls database.py functions (e.g. `db.get_all_events(search="Tech")`) to fetch data
5. database.py opens a connection to the SQLite file (`events.db`), runs the SQL query, and returns rows as Python dicts
6. The Flask function passes that data to a Jinja2 HTML template (e.g. `events.html`)
7. The template renders the data into HTML, which Flask sends back to the browser
8. The browser displays the page, loads `style.css` for styling and `main.js` for interactivity
9. When the user submits a form (like registering), the browser sends a POST request, Flask processes it, calls database.py to write, and redirects back

### Design Pattern: MVC (Model-View-Controller)

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

## 4. Detailed File-by-File Explanation

### 4.1 `.gitignore` — Git Ignore Rules

**Purpose:** Tells Git which files and folders should NOT be tracked in version control.

**What it excludes:**
- `__pycache__/`, `*.pyc`, `*.pyo` — Python bytecode cache (auto-generated, not source code)
- `*.db`, `*.sqlite3` — Database files (generated at runtime, would cause merge conflicts)
- `.env` — Environment variable files (may contain secrets)
- `venv/`, `env/` — Virtual environment folders (large, machine-specific)
- `.idea/`, `.vscode/` — IDE settings (personal preference, not project code)
- `profiling/output/` — Profiling output (generated data, not source)

**Why it matters:** Without this file, the repo would be cluttered with hundreds of auto-generated files, database binaries, and machine-specific configs that don't belong in version control.

---

### 4.2 `requirements.txt` — Python Dependencies

**Purpose:** Lists the exact Python packages needed to run the project.

**Contents:**
```
flask==3.0.0        # the web framework
werkzeug==3.0.1     # Flask's HTTP utility library (handles requests/responses)
jinja2==3.1.2       # template engine (renders HTML with Python data)
```

**How it's used:**
```bash
pip install -r requirements.txt
```
This one command installs everything needed. Pinning exact versions (e.g. `flask==3.0.0` not just `flask`) ensures everyone gets the same working setup regardless of when they install.

---

### 4.3 `database.py` — The Data Layer (Model)

**Purpose:** This is the backbone of the application. It defines the database schema, creates all 4 tables, seeds sample data, and provides every function the app needs to read/write data. No other file in the project writes SQL — they all go through database.py.

**Imports used:**
- `sqlite3` — Python's built-in SQLite database driver
- `os` — for building the database file path
- `datetime` — for timestamps

#### Connection Management

```python
DB_PATH = os.path.join(os.path.dirname(__file__), 'events.db')
```
The database file is stored in the same directory as the script. This path is a module-level variable so tests can override it to use a temporary file.

```python
def get_connection():
```
Every database operation calls this function first. It:
- Opens a connection to the SQLite file
- Sets `row_factory = sqlite3.Row` so query results are accessible by column name (e.g. `row['title']` instead of `row[0]`)
- Enables foreign key enforcement with `PRAGMA foreign_keys = ON` (SQLite has foreign keys but they're disabled by default)

#### Schema Definition — `init_db()`

Creates 4 tables if they don't already exist:

**Table: `venues`** — Physical locations for events
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PK | Auto-incrementing unique ID |
| name | TEXT UNIQUE | Venue name (no duplicates allowed) |
| location | TEXT | Building/floor description |
| capacity | INTEGER | Maximum seating |
| has_projector | INTEGER (0/1) | Boolean flag for projector availability |
| has_ac | INTEGER (0/1) | Boolean flag for AC availability |

**Table: `events`** — The central table
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PK | Auto-incrementing unique ID |
| title | TEXT | Event name |
| description | TEXT | Detailed description |
| event_date | TEXT | Date in YYYY-MM-DD format |
| start_time | TEXT | Start time in HH:MM format |
| end_time | TEXT | End time in HH:MM format |
| venue_id | INTEGER FK | Links to venues.id |
| organizer | TEXT | Who's organizing |
| category | TEXT | general/technical/cultural/workshop/academic/lecture/sports |
| max_participants | INTEGER | Cap for registrations (triggers waitlisting) |
| created_at | TEXT | Auto-set timestamp |

**Table: `participants`** — People who register
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PK | Auto-incrementing unique ID |
| name | TEXT | Full name |
| email | TEXT | Used as unique identifier |
| phone | TEXT | Optional phone number |
| department | TEXT | CSE, ECE, ME, etc. |
| role | TEXT | attendee/volunteer/organizer |

**Table: `registrations`** — Junction table (many-to-many between events and participants)
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PK | Auto-incrementing unique ID |
| event_id | INTEGER FK | Links to events.id |
| participant_id | INTEGER FK | Links to participants.id |
| registered_at | TEXT | When they registered |
| status | TEXT | confirmed/waitlisted/cancelled |
| UNIQUE(event_id, participant_id) | Constraint | Prevents double registration |

#### Seed Data — `seed_data()`

Pre-loads the database with realistic sample data so the app isn't empty on first run:
- 6 venues (Main Auditorium, Seminar Halls, Open Air Theatre, Conference Room, Computer Lab)
- 8 events (Tech Fest, ML Workshop, Cultural Night, Research Presentations, Guest Lecture, Coding Marathon, Sports Day, Alumni Meetup)
- 10 participants with names, emails, departments
- 15 registrations linking participants to events

The function checks `SELECT COUNT(*) FROM venues` first — if venues already exist, it skips seeding (idempotent, safe to call multiple times).

#### CRUD Functions

**Reading data:**
- `get_all_events(search, category, date_from, date_to)` — The most complex query. It JOINs events with venues, includes a subquery to count confirmed registrations per event, and dynamically appends WHERE clauses based on which filters are provided. Uses parameterized queries (`?` placeholders) to prevent SQL injection.
- `get_event_by_id(event_id)` — Fetches a single event with its venue details.
- `get_all_venues()` — Simple SELECT * ordered by name.
- `get_venue_by_id(venue_id)` — Single venue lookup.
- `get_event_registrations(event_id)` — JOINs registrations with participants to get full registration details for an event.
- `get_summary_report()` — Runs 4 separate aggregate queries to build a dashboard: total counts, events grouped by category, top events by registration count, venue usage stats, and registrations grouped by department.

**Writing data:**
- `create_event(data)` — INSERT into events table, returns the new event's ID.
- `update_event(event_id, data)` — UPDATE an existing event's fields.
- `delete_event(event_id)` — First deletes related registrations (to satisfy foreign key constraints), then deletes the event.
- `create_venue(data)` — INSERT into venues table.

**Registration logic:**
- `register_participant(event_id, participant_data)` — The most interesting function. It:
  1. Checks if a participant with that email already exists (reuses them if so)
  2. If new, creates the participant record
  3. Counts current confirmed registrations for the event
  4. Compares against `max_participants` to decide: 'confirmed' or 'waitlisted'
  5. INSERTs into registrations table
  6. Catches `IntegrityError` if they're already registered (returns error message)
- `cancel_registration(event_id, participant_id)` — DELETEs the registration row.

**Venue conflict detection:**
- `check_venue_conflict(venue_id, event_date, start_time, end_time, exclude_event_id)` — Queries for any event at the same venue on the same date where times overlap. The overlap logic: `NOT (existing_end <= new_start OR existing_start >= new_end)`. The optional `exclude_event_id` parameter is used when editing an event (so it doesn't conflict with itself).

#### SQL Concepts Demonstrated
- Foreign keys with enforcement (`PRAGMA foreign_keys = ON`)
- LEFT JOIN (events + venues — includes events even if venue is NULL)
- INNER JOIN (registrations + participants)
- Subqueries (counting registrations within SELECT)
- Aggregate functions (COUNT, GROUP BY, ORDER BY)
- Parameterized queries (prevent SQL injection)
- UNIQUE constraints (data integrity)
- Dynamic query building (conditionally appending WHERE clauses)
- Transaction management (commit/close pattern)

---

### 4.4 `app.py` — The Web Application (Controller)

**Purpose:** This is the Flask web server. It defines all URL routes, handles HTTP requests, calls database.py for data, and renders HTML templates. It's the glue between the user's browser and the database.

**Imports used:**
- `Flask` — the web framework class
- `render_template` — renders Jinja2 HTML templates
- `request` — access to incoming HTTP request data (URL params, form fields)
- `redirect`, `url_for` — for sending users to a different page after form submission
- `flash` — for showing one-time feedback messages (success, error, etc.)
- `jsonify` — converts Python dicts to JSON for the API endpoint

**App setup:**
```python
app = Flask(__name__)
app.secret_key = 'campus-event-mgmt-secret-key-2024'
```
The secret key is required by Flask for session management and flash messages (it signs the session cookie).

**`@app.before_request` hook:**
```python
@app.before_request
def setup():
    db.init_db()
    db.seed_data()
```
This runs before EVERY request. It ensures the database exists and has seed data. Both functions are idempotent (safe to call repeatedly — they check before creating).

#### Route-by-Route Breakdown

**`GET /` → `index()`**
Home page. Fetches all events and the summary report, passes them to `index.html`. Shows a hero banner, stats cards, and the first 6 events.

**`GET /events` → `events_list()`**
Main event browsing page. Reads URL query parameters (`?search=Tech&category=technical&date_from=2024-01-01&date_to=2024-12-31`), passes them to `get_all_events()`, renders `events.html` with the filtered results.

**`GET /events/<id>` → `event_detail(event_id)`**
Single event page. Looks up the event by ID — if not found, flashes an error and redirects to the event list. Otherwise fetches the event's registrations and renders `event_detail.html`.

**`GET/POST /events/<id>/register` → `register_for_event(event_id)`**
- GET: Shows the registration form (`register.html`)
- POST: Reads form data (name, email, phone, department), calls `register_participant()`, flashes a success/waitlist/error message, redirects to the event detail page

**`POST /events/<id>/cancel/<pid>` → `cancel_registration(event_id, participant_id)`**
Cancels a registration and redirects back to the event detail page.

**`GET /admin` → `admin_panel()`**
Admin dashboard. Shows all events in a table with edit/delete buttons, and all venues with their details.

**`GET/POST /admin/events/new` → `create_event()`**
- GET: Shows empty event creation form with venue dropdown
- POST: Reads form data, checks for venue scheduling conflicts. If conflict found, flashes error and re-shows the form. If clean, creates the event and redirects to admin panel.

**`GET/POST /admin/events/<id>/edit` → `edit_event(event_id)`**
Same as create but pre-fills the form with existing data. On POST, checks venue conflicts (excluding the current event), updates the record.

**`POST /admin/events/<id>/delete` → `delete_event(event_id)`**
Deletes the event and all its registrations, redirects to admin panel.

**`GET/POST /admin/venues/new` → `create_venue()`**
Form to add a new venue with name, location, capacity, and amenity checkboxes.

**`GET /reports` → `reports()`**
Renders summary statistics: total counts, events by category, top events, venue usage, registrations by department.

**`GET /api/events` → `api_events()`**
REST API endpoint. Returns all events as JSON. Supports `?search=` and `?category=` query parameters. This is useful for external tools or AJAX calls.

**`if __name__ == '__main__':`**
When run directly with `python app.py`, initializes the database and starts Flask's development server on port 5000 with debug mode enabled (auto-reloads on code changes).

---

### 4.5 `templates/base.html` — Base Layout Template

**Purpose:** The master template that every other page inherits from. Defines the common HTML structure so it's written once, not repeated in every page.

**What it provides:**
- `<!DOCTYPE html>`, charset, viewport meta (responsive) — standard HTML5 boilerplate
- `<title>` with a Jinja2 block: `{% block title %}Campus Events{% endblock %}` — child templates override this
- CSS stylesheet link (`style.css`)
- **Navigation bar** with links to Home, Events, Reports, Admin
- **Flash message area**: Loops through `get_flashed_messages(with_categories=true)` and renders each as a colored alert div (success=green, error=red, warning=yellow, info=blue)
- `{% block content %}{% endblock %}` — the placeholder that child templates fill with their page-specific content
- **Footer** with copyright text
- JavaScript file link (`main.js`)

**How template inheritance works:**
Every other template starts with `{% extends 'base.html' %}` and only defines the content block. They automatically get the navbar, footer, flash messages, and CSS/JS without repeating any of it.

---

### 4.6 `templates/index.html` — Home Page

**Purpose:** The landing page users see at `/`. Gives a quick overview of the platform.

**Sections:**
1. **Hero banner** — gradient background with title, tagline, and "Browse Events" button
2. **Stats bar** — 4 cards showing total events, participants, registrations, and venues (data comes from `report` variable passed by the controller)
3. **Upcoming Events grid** — Shows the first 6 events as cards. Each card has: category badge, date, title, venue, time, organizer, registration count, and a "View Details" link

**Jinja2 features used:** `{{ variable }}` for outputting data, `{% for %}` loop, slice with `events[:6]`, `{{ event.venue_name or 'TBD' }}` for fallback values.

---

### 4.7 `templates/events.html` — Event Listing with Search/Filter

**Purpose:** The main browsing page at `/events`. Shows all events with powerful filtering.

**Sections:**
1. **Search/Filter bar** — A form with:
   - Text search input (searches title, description, organizer)
   - Category dropdown (technical, cultural, workshop, academic, lecture, sports, general)
   - Date range inputs (from/to)
   - Filter button and Clear button
2. **Events grid** — All matching events as cards, each with: category badge, date, truncated description (120 chars), venue, time, organizer, spots remaining, Register and Details buttons
3. **Empty state** — "No events found matching your criteria" if filters return nothing

The form submits via GET (query params in URL), so filtered results are bookmarkable/shareable.

---

### 4.8 `templates/event_detail.html` — Single Event Page

**Purpose:** Shows full details for one event at `/events/<id>`.

**Layout:** Two-column grid:
- **Left column (Detail Info):**
  - Category badge and title
  - Full description
  - Info table: date, time, venue, capacity, max participants, current registration count
  - "Register Now" button
- **Right column (Registrations):**
  - Table of all registered participants: name, department, status (confirmed/waitlisted), cancel button
  - Each cancel button is a POST form with a JavaScript confirmation dialog

---

### 4.9 `templates/register.html` — Registration Form

**Purpose:** Form at `/events/<id>/register` where users sign up for an event.

**Form fields:**
- Full Name (required)
- Email (required, type=email for browser validation)
- Phone (optional)
- Department (dropdown: CSE, ECE, EE, ME, CE, IT)
- Submit and Cancel buttons

On submission, POST request goes to the same URL. Flask processes it, calls `register_participant()`, and redirects to the event detail page with a flash message.

---

### 4.10 `templates/admin.html` — Admin Dashboard

**Purpose:** Central management page at `/admin`.

**Sections:**
1. **Events Management** — Header with "+ New Event" button, then a table of all events showing: title, date, venue, category badge, registration count/max, Edit and Delete buttons. Delete has a confirmation dialog.
2. **Venues** — Header with "+ New Venue" button, then a table showing: name, location, capacity, projector (checkmark/cross), AC (checkmark/cross)

---

### 4.11 `templates/event_form.html` — Create/Edit Event Form

**Purpose:** Dual-purpose form used for both creating new events and editing existing ones at `/admin/events/new` and `/admin/events/<id>/edit`.

**How dual-purpose works:** The template receives an `editing` boolean and a `data` dict. If editing, the form fields are pre-filled with `data.get('title', '')`. The submit button says "Create" or "Update" accordingly. The form's POST action goes to the appropriate route.

**Fields:** Title, description (textarea), date/start time/end time (row), venue dropdown (shows capacity), category dropdown, organizer, max participants.

---

### 4.12 `templates/venue_form.html` — Add Venue Form

**Purpose:** Form at `/admin/venues/new` for adding new venues.

**Fields:** Venue name, location (with placeholder example), seating capacity, checkboxes for projector and AC.

---

### 4.13 `templates/reports.html` — Summary Reports Page

**Purpose:** Analytics dashboard at `/reports`.

**Sections:**
1. **Stats bar** — Same 4 stat cards as home page (events, participants, registrations, venues)
2. **Reports grid** — 4 report cards, each with a data table:
   - Events by Category (e.g. technical: 2, cultural: 1, ...)
   - Top Events by Registrations (most popular events)
   - Venue Utilization (how many events each venue hosted)
   - Registrations by Department (which departments are most active)

---

### 4.14 `static/css/style.css` — Stylesheet

**Purpose:** All visual styling for the entire application. ~350 lines of CSS.

**Key design systems:**
- **Layout:** CSS Grid for multi-column layouts (events grid, stats bar, reports, detail page). `grid-template-columns: repeat(auto-fill, minmax(350px, 1fr))` creates responsive columns that automatically wrap.
- **Card pattern:** White background, border-radius, box-shadow, hover effect. Used for events, stats, and reports.
- **Color palette:** Dark blue (`#2c3e50`) for headers/navbar, blue (`#3498db`) for primary actions, red (`#e74c3c`) for danger, green (`#27ae60`) for success, gray scale for text.
- **Category badges:** Each category gets a unique background/text color combo (technical=blue, cultural=purple, workshop=green, academic=orange, lecture=navy, sports=red, general=gray).
- **Button system:** `.btn` base class with modifiers (`.btn-primary`, `.btn-secondary`, `.btn-danger`, `.btn-small`). Hover effects include slight upward translation.
- **Form styling:** Consistent input fields with focus states (blue border on focus), form groups with labels, multi-column rows.
- **Table styling:** Striped-on-hover data tables with header styling.
- **Flash alerts:** Color-coded with borders (green/red/yellow/blue).
- **Responsive design:** `@media (max-width: 768px)` breakpoint collapses grids to single column, stacks navbar, switches form rows to vertical.
- **Navbar:** Flexbox layout, dark background, white links with hover color change.

---

### 4.15 `static/js/main.js` — Client-Side JavaScript

**Purpose:** Adds interactivity to the browser-rendered pages. ~57 lines of vanilla JavaScript (no frameworks).

**Feature 1: Auto-dismissing flash alerts**
```javascript
setTimeout(function() {
    alert.style.opacity = '0';
    setTimeout(function() { alert.remove(); }, 500);
}, 5000);
```
After 5 seconds, each flash message fades out (opacity transition over 0.5s) and is removed from the DOM. This keeps the UI clean without requiring user action.

**Feature 2: Live search filtering**
```javascript
searchInput.addEventListener('input', function() {
    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(function() {
        // filter cards by title/description match
    }, 300);
});
```
On the events page, as the user types in the search box, event cards are instantly shown/hidden based on whether their title or description contains the search text. Uses **debouncing** (300ms delay) so it doesn't re-filter on every keystroke — waits until the user pauses typing. This is client-side filtering (instant, no server request) that works alongside the server-side search.

**Feature 3: Form validation**
Before form submission, checks all `[required]` fields. Empty fields get a red border, and submission is prevented with an alert. This provides immediate feedback before the form even hits the server.

---

### 4.16 `tests/test_database.py` — Database Unit Tests

**Purpose:** Tests every function in database.py in isolation. 18 test cases organized into 5 test classes.

**Test fixture:**
```python
@pytest.fixture(autouse=True)
def setup_test_db(tmp_path):
    db.DB_PATH = str(tmp_path / 'test_events.db')
    db.init_db()
    db.seed_data()
```
Before each test, creates a fresh SQLite database in a temporary directory. This means:
- Tests don't affect each other (complete isolation)
- Tests don't touch the real database
- The temp directory is automatically cleaned up by pytest

**Test classes and what they verify:**

**TestVenues (3 tests):**
- `test_seed_venues_loaded` — Verifies all 6 seed venues are present
- `test_create_venue` — Creates a venue, retrieves it, checks all fields match
- `test_get_venue_by_id` — Fetches venue ID 1, verifies it's "Main Auditorium"

**TestEvents (7 tests):**
- `test_seed_events_loaded` — Verifies all 8 seed events are present
- `test_create_event` — Creates an event with all fields, retrieves and verifies
- `test_update_event` — Updates event 1's title, verifies the change persisted
- `test_delete_event` — Deletes event 1, verifies `get_event_by_id` returns None
- `test_search_events` — Searches for "Tech Fest", verifies at least 1 result with matching title
- `test_filter_by_category` — Filters by "technical", verifies all results have that category
- `test_filter_by_date_range` — Filters March 2024, verifies all dates are in March

**TestRegistrations (4 tests):**
- `test_register_new_participant` — Registers a new person, verifies status is 'confirmed'
- `test_duplicate_registration` — Tries to register someone already registered, verifies error message
- `test_get_event_registrations` — Gets registrations for event 1, verifies at least 1 exists
- `test_cancel_registration` — Cancels a registration, verifies count decreased by 1

**TestVenueConflict (3 tests):**
- `test_detect_conflict` — Books venue 1 on 2024-03-15 for a time overlapping with Tech Fest, verifies conflict detected
- `test_no_conflict_different_date` — Same venue, different date (Dec 25), verifies no conflict
- `test_no_conflict_different_time` — Same venue, same date, but non-overlapping time (19:00-21:00), verifies no conflict

**TestReports (1 test):**
- `test_summary_report` — Calls `get_summary_report()`, verifies counts match seed data (8 events, 6 venues, etc.) and that category/top-events lists are non-empty

---

### 4.17 `tests/test_app.py` — Web Route Integration Tests

**Purpose:** Tests the Flask application routes end-to-end. 17 test cases that simulate browser requests.

**Fixtures:**
- Same `setup_test_db` as above (isolated database)
- `client` fixture: Creates a Flask test client (`app.test_client()`) that can make fake HTTP requests without starting a real server

**What each test verifies:**

| Test | What it does | Expected |
|------|-------------|----------|
| `test_home_page` | GET `/` | Status 200, contains "Campus Event" |
| `test_events_page` | GET `/events` | Status 200 |
| `test_events_search` | GET `/events?search=Tech` | Status 200 |
| `test_events_filter_category` | GET `/events?category=technical` | Status 200 |
| `test_event_detail` | GET `/events/1` | Status 200 |
| `test_event_not_found` | GET `/events/9999` | Status 302 (redirect) |
| `test_register_page` | GET `/events/1/register` | Status 200 |
| `test_register_submit` | POST `/events/2/register` with form data | Status 302 (redirect after success) |
| `test_admin_panel` | GET `/admin` | Status 200 |
| `test_create_event_page` | GET `/admin/events/new` | Status 200 |
| `test_create_event_submit` | POST `/admin/events/new` with full form data | Status 302 |
| `test_reports_page` | GET `/reports` | Status 200, contains "Total Events" |
| `test_api_events` | GET `/api/events` | Status 200, response is a JSON list |
| `test_api_events_search` | GET `/api/events?search=Tech` | Status 200 |
| `test_delete_event` | POST `/admin/events/1/delete` | Status 302 |
| `test_create_venue_page` | GET `/admin/venues/new` | Status 200 |
| `test_create_venue_submit` | POST `/admin/venues/new` with form data | Status 302 |

**Why 302?** HTTP 302 is a redirect. After a successful POST (create, delete, register), Flask redirects the user to another page. This is the POST-Redirect-GET pattern — it prevents double-submission if the user refreshes.

---

### 4.18 `scripts/setup.sh` — Bash Automation Script

**Purpose:** Automates the entire project setup, testing, and profiling in one command.

**Step-by-step breakdown:**

```bash
#!/bin/bash           # Shebang — tells the OS to use bash interpreter
set -e                # Exit immediately if any command fails
```

**Step 1 — Check Python:**
Uses `command -v python3` to verify Python 3 is installed. Exits with error message if not.

**Step 2 — Virtual Environment:**
```bash
python3 -m venv "$VENV_DIR"
```
Creates an isolated Python environment so dependencies don't pollute the system. Checks if `venv/` already exists to avoid recreating it.

**Step 3 — Install Dependencies:**
```bash
source "$VENV_DIR/bin/activate" 2>/dev/null || source "$VENV_DIR/Scripts/activate" 2>/dev/null
```
Activates the virtual environment. Tries Linux path first, falls back to Windows path. Then runs `pip install -r requirements.txt`.

**Step 4 — Database Init:**
Runs a Python one-liner that imports database.py and calls `init_db()` and `seed_data()`.

**Step 5 — Tests:**
Runs `python3 -m pytest tests/ -v --tb=short`. The `|| { ... }` ensures the script continues even if some tests fail (test failures shouldn't block setup).

**Step 6 — Profiling:**
Runs `python3 profiling/profile_app.py` with the same error-tolerant pattern.

**Bash concepts demonstrated:**
- Shebang, `set -e` (exit on error)
- Variables and path manipulation (`PROJECT_DIR`, `VENV_DIR`)
- Command substitution `$(cd ... && pwd)`
- Conditional with `-d` (directory exists check)
- `source` for environment activation
- `||` operator for non-critical failure handling
- `2>/dev/null` for suppressing error output
- Heredoc-style inline Python

---

### 4.19 `profiling/profile_app.py` — Performance Profiling

**Purpose:** Measures how fast each database operation runs, identifies bottlenecks, and produces benchmarks.

**Tools used:**
- `cProfile` — Python's built-in deterministic profiler. Records every function call, how many times it was called, and how much time was spent.
- `pstats` — Formats and sorts cProfile output
- `time.perf_counter()` — High-resolution timer for individual benchmarks

**What it does:**

1. **Setup:** Creates a temporary database (`profile_test.db`), initializes and seeds it
2. **cProfile run:** Wraps 470+ database calls in a profiler:
   - 50× `get_all_events()` (unfiltered)
   - 50× `get_all_events(search='Tech')` (with search)
   - 30× `get_all_events(category='technical')` (with filter)
   - 30× `get_all_events(date_from, date_to)` (with date range)
   - 160× `get_event_by_id()` (8 events × 20 each)
   - 40× `get_all_venues()`
   - 20× `get_summary_report()` (most expensive)
   - 80× `get_event_registrations()` (8 events × 10 each)
   - 20× `check_venue_conflict()`
3. **Prints top 20 functions** sorted by cumulative time
4. **Individual benchmarks:** Runs each operation 100 times, reports avg/min/max in milliseconds
5. **Cleanup:** Deletes the temporary database file

**Typical findings:**
- `get_summary_report()` is the slowest — it runs 4 separate aggregate queries
- `sqlite3.connect()` appears frequently — connection pooling would help at scale
- Most operations complete in <1ms — well within acceptable for campus scale
- The LIKE query in search adds marginal overhead compared to exact-match filters

---

### 4.20 `export_csv.py` — CSV Export Utility (by Shivtej)

**Purpose:** Exports event data and registration lists to CSV files for reporting, printing, or importing into Excel.

**Functions:**
- `export_event_registrations(event_id)` — Exports all participants registered for a specific event. Creates a CSV with columns: Name, Email, Phone, Department, Role, Registered At, Status. File is named with the event title and timestamp (e.g. `Annual_Tech_Fest_2024_20240315_143022.csv`).
- `export_all_events_summary()` — Exports a summary of all events to CSV with columns: ID, Title, Date, Time, Venue, Category, Organizer, Registered count, Max capacity.

**CLI usage:**
```bash
python export_csv.py          # exports all events summary
python export_csv.py 1        # exports registrations for event ID 1
```

Files are saved to an `exports/` directory (auto-created).

---

### 4.21 `statistics_helper.py` — Analytics Module (by Sai)

**Purpose:** Provides computed analytics beyond what the basic report offers. Includes a text-based dashboard for terminal display.

**Functions:**
- `get_event_fill_rates()` — Calculates percentage of seats filled for each event. Returns fill rate, and labels events as "Full" (>=100%), "Almost Full" (>=80%), or "Open".
- `get_popular_time_slots()` — Uses Python's `Counter` to find which time slots (e.g. "09:00-18:00") are used most often.
- `get_organizer_stats()` — Groups events by organizer, counts total events and total registrations per organizer.
- `get_venue_utilization()` — Calculates how many events each venue has hosted and lists its amenities.
- `print_dashboard()` — Renders all the above as a formatted ASCII dashboard with bar charts (using `#` characters).

**CLI usage:**
```bash
python statistics_helper.py   # prints the full dashboard
```

---

### 4.22 `notifications.py` — Email Templates (by Aditya)

**Purpose:** Generates email content for various notification scenarios. Doesn't actually send emails (no SMTP) — it generates the text that would be sent.

**Functions:**
- `generate_registration_email(event_id, name, email, status)` — Generates a confirmation or waitlist email with event details (date, time, venue, organizer).
- `generate_cancellation_email(event_id, name, email)` — Generates a cancellation confirmation email.
- `generate_event_reminder(event_id)` — Generates reminder emails for ALL confirmed participants of an event. Returns a list of email dicts.

**Each email is returned as a dict:**
```python
{
    'to': 'student@college.edu',
    'subject': 'Registration Confirmed - Annual Tech Fest',
    'body': 'Dear Rahul, ...',
    'generated_at': '2024-03-15T10:30:00'
}
```

**CLI usage:**
```bash
python notifications.py       # prints sample emails
```

---

### 4.23 `validators.py` — Input Validation Module (by Sumit)

**Purpose:** Validates user input before it reaches the database. Catches bad data early with clear error messages.

**Custom exception:** `ValidationError(field, message)` — carries which field failed and why.

**Validation functions:**
- `validate_email(email)` — Checks format with regex pattern `^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$`. Rejects empty, whitespace-only, or malformed emails.
- `validate_phone(phone)` — Optional field. Strips spaces/dashes/parens, checks it's 10-13 digits (supports `+91` prefix).
- `validate_event_data(data)` — Validates all event form fields: title required and <200 chars, date in YYYY-MM-DD format, end time after start time, organizer required, max_participants is 1-10000, category is one of the allowed values.
- `validate_registration_data(data)` — Validates registration form: name required and <100 chars, valid email, optional valid phone.
- `validate_venue_data(data)` — Validates venue form: name required, location required, capacity is a positive number.

**CLI usage:**
```bash
python validators.py          # runs built-in validation demos
```

---

### 4.24 `README.md` — Project Documentation

**Purpose:** The first thing anyone sees on the GitHub repo page. Provides a quick overview, setup instructions, and usage guide.

**Sections:** Features list, tech stack table, project structure tree, installation (automated + manual), usage table with all URLs, test/profiling commands, topics covered, team list.

---

## 5. How Files Work Together (Collective Flow)

### Flow 1: User browses events and registers

```
Browser → GET /events?search=Tech
         ↓
app.py: events_list() reads query params
         ↓
database.py: get_all_events(search='Tech')
         → SQL: SELECT ... FROM events LEFT JOIN venues WHERE title LIKE '%Tech%'
         → returns list of matching events
         ↓
app.py: render_template('events.html', events=results)
         ↓
templates/events.html: extends base.html, loops through events, renders cards
         ↓
Browser receives HTML → loads style.css (grid layout, card styling)
                       → loads main.js (enables live search filtering)
         ↓
User clicks "Register" → GET /events/1/register
         ↓
app.py: renders register.html with event info
         ↓
User fills form, clicks submit → POST /events/1/register
         ↓
app.py: reads form data, calls db.register_participant(1, {...})
         ↓
database.py: checks email exists? counts registrations vs max_participants
         → INSERT into registrations (status = confirmed or waitlisted)
         ↓
app.py: flash('Registration successful!'), redirect to event detail
         ↓
Browser → GET /events/1 (shows updated registration list)
```

### Flow 2: Admin creates an event

```
Browser → GET /admin/events/new
         ↓
app.py: fetches all venues, renders event_form.html (empty form)
         ↓
User fills form, submits → POST /admin/events/new
         ↓
app.py: reads all form fields, calls db.check_venue_conflict(...)
         ↓
database.py: SQL checks for overlapping events at same venue/date
         → returns empty list (no conflict)
         ↓
app.py: calls db.create_event(data) → INSERT INTO events
         → flash('Event created!'), redirect to /admin
         ↓
Browser → GET /admin (shows updated event table)
```

### Flow 3: Running tests

```
pytest starts → collects test_database.py and test_app.py
         ↓
For each test:
  setup_test_db fixture → creates temp SQLite file, runs init_db() + seed_data()
         ↓
  test function runs (e.g. test_search_events)
    → calls db.get_all_events(search='Tech Fest')
    → asserts result count >= 1
    → asserts 'Tech Fest' in result title
         ↓
  fixture cleanup → temp directory deleted
         ↓
pytest reports: 35 passed
```

### Flow 4: Profiling

```
profile_app.py starts
         ↓
Creates temporary database, seeds data
         ↓
cProfile.enable() → starts recording every function call
         ↓
Runs 470+ database operations (simulated load)
         ↓
cProfile.disable() → stops recording
         ↓
pstats sorts by cumulative time, prints top 20 functions
         ↓
Individual benchmarks: runs each operation 100 times with perf_counter
         → prints avg/min/max ms per operation
         ↓
Cleanup: deletes temp database
```

---

## 6. Database Design (Entity-Relationship)

### ER Diagram

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

### Relationships
- **venues → events**: One-to-Many. One venue can host many events, but each event has one venue.
- **events ↔ participants**: Many-to-Many (via registrations). One event has many participants, one participant can register for many events.
- **registrations**: The bridge/junction table that connects events and participants. Also stores metadata (when they registered, their status).

### Key Constraints
- `venues.name` is UNIQUE — no two venues can have the same name
- `registrations(event_id, participant_id)` is UNIQUE — prevents a person from registering twice for the same event
- Foreign keys ensure referential integrity — you can't register for a non-existent event

---

## 7. Testing Strategy

### Why pytest?
- Minimal boilerplate (plain functions or classes, no unittest inheritance required)
- `tmp_path` fixture creates isolated temp directories automatically
- Descriptive assertion error messages (shows actual vs expected values)
- Easy fixture composition with `autouse=True`

### Test Summary: 35 total tests

| File | Tests | Layer | What's tested |
|------|-------|-------|--------------|
| test_database.py | 18 | Data | CRUD, search, filter, registration logic, conflicts, reports |
| test_app.py | 17 | Web | All routes, form submissions, API, error handling |

### How to run
```bash
python -m pytest tests/ -v          # verbose, shows each test name
python -m pytest tests/ -v --tb=short  # short traceback on failures
python -m pytest tests/test_database.py  # run only database tests
```

---

## 8. Profiling & Performance

### Tool: cProfile (Python standard library)

cProfile is a **deterministic profiler** — it records every function call with:
- How many times it was called (`ncalls`)
- Total time spent in that function alone (`tottime`)
- Cumulative time including sub-calls (`cumtime`)

### What we found (typical results)

| Operation | Avg Time | Notes |
|-----------|----------|-------|
| get_all_events() | ~0.3ms | Fast — single JOIN query |
| get_all_events(search) | ~0.4ms | Slight overhead from LIKE pattern |
| get_event_by_id() | ~0.1ms | Simple primary key lookup |
| get_all_venues() | ~0.1ms | Small table, fast |
| get_summary_report() | ~1.2ms | Slowest — runs 4 aggregate queries |
| get_event_registrations() | ~0.2ms | JOIN on indexed columns |
| check_venue_conflict() | ~0.2ms | Focused query on date + venue |

### Bottleneck Analysis
1. **`get_summary_report()` is 4× slower** than other operations because it runs 4 separate SQL queries (total events, events by category, top events, venue usage). Fix: Could combine into a single query with CTEs, or cache the result.
2. **`sqlite3.connect()` called per operation** — each function opens and closes a connection. At scale, a connection pool would reduce overhead.
3. **All operations under 2ms** — for a campus-scale app (100s of users), this is well within acceptable. No optimization actually needed at our scale.

---

## 9. Bash Automation

### Script: `scripts/setup.sh`

**Concepts demonstrated:**
| Concept | Where in script | What it does |
|---------|----------------|-------------|
| Shebang | `#!/bin/bash` | Tells OS which interpreter to use |
| Strict mode | `set -e` | Exit immediately on any error |
| Variables | `PROJECT_DIR`, `VENV_DIR` | Store paths for reuse |
| Command substitution | `$(cd "$(dirname "$0")/.." && pwd)` | Gets absolute path of project root |
| Conditional | `if [ ! -d "$VENV_DIR" ]` | Check if directory exists |
| Source | `source venv/bin/activate` | Load virtual environment |
| Error suppression | `2>/dev/null` | Hide error output for fallback paths |
| Fallback operator | `\|\|` | Try alternative if first command fails |
| Inline Python | `python3 -c "..."` | Run Python code without a separate file |
| Non-fatal errors | `command \|\| { warning; }` | Continue script even if tests fail |

---

## 10. Key Design Decisions

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

### Server-Side Rendering over SPA
We chose Flask with Jinja2 templates (server-side rendering) instead of a SPA framework (React/Vue) because:
- Simpler to understand and debug
- No build step or node_modules required
- Works without JavaScript for core functionality
- Better for a project focused on backend concepts

### Seed Data
The database is pre-loaded with realistic sample data (6 venues, 8 events, 10 participants, 15 registrations) so the application is immediately usable for demos without manual data entry.

---

## 11. How to Run / Quick Start

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

# CSV Export
python export_csv.py

# Statistics Dashboard
python statistics_helper.py

# Notification Templates
python notifications.py

# Validator Demo
python validators.py
```

Open `http://localhost:5000` in a browser.

---

## 12. Future Improvements

Things we'd add given more time:
- User authentication (login/signup with password hashing)
- Actually sending emails via SMTP (currently just generates templates)
- Calendar view for events (full month grid)
- Event image uploads
- QR code generation for event check-in
- WebSocket-based real-time seat availability
- Connection pooling for database performance
- Rate limiting on the API endpoint
- Role-based access control (separate admin login)

---

## 13. Summary Table

| Requirement | Implementation | Files |
|------------|---------------|-------|
| Web interface | Flask + HTML/CSS/JS | app.py, templates/, static/ |
| Database (SQL) | SQLite with 4 tables, foreign keys, joins, aggregation | database.py |
| Search/Filtering | Keyword search, category filter, date range filter | database.py, events.html |
| Registration | Register with waitlisting, cancel, duplicate prevention | database.py, register.html |
| Admin controls | Full CRUD for events and venues, conflict detection | admin.html, event_form.html, venue_form.html |
| Reports/Analytics | Aggregated statistics, fill rates, utilization | reports.html, database.py, statistics_helper.py |
| CSV Export | Export events and registrations to CSV files | export_csv.py |
| Email Notifications | Registration, cancellation, and reminder templates | notifications.py |
| Input Validation | Email, phone, event, registration, venue validators | validators.py |
| Bash script | Automated setup, dependency install, test, profile | scripts/setup.sh |
| Test cases | 35 tests with pytest (database + web routes) | tests/ |
| Profiling | cProfile + individual benchmarks with timing | profiling/profile_app.py |
| Version control | Git with 14 meaningful commits by 5 team members | .git/ |
| Documentation | README (setup guide) + explain.md (full explanation) | README.md, explain.md |
