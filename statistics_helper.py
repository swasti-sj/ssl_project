import database as db
from collections import Counter


def get_event_fill_rates():
    """Calculate fill rate percentage for each event."""
    events = db.get_all_events()
    fill_rates = []
    for event in events:
        registered = event['registered_count']
        max_cap = event['max_participants']
        rate = (registered / max_cap * 100) if max_cap > 0 else 0
        fill_rates.append({
            'title': event['title'],
            'registered': registered,
            'max': max_cap,
            'fill_rate': round(rate, 1),
            'status': 'Full' if rate >= 100 else ('Almost Full' if rate >= 80 else 'Open')
        })
    return sorted(fill_rates, key=lambda x: x['fill_rate'], reverse=True)


def get_popular_time_slots():
    """Find the most popular event time slots."""
    events = db.get_all_events()
    time_slots = Counter()
    for event in events:
        slot = f"{event['start_time']}-{event['end_time']}"
        time_slots[slot] += 1
    return time_slots.most_common()


def get_organizer_stats():
    """Get statistics grouped by organizer."""
    events = db.get_all_events()
    organizer_data = {}
    for event in events:
        org = event['organizer']
        if org not in organizer_data:
            organizer_data[org] = {'events': 0, 'total_registrations': 0}
        organizer_data[org]['events'] += 1
        organizer_data[org]['total_registrations'] += event['registered_count']
    return dict(sorted(organizer_data.items(), key=lambda x: x[1]['events'], reverse=True))


def get_venue_utilization():
    """Calculate how well each venue is being utilized."""
    venues = db.get_all_venues()
    events = db.get_all_events()

    venue_events = {}
    for event in events:
        vid = event['venue_id']
        if vid not in venue_events:
            venue_events[vid] = 0
        venue_events[vid] += 1

    utilization = []
    for venue in venues:
        event_count = venue_events.get(venue['id'], 0)
        utilization.append({
            'name': venue['name'],
            'capacity': venue['capacity'],
            'events_hosted': event_count,
            'has_projector': bool(venue['has_projector']),
            'has_ac': bool(venue['has_ac'])
        })
    return sorted(utilization, key=lambda x: x['events_hosted'], reverse=True)


def print_dashboard():
    """Print a text-based statistics dashboard."""
    print("=" * 60)
    print("  EVENT MANAGEMENT - STATISTICS DASHBOARD")
    print("=" * 60)

    print("\n--- Event Fill Rates ---")
    for item in get_event_fill_rates():
        bar_len = int(item['fill_rate'] / 5)
        bar = '#' * bar_len + '-' * (20 - bar_len)
        print(f"  {item['title'][:30]:30s} [{bar}] {item['fill_rate']:5.1f}% ({item['status']})")

    print("\n--- Popular Time Slots ---")
    for slot, count in get_popular_time_slots():
        print(f"  {slot:15s} : {count} event(s)")

    print("\n--- Organizer Stats ---")
    for org, stats in get_organizer_stats().items():
        print(f"  {org:25s} : {stats['events']} events, {stats['total_registrations']} registrations")

    print("\n--- Venue Utilization ---")
    for v in get_venue_utilization():
        features = []
        if v['has_projector']:
            features.append('Projector')
        if v['has_ac']:
            features.append('AC')
        feat_str = ', '.join(features) if features else 'Basic'
        print(f"  {v['name']:25s} : {v['events_hosted']} events (cap: {v['capacity']}, {feat_str})")


if __name__ == '__main__':
    db.init_db()
    db.seed_data()
    print_dashboard()