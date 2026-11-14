import re
from datetime import datetime


class ValidationError(Exception):
    def __init__(self, field, message):
        self.field = field
        self.message = message
        super().__init__(f"{field}: {message}")


def validate_email(email):
    """Check if email format is valid."""
    if not email or not email.strip():
        raise ValidationError('email', 'Email is required')
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email.strip()):
        raise ValidationError('email', 'Invalid email format')
    return email.strip()


def validate_phone(phone):
    """Check if phone number is valid (optional field)."""
    if not phone or not phone.strip():
        return ''
    cleaned = re.sub(r'[\s\-\(\)]', '', phone)
    if not re.match(r'^\+?\d{10,13}$', cleaned):
        raise ValidationError('phone', 'Phone must be 10-13 digits')
    return cleaned


def validate_event_data(data):
    """Validate all fields of an event submission."""
    errors = []

    if not data.get('title', '').strip():
        errors.append(ValidationError('title', 'Event title is required'))
    elif len(data['title'].strip()) > 200:
        errors.append(ValidationError('title', 'Title must be under 200 characters'))

    if not data.get('event_date', '').strip():
        errors.append(ValidationError('event_date', 'Event date is required'))
    else:
        try:
            event_date = datetime.strptime(data['event_date'], '%Y-%m-%d')
        except ValueError:
            errors.append(ValidationError('event_date', 'Date must be in YYYY-MM-DD format'))

    if not data.get('start_time', '').strip():
        errors.append(ValidationError('start_time', 'Start time is required'))
    if not data.get('end_time', '').strip():
        errors.append(ValidationError('end_time', 'End time is required'))

    if data.get('start_time') and data.get('end_time'):
        if data['start_time'] >= data['end_time']:
            errors.append(ValidationError('end_time', 'End time must be after start time'))

    if not data.get('organizer', '').strip():
        errors.append(ValidationError('organizer', 'Organizer is required'))

    max_p = data.get('max_participants')
    if max_p is not None:
        try:
            max_p = int(max_p)
            if max_p < 1:
                errors.append(ValidationError('max_participants', 'Must be at least 1'))
            elif max_p > 10000:
                errors.append(ValidationError('max_participants', 'Must be under 10000'))
        except (ValueError, TypeError):
            errors.append(ValidationError('max_participants', 'Must be a number'))

    valid_categories = ['general', 'technical', 'cultural', 'workshop', 'academic', 'lecture', 'sports']
    if data.get('category') and data['category'] not in valid_categories:
        errors.append(ValidationError('category', f'Must be one of: {", ".join(valid_categories)}'))

    return errors


def validate_registration_data(data):
    """Validate participant registration fields."""
    errors = []

    if not data.get('name', '').strip():
        errors.append(ValidationError('name', 'Name is required'))
    elif len(data['name'].strip()) > 100:
        errors.append(ValidationError('name', 'Name must be under 100 characters'))

    try:
        validate_email(data.get('email', ''))
    except ValidationError as e:
        errors.append(e)

    if data.get('phone'):
        try:
            validate_phone(data['phone'])
        except ValidationError as e:
            errors.append(e)

    return errors


def validate_venue_data(data):
    """Validate venue creation fields."""
    errors = []

    if not data.get('name', '').strip():
        errors.append(ValidationError('name', 'Venue name is required'))

    if not data.get('location', '').strip():
        errors.append(ValidationError('location', 'Location is required'))

    try:
        cap = int(data.get('capacity', 0))
        if cap < 1:
            errors.append(ValidationError('capacity', 'Capacity must be at least 1'))
    except (ValueError, TypeError):
        errors.append(ValidationError('capacity', 'Capacity must be a number'))

    return errors


if __name__ == '__main__':
    print("=== Validation Module Tests ===\n")

    print("Testing email validation:")
    for email in ['test@example.com', 'bad-email', '', 'user@domain.co.in']:
        try:
            result = validate_email(email)
            print(f"  '{email}' -> OK ({result})")
        except ValidationError as e:
            print(f"  '{email}' -> FAIL ({e.message})")

    print("\nTesting phone validation:")
    for phone in ['9876543210', '123', '+919876543210', '']:
        try:
            result = validate_phone(phone)
            print(f"  '{phone}' -> OK ({result})")
        except ValidationError as e:
            print(f"  '{phone}' -> FAIL ({e.message})")

    print("\nTesting event data validation:")
    bad_event = {'title': '', 'event_date': 'not-a-date', 'start_time': '14:00', 'end_time': '10:00'}
    errors = validate_event_data(bad_event)
    for e in errors:
        print(f"  {e.field}: {e.message}")
