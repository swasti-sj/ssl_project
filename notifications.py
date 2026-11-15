from datetime import datetime

import database as db


def generate_registration_email(event_id, participant_name, participant_email, status):
    """Generate registration confirmation email content."""
    event = db.get_event_by_id(event_id)
    if not event:
        return None

    if status == 'confirmed':
        subject = f"Registration Confirmed - {event['title']}"
        body = f"""Dear {participant_name},

Your registration for the following event has been confirmed:

Event: {event['title']}
Date: {event['event_date']}
Time: {event['start_time']} - {event['end_time']}
Venue: {event['venue_name']} ({event['venue_location']})
Organizer: {event['organizer']}

Please arrive 10 minutes before the start time.

Regards,
Campus Events Team"""
    else:
        subject = f"Waitlisted - {event['title']}"
        body = f"""Dear {participant_name},

You have been added to the waitlist for:

Event: {event['title']}
Date: {event['event_date']}
Time: {event['start_time']} - {event['end_time']}

The event is currently full. You will be notified if a spot opens up.

Regards,
Campus Events Team"""

    return {
        'to': participant_email,
        'subject': subject,
        'body': body,
        'generated_at': datetime.now().isoformat()
    }


def generate_cancellation_email(event_id, participant_name, participant_email):
    """Generate cancellation confirmation email."""
    event = db.get_event_by_id(event_id)
    if not event:
        return None

    subject = f"Registration Cancelled - {event['title']}"
    body = f"""Dear {participant_name},

Your registration for "{event['title']}" on {event['event_date']} has been cancelled.

If this was a mistake, you can register again through the event page.

Regards,
Campus Events Team"""

    return {
        'to': participant_email,
        'subject': subject,
        'body': body,
        'generated_at': datetime.now().isoformat()
    }


def generate_event_reminder(event_id):
    """Generate reminder emails for all confirmed participants of an event."""
    event = db.get_event_by_id(event_id)
    if not event:
        return []

    registrations = db.get_event_registrations(event_id)
    reminders = []

    for reg in registrations:
        if reg['status'] != 'confirmed':
            continue

        email = {
            'to': reg['email'],
            'subject': f"Reminder: {event['title']} - {event['event_date']}",
            'body': f"""Dear {reg['name']},

This is a reminder that you are registered for:

Event: {event['title']}
Date: {event['event_date']}
Time: {event['start_time']} - {event['end_time']}
Venue: {event['venue_name']}

See you there!

Regards,
Campus Events Team""",
            'generated_at': datetime.now().isoformat()
        }
        reminders.append(email)

    return reminders


if __name__ == '__main__':
    db.init_db()
    db.seed_data()

    print("=== Sample Registration Email ===")
    email = generate_registration_email(1, 'Test User', 'test@college.edu', 'confirmed')
    if email:
        print(f"To: {email['to']}")
        print(f"Subject: {email['subject']}")
        print(f"\n{email['body']}")

    print("\n=== Sample Reminder Emails ===")
    reminders = generate_event_reminder(1)
    print(f"Generated {len(reminders)} reminder(s) for event 1")
    if reminders:
        print(f"First reminder to: {reminders[0]['to']}")
