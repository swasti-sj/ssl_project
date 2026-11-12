# Campus Event Management Platform

A web-based platform for managing campus events, venues, schedules, registrations, and participants. Built with Python (Flask), SQLite, HTML/CSS, and JavaScript.

## Features

- **Event Management**: Create, edit, delete, and browse campus events
- **Venue Management**: Track venues with capacity, facilities (projector, AC)
- **Registration System**: Register participants, handle waitlisting, cancel registrations
- **Search & Filtering**: Search by keyword, filter by category, date range
- **Venue Conflict Detection**: Prevents double-booking of venues
- **Admin Panel**: Full CRUD controls for events and venues
- **Summary Reports**: Statistics on events, registrations, venues, and departments
- **REST API**: JSON endpoint for programmatic event access

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Backend | Python 3.x, Flask |
| Database | SQLite3 |
| Frontend | HTML5, CSS3, JavaScript |
| Testing | pytest |
| Profiling | cProfile, pstats |
| Automation | Bash scripting |

## Project Structure

```
ssl_project/
├── app.py                  # Flask application and routes
├── database.py             # Database schema, CRUD, queries
├── requirements.txt        # Python dependencies
├── templates/              # Jinja2 HTML templates
│   ├── base.html           # Base layout
│   ├── index.html          # Home page
│   ├── events.html         # Event listing with filters
│   ├── event_detail.html   # Single event view
│   ├── register.html       # Registration form
│   ├── admin.html          # Admin dashboard
│   ├── event_form.html     # Create/edit event form
│   ├── venue_form.html     # Add venue form
│   └── reports.html        # Summary reports
├── static/
│   ├── css/style.css       # Stylesheet
│   └── js/main.js          # Client-side JS
├── tests/
│   ├── test_database.py    # Database unit tests
│   └── test_app.py         # Route integration tests
├── scripts/
│   └── setup.sh            # Automated setup script
├── profiling/
│   └── profile_app.py      # Performance profiling
└── explain.md              # Detailed project explanation
```

## Installation & Setup

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Git

### Option 1: Automated Setup (Bash)

```bash
git clone https://github.com/swasti-sj/ssl_project.git
cd ssl_project
chmod +x scripts/setup.sh
bash scripts/setup.sh
```

This script will:
1. Create a virtual environment
2. Install dependencies
3. Initialize the database with sample data
4. Run tests
5. Run profiling

### Option 2: Manual Setup

```bash
# clone the repo
git clone https://github.com/swasti-sj/ssl_project.git
cd ssl_project

# create virtual environment
python -m venv venv

# activate it
# Linux/Mac:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# install dependencies
pip install -r requirements.txt

# run the application
python app.py
```

### Running the App

After setup, the app runs on `http://localhost:5000`:

```bash
python app.py
```

The database is automatically created and seeded with sample data on first run.

## Usage

| Page | URL | Description |
|------|-----|-------------|
| Home | `/` | Dashboard with stats and upcoming events |
| Events | `/events` | Browse all events with search/filter |
| Event Details | `/events/<id>` | View event info and registered participants |
| Register | `/events/<id>/register` | Register for an event |
| Admin | `/admin` | Manage events and venues |
| New Event | `/admin/events/new` | Create a new event |
| Reports | `/reports` | View summary statistics |
| API | `/api/events` | JSON endpoint (supports `?search=` and `?category=`) |

## Running Tests

```bash
python -m pytest tests/ -v
```

Tests cover:
- Database CRUD operations (venues, events, participants)
- Search and filtering functionality
- Registration and waitlisting logic
- Venue conflict detection
- All Flask routes and form submissions
- API endpoints

## Profiling

```bash
python profiling/profile_app.py
```

Outputs:
- Top 20 functions by cumulative execution time (cProfile)
- Individual operation benchmarks (avg/min/max in milliseconds)

## Topics Covered

- Web development (Flask, HTML/CSS, JavaScript)
- Database design and SQL (SQLite, foreign keys, joins, aggregation)
- Software testing (unit tests, integration tests, pytest fixtures)
- Performance profiling (cProfile, benchmarking)
- Version control (Git, branching, commit history)
- Shell scripting (Bash automation)
- REST API design
- MVC architecture pattern

## Team

- Swasti (Lead Developer)
- Team Member 2
- Team Member 3
- Team Member 4
- Team Member 5
