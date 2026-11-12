import os
import sys
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import database as db
from app import app


@pytest.fixture(autouse=True)
def setup_test_db(tmp_path):
    db.DB_PATH = str(tmp_path / 'test_events.db')
    db.init_db()
    db.seed_data()
    yield


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


class TestRoutes:
    def test_home_page(self, client):
        response = client.get('/')
        assert response.status_code == 200
        assert b'Campus Event' in response.data

    def test_events_page(self, client):
        response = client.get('/events')
        assert response.status_code == 200

    def test_events_search(self, client):
        response = client.get('/events?search=Tech')
        assert response.status_code == 200

    def test_events_filter_category(self, client):
        response = client.get('/events?category=technical')
        assert response.status_code == 200

    def test_event_detail(self, client):
        response = client.get('/events/1')
        assert response.status_code == 200

    def test_event_not_found(self, client):
        response = client.get('/events/9999')
        assert response.status_code == 302

    def test_register_page(self, client):
        response = client.get('/events/1/register')
        assert response.status_code == 200

    def test_register_submit(self, client):
        response = client.post('/events/2/register', data={
            'name': 'New Person',
            'email': 'new.person@test.com',
            'phone': '5551234567',
            'department': 'CSE'
        })
        assert response.status_code == 302

    def test_admin_panel(self, client):
        response = client.get('/admin')
        assert response.status_code == 200

    def test_create_event_page(self, client):
        response = client.get('/admin/events/new')
        assert response.status_code == 200

    def test_create_event_submit(self, client):
        response = client.post('/admin/events/new', data={
            'title': 'Test Event',
            'description': 'A test event',
            'event_date': '2024-12-01',
            'start_time': '10:00',
            'end_time': '12:00',
            'venue_id': '3',
            'organizer': 'Test Person',
            'category': 'general',
            'max_participants': '50'
        })
        assert response.status_code == 302

    def test_reports_page(self, client):
        response = client.get('/reports')
        assert response.status_code == 200
        assert b'Total Events' in response.data

    def test_api_events(self, client):
        response = client.get('/api/events')
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)

    def test_api_events_search(self, client):
        response = client.get('/api/events?search=Tech')
        assert response.status_code == 200

    def test_delete_event(self, client):
        response = client.post('/admin/events/1/delete')
        assert response.status_code == 302

    def test_create_venue_page(self, client):
        response = client.get('/admin/venues/new')
        assert response.status_code == 200

    def test_create_venue_submit(self, client):
        response = client.post('/admin/venues/new', data={
            'name': 'New Lab',
            'location': 'Block E',
            'capacity': '40',
            'has_projector': '1'
        })
        assert response.status_code == 302
