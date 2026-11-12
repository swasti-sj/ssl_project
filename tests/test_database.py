import os
import sys
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import database as db


@pytest.fixture(autouse=True)
def setup_test_db(tmp_path):
    db.DB_PATH = str(tmp_path / 'test_events.db')
    db.init_db()
    db.seed_data()
    yield


class TestVenues:
    def test_seed_venues_loaded(self):
        venues = db.get_all_venues()
        assert len(venues) == 6

    def test_create_venue(self):
        data = {
            'name': 'Test Hall',
            'location': 'Block Z',
            'capacity': 200,
            'has_projector': 1,
            'has_ac': 0
        }
        vid = db.create_venue(data)
        assert vid is not None
        venue = db.get_venue_by_id(vid)
        assert venue['name'] == 'Test Hall'
        assert venue['capacity'] == 200

    def test_get_venue_by_id(self):
        venue = db.get_venue_by_id(1)
        assert venue is not None
        assert venue['name'] == 'Main Auditorium'


class TestEvents:
    def test_seed_events_loaded(self):
        events = db.get_all_events()
        assert len(events) == 8

    def test_create_event(self):
        data = {
            'title': 'New Workshop',
            'description': 'Test workshop desc',
            'event_date': '2024-06-15',
            'start_time': '10:00',
            'end_time': '12:00',
            'venue_id': 1,
            'organizer': 'Test Org',
            'category': 'workshop',
            'max_participants': 50
        }
        eid = db.create_event(data)
        event = db.get_event_by_id(eid)
        assert event['title'] == 'New Workshop'
        assert event['organizer'] == 'Test Org'

    def test_update_event(self):
        data = {
            'title': 'Updated Title',
            'description': 'Updated desc',
            'event_date': '2024-06-20',
            'start_time': '11:00',
            'end_time': '13:00',
            'venue_id': 2,
            'organizer': 'Updated Org',
            'category': 'lecture',
            'max_participants': 80
        }
        db.update_event(1, data)
        event = db.get_event_by_id(1)
        assert event['title'] == 'Updated Title'

    def test_delete_event(self):
        db.delete_event(1)
        event = db.get_event_by_id(1)
        assert event is None

    def test_search_events(self):
        results = db.get_all_events(search='Tech Fest')
        assert len(results) >= 1
        assert 'Tech Fest' in results[0]['title']

    def test_filter_by_category(self):
        results = db.get_all_events(category='technical')
        for r in results:
            assert r['category'] == 'technical'

    def test_filter_by_date_range(self):
        results = db.get_all_events(date_from='2024-03-01', date_to='2024-03-31')
        for r in results:
            assert '2024-03' in r['event_date']


class TestRegistrations:
    def test_register_new_participant(self):
        participant = {
            'name': 'Test User',
            'email': 'test@example.com',
            'phone': '1234567890',
            'department': 'CSE'
        }
        pid, status = db.register_participant(2, participant)
        assert pid is not None
        assert status == 'confirmed'

    def test_duplicate_registration(self):
        participant = {
            'name': 'Rahul Sharma',
            'email': 'rahul.s@college.edu',
        }
        pid, status = db.register_participant(1, participant)
        assert pid is None
        assert 'Already registered' in status

    def test_get_event_registrations(self):
        regs = db.get_event_registrations(1)
        assert len(regs) >= 1

    def test_cancel_registration(self):
        regs_before = db.get_event_registrations(1)
        count_before = len(regs_before)
        if count_before > 0:
            db.cancel_registration(1, regs_before[0]['id'])
            regs_after = db.get_event_registrations(1)
            assert len(regs_after) == count_before - 1


class TestVenueConflict:
    def test_detect_conflict(self):
        conflicts = db.check_venue_conflict(1, '2024-03-15', '08:00', '19:00')
        assert len(conflicts) >= 1

    def test_no_conflict_different_date(self):
        conflicts = db.check_venue_conflict(1, '2024-12-25', '09:00', '17:00')
        assert len(conflicts) == 0

    def test_no_conflict_different_time(self):
        conflicts = db.check_venue_conflict(1, '2024-03-15', '19:00', '21:00')
        assert len(conflicts) == 0


class TestReports:
    def test_summary_report(self):
        report = db.get_summary_report()
        assert report['total_events'] == 8
        assert report['total_venues'] == 6
        assert report['total_participants'] > 0
        assert len(report['events_by_category']) > 0
        assert len(report['top_events']) > 0
