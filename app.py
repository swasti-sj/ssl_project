from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import database as db

app = Flask(__name__)
app.secret_key = 'campus-event-mgmt-secret-key-2024'


@app.before_request
def setup():
    db.init_db()
    db.seed_data()


# ---- Home ----

@app.route('/')
def index():
    events = db.get_all_events()
    report = db.get_summary_report()
    return render_template('index.html', events=events, report=report)


# ---- Events ----

@app.route('/events')
def events_list():
    search = request.args.get('search', '')
    category = request.args.get('category', '')
    date_from = request.args.get('date_from', '')
    date_to = request.args.get('date_to', '')

    events = db.get_all_events(
        search=search or None,
        category=category or None,
        date_from=date_from or None,
        date_to=date_to or None
    )
    return render_template('events.html', events=events, search=search,
                           category=category, date_from=date_from, date_to=date_to)


@app.route('/events/<int:event_id>')
def event_detail(event_id):
    event = db.get_event_by_id(event_id)
    if not event:
        flash('Event not found', 'error')
        return redirect(url_for('events_list'))
    registrations = db.get_event_registrations(event_id)
    return render_template('event_detail.html', event=event, registrations=registrations)


@app.route('/events/<int:event_id>/register', methods=['GET', 'POST'])
def register_for_event(event_id):
    event = db.get_event_by_id(event_id)
    if not event:
        flash('Event not found', 'error')
        return redirect(url_for('events_list'))

    if request.method == 'POST':
        participant_data = {
            'name': request.form['name'],
            'email': request.form['email'],
            'phone': request.form.get('phone', ''),
            'department': request.form.get('department', ''),
            'role': 'attendee'
        }

        pid, status = db.register_participant(event_id, participant_data)
        if pid is None:
            flash(status, 'error')
        elif status == 'waitlisted':
            flash('Event is full. You have been added to the waitlist.', 'warning')
        else:
            flash('Registration successful!', 'success')
        return redirect(url_for('event_detail', event_id=event_id))

    return render_template('register.html', event=event)


@app.route('/events/<int:event_id>/cancel/<int:participant_id>', methods=['POST'])
def cancel_registration(event_id, participant_id):
    db.cancel_registration(event_id, participant_id)
    flash('Registration cancelled.', 'info')
    return redirect(url_for('event_detail', event_id=event_id))


# ---- Admin ----

@app.route('/admin')
def admin_panel():
    events = db.get_all_events()
    venues = db.get_all_venues()
    return render_template('admin.html', events=events, venues=venues)


@app.route('/admin/events/new', methods=['GET', 'POST'])
def create_event():
    venues = db.get_all_venues()
    if request.method == 'POST':
        data = {
            'title': request.form['title'],
            'description': request.form.get('description', ''),
            'event_date': request.form['event_date'],
            'start_time': request.form['start_time'],
            'end_time': request.form['end_time'],
            'venue_id': int(request.form['venue_id']),
            'organizer': request.form['organizer'],
            'category': request.form.get('category', 'general'),
            'max_participants': int(request.form.get('max_participants', 100))
        }

        conflicts = db.check_venue_conflict(
            data['venue_id'], data['event_date'],
            data['start_time'], data['end_time']
        )
        if conflicts:
            conflict_names = ', '.join([c['title'] for c in conflicts])
            flash(f'Venue conflict with: {conflict_names}', 'error')
            return render_template('event_form.html', venues=venues, data=data, editing=False)

        db.create_event(data)
        flash('Event created successfully!', 'success')
        return redirect(url_for('admin_panel'))

    return render_template('event_form.html', venues=venues, data={}, editing=False)


@app.route('/admin/events/<int:event_id>/edit', methods=['GET', 'POST'])
def edit_event(event_id):
    venues = db.get_all_venues()
    event = db.get_event_by_id(event_id)
    if not event:
        flash('Event not found', 'error')
        return redirect(url_for('admin_panel'))

    if request.method == 'POST':
        data = {
            'title': request.form['title'],
            'description': request.form.get('description', ''),
            'event_date': request.form['event_date'],
            'start_time': request.form['start_time'],
            'end_time': request.form['end_time'],
            'venue_id': int(request.form['venue_id']),
            'organizer': request.form['organizer'],
            'category': request.form.get('category', 'general'),
            'max_participants': int(request.form.get('max_participants', 100))
        }

        conflicts = db.check_venue_conflict(
            data['venue_id'], data['event_date'],
            data['start_time'], data['end_time'],
            exclude_event_id=event_id
        )
        if conflicts:
            conflict_names = ', '.join([c['title'] for c in conflicts])
            flash(f'Venue conflict with: {conflict_names}', 'error')
            return render_template('event_form.html', venues=venues, data=data, editing=True, event_id=event_id)

        db.update_event(event_id, data)
        flash('Event updated.', 'success')
        return redirect(url_for('admin_panel'))

    return render_template('event_form.html', venues=venues, data=dict(event), editing=True, event_id=event_id)


@app.route('/admin/events/<int:event_id>/delete', methods=['POST'])
def delete_event(event_id):
    db.delete_event(event_id)
    flash('Event deleted.', 'info')
    return redirect(url_for('admin_panel'))


@app.route('/admin/venues/new', methods=['GET', 'POST'])
def create_venue():
    if request.method == 'POST':
        data = {
            'name': request.form['name'],
            'location': request.form['location'],
            'capacity': int(request.form['capacity']),
            'has_projector': 1 if request.form.get('has_projector') else 0,
            'has_ac': 1 if request.form.get('has_ac') else 0,
        }
        db.create_venue(data)
        flash('Venue added successfully!', 'success')
        return redirect(url_for('admin_panel'))

    return render_template('venue_form.html')


# ---- Reports ----

@app.route('/reports')
def reports():
    report = db.get_summary_report()
    return render_template('reports.html', report=report)


# ---- API endpoints for search/filter ----

@app.route('/api/events')
def api_events():
    search = request.args.get('search', '')
    category = request.args.get('category', '')
    events = db.get_all_events(search=search or None, category=category or None)
    return jsonify([dict(e) for e in events])


if __name__ == '__main__':
    db.init_db()
    db.seed_data()
    app.run(debug=True, port=5000)
