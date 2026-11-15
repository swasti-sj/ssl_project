import csv
import os
import sys
from datetime import datetime

import database as db


def export_event_registrations(event_id, output_dir='exports'):
    """Export all registrations for an event to a CSV file."""
    event = db.get_event_by_id(event_id)
    if not event:
        print(f"Event with ID {event_id} not found.")
        return None

    registrations = db.get_event_registrations(event_id)

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    safe_title = event['title'].replace(' ', '_').replace('/', '-')
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"{output_dir}/{safe_title}_{timestamp}.csv"

    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Name', 'Email', 'Phone', 'Department', 'Role', 'Registered At', 'Status'])

        for reg in registrations:
            writer.writerow([
                reg['name'],
                reg['email'],
                reg['phone'],
                reg['department'],
                reg['role'],
                reg['registered_at'],
                reg['status']
            ])

    print(f"Exported {len(registrations)} registrations to {filename}")
    return filename


def export_all_events_summary(output_dir='exports'):
    """Export a summary of all events to CSV."""
    events = db.get_all_events()

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"{output_dir}/all_events_summary_{timestamp}.csv"

    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['ID', 'Title', 'Date', 'Time', 'Venue', 'Category', 'Organizer', 'Registered', 'Max'])

        for event in events:
            writer.writerow([
                event['id'],
                event['title'],
                event['event_date'],
                f"{event['start_time']}-{event['end_time']}",
                event['venue_name'] or 'TBD',
                event['category'],
                event['organizer'],
                event['registered_count'],
                event['max_participants']
            ])

    print(f"Exported {len(events)} events to {filename}")
    return filename


if __name__ == '__main__':
    db.init_db()
    db.seed_data()

    if len(sys.argv) > 1:
        event_id = int(sys.argv[1])
        export_event_registrations(event_id)
    else:
        export_all_events_summary()
        print("\nUsage: python export_csv.py [event_id]")
        print("  No args = export all events summary")
        print("  With event_id = export that event's registrations")
