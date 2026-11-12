import cProfile
import pstats
import io
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import database as db


def profile_database_operations():
    """Profile the core database operations to find bottlenecks."""

    db.DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'profile_test.db')

    if os.path.exists(db.DB_PATH):
        os.remove(db.DB_PATH)

    db.init_db()
    db.seed_data()

    profiler = cProfile.Profile()
    profiler.enable()

    # simulate typical usage patterns
    for _ in range(50):
        db.get_all_events()

    for _ in range(50):
        db.get_all_events(search='Tech')

    for _ in range(30):
        db.get_all_events(category='technical')

    for _ in range(30):
        db.get_all_events(date_from='2024-01-01', date_to='2024-06-30')

    for i in range(1, 9):
        for _ in range(20):
            db.get_event_by_id(i)

    for _ in range(40):
        db.get_all_venues()

    for _ in range(20):
        db.get_summary_report()

    for i in range(1, 9):
        for _ in range(10):
            db.get_event_registrations(i)

    for _ in range(20):
        db.check_venue_conflict(1, '2024-03-15', '09:00', '18:00')

    profiler.disable()

    # print results
    stream = io.StringIO()
    stats = pstats.Stats(profiler, stream=stream)
    stats.strip_dirs()
    stats.sort_stats('cumulative')

    print("=" * 70)
    print("  PROFILING RESULTS - Campus Event Management Platform")
    print("=" * 70)
    print()

    print("Top 20 functions by cumulative time:")
    print("-" * 70)
    stats.print_stats(20)
    print(stream.getvalue())

    # also time individual operations
    print("\n" + "=" * 70)
    print("  INDIVIDUAL OPERATION BENCHMARKS")
    print("=" * 70)

    benchmarks = [
        ("get_all_events()", lambda: db.get_all_events()),
        ("get_all_events(search)", lambda: db.get_all_events(search='Tech')),
        ("get_all_events(category)", lambda: db.get_all_events(category='technical')),
        ("get_event_by_id(1)", lambda: db.get_event_by_id(1)),
        ("get_all_venues()", lambda: db.get_all_venues()),
        ("get_summary_report()", lambda: db.get_summary_report()),
        ("get_event_registrations(1)", lambda: db.get_event_registrations(1)),
        ("check_venue_conflict()", lambda: db.check_venue_conflict(1, '2024-03-15', '09:00', '18:00')),
    ]

    for name, func in benchmarks:
        times = []
        for _ in range(100):
            start = time.perf_counter()
            func()
            end = time.perf_counter()
            times.append(end - start)

        avg_ms = (sum(times) / len(times)) * 1000
        min_ms = min(times) * 1000
        max_ms = max(times) * 1000
        print(f"  {name:35s}  avg={avg_ms:.3f}ms  min={min_ms:.3f}ms  max={max_ms:.3f}ms")

    # cleanup
    if os.path.exists(db.DB_PATH):
        os.remove(db.DB_PATH)

    print("\n[Done] Profiling complete.")


if __name__ == '__main__':
    profile_database_operations()
