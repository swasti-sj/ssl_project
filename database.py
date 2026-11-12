import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), 'events.db')


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS venues (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            location TEXT NOT NULL,
            capacity INTEGER NOT NULL,
            has_projector INTEGER DEFAULT 0,
            has_ac INTEGER DEFAULT 0
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            event_date TEXT NOT NULL,
            start_time TEXT NOT NULL,
            end_time TEXT NOT NULL,
            venue_id INTEGER,
            organizer TEXT NOT NULL,
            category TEXT DEFAULT 'general',
            max_participants INTEGER DEFAULT 100,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (venue_id) REFERENCES venues(id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS participants (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT,
            department TEXT,
            role TEXT DEFAULT 'attendee'
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS registrations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_id INTEGER NOT NULL,
            participant_id INTEGER NOT NULL,
            registered_at TEXT DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'confirmed',
            FOREIGN KEY (event_id) REFERENCES events(id),
            FOREIGN KEY (participant_id) REFERENCES participants(id),
            UNIQUE(event_id, participant_id)
        )
    ''')

    conn.commit()
    conn.close()


def seed_data():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM venues")
    if cursor.fetchone()[0] > 0:
        conn.close()
        return

    venues = [
        ('Main Auditorium', 'Block A, Ground Floor', 500, 1, 1),
        ('Seminar Hall 1', 'Block B, First Floor', 150, 1, 1),
        ('Seminar Hall 2', 'Block B, Second Floor', 120, 1, 0),
        ('Open Air Theatre', 'Central Campus', 1000, 0, 0),
        ('Conference Room 101', 'Block C, First Floor', 50, 1, 1),
        ('Computer Lab 3', 'Block D, Ground Floor', 60, 1, 1),
    ]
    cursor.executemany(
        "INSERT INTO venues (name, location, capacity, has_projector, has_ac) VALUES (?,?,?,?,?)",
        venues
    )

    events = [
        ('Annual Tech Fest 2024', 'A two-day technology festival featuring coding contests, hackathons, and tech talks.',
         '2024-03-15', '09:00', '18:00', 1, 'CSE Department', 'technical', 400),
        ('Workshop on Machine Learning', 'Hands-on workshop covering supervised and unsupervised learning techniques.',
         '2024-02-20', '10:00', '16:00', 2, 'AI Club', 'workshop', 100),
        ('Cultural Night', 'Annual cultural program with music, dance, and drama performances.',
         '2024-04-05', '17:00', '22:00', 4, 'Cultural Committee', 'cultural', 800),
        ('Research Paper Presentation', 'Students present their research work in various CS domains.',
         '2024-03-01', '09:30', '15:00', 5, 'Research Cell', 'academic', 40),
        ('Guest Lecture: Cloud Computing', 'Industry expert discusses trends in cloud infrastructure.',
         '2024-02-28', '14:00', '16:00', 2, 'CSE Department', 'lecture', 130),
        ('Coding Marathon', '12-hour coding competition for all branches.',
         '2024-03-22', '08:00', '20:00', 6, 'Coding Club', 'technical', 55),
        ('Sports Day', 'Inter-department sports competition.',
         '2024-04-10', '07:00', '17:00', 4, 'Sports Committee', 'sports', 500),
        ('Alumni Meetup 2024', 'Annual alumni gathering and networking event.',
         '2024-05-01', '10:00', '14:00', 1, 'Alumni Cell', 'general', 300),
    ]
    cursor.executemany(
        '''INSERT INTO events (title, description, event_date, start_time, end_time,
           venue_id, organizer, category, max_participants) VALUES (?,?,?,?,?,?,?,?,?)''',
        events
    )

    participants = [
        ('Rahul Sharma', 'rahul.s@college.edu', '9876543210', 'CSE', 'attendee'),
        ('Priya Patel', 'priya.p@college.edu', '9876543211', 'ECE', 'attendee'),
        ('Amit Kumar', 'amit.k@college.edu', '9876543212', 'CSE', 'volunteer'),
        ('Sneha Reddy', 'sneha.r@college.edu', '9876543213', 'ME', 'attendee'),
        ('Vikram Singh', 'vikram.s@college.edu', '9876543214', 'CSE', 'organizer'),
        ('Ananya Gupta', 'ananya.g@college.edu', '9876543215', 'EE', 'attendee'),
        ('Rohan Joshi', 'rohan.j@college.edu', '9876543216', 'CSE', 'volunteer'),
        ('Deepika Nair', 'deepika.n@college.edu', '9876543217', 'IT', 'attendee'),
        ('Karthik Menon', 'karthik.m@college.edu', '9876543218', 'CSE', 'attendee'),
        ('Fatima Begum', 'fatima.b@college.edu', '9876543219', 'CE', 'attendee'),
    ]
    cursor.executemany(
        "INSERT INTO participants (name, email, phone, department, role) VALUES (?,?,?,?,?)",
        participants
    )

    registrations = [
        (1, 1, '2024-02-10 09:00:00', 'confirmed'),
        (1, 2, '2024-02-11 10:30:00', 'confirmed'),
        (1, 3, '2024-02-11 11:00:00', 'confirmed'),
        (2, 1, '2024-02-15 08:00:00', 'confirmed'),
        (2, 4, '2024-02-16 14:00:00', 'confirmed'),
        (3, 5, '2024-03-20 12:00:00', 'confirmed'),
        (3, 6, '2024-03-21 09:30:00', 'confirmed'),
        (3, 7, '2024-03-22 16:00:00', 'confirmed'),
        (4, 9, '2024-02-25 10:00:00', 'confirmed'),
        (5, 1, '2024-02-20 11:00:00', 'waitlisted'),
        (5, 10, '2024-02-22 08:45:00', 'confirmed'),
        (6, 3, '2024-03-10 07:30:00', 'confirmed'),
        (6, 9, '2024-03-12 13:00:00', 'confirmed'),
        (7, 2, '2024-03-28 09:00:00', 'confirmed'),
        (8, 5, '2024-04-15 10:00:00', 'confirmed'),
    ]
    cursor.executemany(
        "INSERT INTO registrations (event_id, participant_id, registered_at, status) VALUES (?,?,?,?)",
        registrations
    )

    conn.commit()
    conn.close()


# --- CRUD operations ---

def get_all_events(search=None, category=None, date_from=None, date_to=None):
    conn = get_connection()
    query = '''
        SELECT e.*, v.name as venue_name, v.location as venue_location,
               (SELECT COUNT(*) FROM registrations r WHERE r.event_id = e.id AND r.status = 'confirmed') as registered_count
        FROM events e
        LEFT JOIN venues v ON e.venue_id = v.id
        WHERE 1=1
    '''
    params = []

    if search:
        query += " AND (e.title LIKE ? OR e.description LIKE ? OR e.organizer LIKE ?)"
        s = f"%{search}%"
        params.extend([s, s, s])
    if category:
        query += " AND e.category = ?"
        params.append(category)
    if date_from:
        query += " AND e.event_date >= ?"
        params.append(date_from)
    if date_to:
        query += " AND e.event_date <= ?"
        params.append(date_to)

    query += " ORDER BY e.event_date ASC"
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return rows


def get_event_by_id(event_id):
    conn = get_connection()
    row = conn.execute('''
        SELECT e.*, v.name as venue_name, v.location as venue_location, v.capacity as venue_capacity
        FROM events e
        LEFT JOIN venues v ON e.venue_id = v.id
        WHERE e.id = ?
    ''', (event_id,)).fetchone()
    conn.close()
    return row


def create_event(data):
    conn = get_connection()
    cursor = conn.execute('''
        INSERT INTO events (title, description, event_date, start_time, end_time,
                           venue_id, organizer, category, max_participants)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (data['title'], data.get('description', ''), data['event_date'],
          data['start_time'], data['end_time'], data['venue_id'],
          data['organizer'], data.get('category', 'general'),
          data.get('max_participants', 100)))
    conn.commit()
    event_id = cursor.lastrowid
    conn.close()
    return event_id


def update_event(event_id, data):
    conn = get_connection()
    conn.execute('''
        UPDATE events SET title=?, description=?, event_date=?, start_time=?,
               end_time=?, venue_id=?, organizer=?, category=?, max_participants=?
        WHERE id=?
    ''', (data['title'], data.get('description', ''), data['event_date'],
          data['start_time'], data['end_time'], data['venue_id'],
          data['organizer'], data.get('category', 'general'),
          data.get('max_participants', 100), event_id))
    conn.commit()
    conn.close()


def delete_event(event_id):
    conn = get_connection()
    conn.execute("DELETE FROM registrations WHERE event_id = ?", (event_id,))
    conn.execute("DELETE FROM events WHERE id = ?", (event_id,))
    conn.commit()
    conn.close()


def get_all_venues():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM venues ORDER BY name").fetchall()
    conn.close()
    return rows


def get_venue_by_id(venue_id):
    conn = get_connection()
    row = conn.execute("SELECT * FROM venues WHERE id = ?", (venue_id,)).fetchone()
    conn.close()
    return row


def create_venue(data):
    conn = get_connection()
    cursor = conn.execute('''
        INSERT INTO venues (name, location, capacity, has_projector, has_ac)
        VALUES (?, ?, ?, ?, ?)
    ''', (data['name'], data['location'], data['capacity'],
          data.get('has_projector', 0), data.get('has_ac', 0)))
    conn.commit()
    vid = cursor.lastrowid
    conn.close()
    return vid


def get_event_registrations(event_id):
    conn = get_connection()
    rows = conn.execute('''
        SELECT p.*, r.registered_at, r.status
        FROM registrations r
        JOIN participants p ON r.participant_id = p.id
        WHERE r.event_id = ?
        ORDER BY r.registered_at
    ''', (event_id,)).fetchall()
    conn.close()
    return rows


def register_participant(event_id, participant_data):
    conn = get_connection()

    existing = conn.execute(
        "SELECT id FROM participants WHERE email = ?",
        (participant_data['email'],)
    ).fetchone()

    if existing:
        pid = existing['id']
    else:
        cursor = conn.execute('''
            INSERT INTO participants (name, email, phone, department, role)
            VALUES (?, ?, ?, ?, ?)
        ''', (participant_data['name'], participant_data['email'],
              participant_data.get('phone', ''), participant_data.get('department', ''),
              participant_data.get('role', 'attendee')))
        pid = cursor.lastrowid

    event = conn.execute("SELECT max_participants FROM events WHERE id = ?", (event_id,)).fetchone()
    reg_count = conn.execute(
        "SELECT COUNT(*) as cnt FROM registrations WHERE event_id = ? AND status = 'confirmed'",
        (event_id,)
    ).fetchone()['cnt']

    status = 'confirmed' if reg_count < event['max_participants'] else 'waitlisted'

    try:
        conn.execute('''
            INSERT INTO registrations (event_id, participant_id, status)
            VALUES (?, ?, ?)
        ''', (event_id, pid, status))
        conn.commit()
    except sqlite3.IntegrityError:
        conn.close()
        return None, "Already registered for this event"

    conn.close()
    return pid, status


def cancel_registration(event_id, participant_id):
    conn = get_connection()
    conn.execute('''
        DELETE FROM registrations WHERE event_id = ? AND participant_id = ?
    ''', (event_id, participant_id))
    conn.commit()
    conn.close()


def get_summary_report():
    conn = get_connection()
    report = {}

    report['total_events'] = conn.execute("SELECT COUNT(*) FROM events").fetchone()[0]
    report['total_participants'] = conn.execute("SELECT COUNT(*) FROM participants").fetchone()[0]
    report['total_registrations'] = conn.execute(
        "SELECT COUNT(*) FROM registrations WHERE status = 'confirmed'"
    ).fetchone()[0]
    report['total_venues'] = conn.execute("SELECT COUNT(*) FROM venues").fetchone()[0]

    report['events_by_category'] = conn.execute('''
        SELECT category, COUNT(*) as count FROM events GROUP BY category ORDER BY count DESC
    ''').fetchall()

    report['top_events'] = conn.execute('''
        SELECT e.title, COUNT(r.id) as reg_count
        FROM events e
        LEFT JOIN registrations r ON e.id = r.event_id AND r.status = 'confirmed'
        GROUP BY e.id
        ORDER BY reg_count DESC
        LIMIT 5
    ''').fetchall()

    report['venue_usage'] = conn.execute('''
        SELECT v.name, COUNT(e.id) as event_count
        FROM venues v
        LEFT JOIN events e ON v.id = e.venue_id
        GROUP BY v.id
        ORDER BY event_count DESC
    ''').fetchall()

    report['registrations_by_dept'] = conn.execute('''
        SELECT p.department, COUNT(r.id) as count
        FROM participants p
        JOIN registrations r ON p.id = r.participant_id
        WHERE r.status = 'confirmed'
        GROUP BY p.department
        ORDER BY count DESC
    ''').fetchall()

    conn.close()
    return report


def check_venue_conflict(venue_id, event_date, start_time, end_time, exclude_event_id=None):
    conn = get_connection()
    query = '''
        SELECT id, title FROM events
        WHERE venue_id = ? AND event_date = ?
        AND NOT (end_time <= ? OR start_time >= ?)
    '''
    params = [venue_id, event_date, start_time, end_time]

    if exclude_event_id:
        query += " AND id != ?"
        params.append(exclude_event_id)

    conflicts = conn.execute(query, params).fetchall()
    conn.close()
    return conflicts
