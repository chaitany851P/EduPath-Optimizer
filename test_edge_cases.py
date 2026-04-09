"""
EduPath Optimizer — Edge Case System Test Suite
================================================
Tests against the /calculate-strategy endpoint in main2.py
Run: pytest test_edge_cases.py -v

Requirements:
  pip install pytest httpx fastapi

Start server first:
  uvicorn main2:app --reload --port 8000
"""

import pytest
from httpx import AsyncClient
from datetime import date, timedelta
import asyncio

BASE_URL = "http://127.0.0.1:8000"

# ──────────────────────────────────────────────────────────────
# HELPERS
# ──────────────────────────────────────────────────────────────

def payload(
    start="2026-03-01",
    end="2026-03-31",
    attended=5,
    target=75.0,
    track="Data Science",
    country="IN"
):
    return {
        "start_date": start,
        "end_date": end,
        "current_attended": attended,
        "target_percentage": target,
        "career_track": track,
        "country_code": country
    }

async def post_strategy(client, data):
    return await client.post("/calculate-strategy", json=data)

# ──────────────────────────────────────────────────────────────
# GROUP 1 — BOUNDARY / MATH EDGE CASES
# ──────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_EC01_already_above_target():
    """
    EC-01: Student has already exceeded 75%.
    Expected: gap = 0, explanation says "Goal met".
    """
    async with AsyncClient(base_url=BASE_URL) as c:
        res = await post_strategy(c, payload(
            start="2026-03-01", end="2026-03-31",
            attended=50, target=75.0, track="Data Science"
        ))
    assert res.status_code == 200
    body = res.json()
    gap = body["attendance_math"]["gap_to_fill"]
    explanation = body["strategic_plan"]["logic_explanation"]
    assert gap == 0, f"EC-01 FAIL: gap should be 0, got {gap}"
    assert "Goal met" in explanation or "above" in explanation.lower(), \
        f"EC-01 FAIL: unexpected explanation: {explanation}"
    print(f"\n✅ EC-01 PASS | gap={gap}")


@pytest.mark.asyncio
async def test_EC02_impossible_target():
    """
    EC-02: Very short range (3 working days), 0 attended, target 90%.
    Need ceil(0.9 * 3) = 3 classes but only 3 remain — and future filter
    may reduce that. Tests counselor warning OR Goal met edge.
    Real impossible case: large range already passed, only 2 days left.
    """
    async with AsyncClient(base_url=BASE_URL) as c:
        # attended=0, only ~3 working days in range, target=90% → need 3, gap>future
        res = await post_strategy(c, payload(
            start="2026-03-18", end="2026-03-20",  # Wed–Fri = 3 days, all past
            attended=0, target=90.0, track="Data Science"
        ))
    assert res.status_code == 200
    body = res.json()
    explanation = body["strategic_plan"]["logic_explanation"]
    # Either impossible warning OR goal met (if 0 future days remain)
    assert any(kw in explanation for kw in ["impossible", "CRITICAL", "counselor", "Goal met", "goal"]), \
        f"EC-02 FAIL: unexpected explanation. Got: {explanation}"
    print(f"\n✅ EC-02 PASS | explanation: {explanation[:80]}")


@pytest.mark.asyncio
async def test_EC03_zero_attended():
    """
    EC-03: Student hasn't attended any class yet.
    Should return a valid positive gap.
    """
    async with AsyncClient(base_url=BASE_URL) as c:
        res = await post_strategy(c, payload(
            start="2026-02-10", end="2026-02-25",
            attended=0, target=60.0, track="IOT"
        ))
    assert res.status_code == 200
    body = res.json()
    gap = body["attendance_math"]["gap_to_fill"]
    assert gap > 0, f"EC-03 FAIL: gap should be >0 when attended=0, got {gap}"
    print(f"\n✅ EC-03 PASS | gap={gap}")


@pytest.mark.asyncio
async def test_EC04_target_exactly_75():
    """
    EC-04: Exact 75% target, border value.
    Should compute cleanly without crash.
    """
    async with AsyncClient(base_url=BASE_URL) as c:
        res = await post_strategy(c, payload(
            start="2026-03-01", end="2026-05-30",
            attended=20, target=75.0, track="Cyber Security"
        ))
    assert res.status_code == 200
    body = res.json()
    assert "gap_to_fill" in body["attendance_math"]
    print(f"\n✅ EC-04 PASS | gap={body['attendance_math']['gap_to_fill']}")


@pytest.mark.asyncio
async def test_EC05_target_100_percent():
    """
    EC-05: 100% target across April 2026.
    All available days must be returned.
    """
    async with AsyncClient(base_url=BASE_URL) as c:
        res = await post_strategy(c, payload(
            start="2026-04-01", end="2026-04-30",
            attended=0, target=100.0, track="IOT"
        ))
    assert res.status_code == 200
    body = res.json()
    total = body["meta_data"]["total_working_days"]
    gap = body["attendance_math"]["gap_to_fill"]
    # gap cannot exceed total
    assert gap <= total, f"EC-05 FAIL: gap ({gap}) > total working days ({total})"
    print(f"\n✅ EC-05 PASS | gap={gap}, total={total}")


@pytest.mark.asyncio
async def test_EC06_start_equals_end():
    """
    EC-06: Single day semester range.
    Only 1 possible working day — should not crash.
    """
    async with AsyncClient(base_url=BASE_URL) as c:
        res = await post_strategy(c, payload(
            start="2026-03-16", end="2026-03-16",  # Monday
            attended=0, target=75.0, track="Data Science"
        ))
    assert res.status_code == 200
    body = res.json()
    total = body["meta_data"]["total_working_days"]
    assert total in [0, 1], f"EC-06 FAIL: expected 0 or 1 working day, got {total}"
    print(f"\n✅ EC-06 PASS | working_days={total}")


@pytest.mark.asyncio
async def test_EC07_start_after_end():
    """
    EC-07: start_date > end_date.
    Should return 0 working days or a 422 validation error.
    """
    async with AsyncClient(base_url=BASE_URL) as c:
        res = await post_strategy(c, payload(
            start="2026-05-01", end="2026-03-01",
            attended=0, target=75.0, track="Data Science"
        ))
    # Accept either a clean 0-days result OR a validation error
    if res.status_code == 200:
        total = res.json()["meta_data"]["total_working_days"]
        assert total == 0, f"EC-07 FAIL: expected 0 working days, got {total}"
    else:
        assert res.status_code in [400, 422], f"EC-07 FAIL: got status {res.status_code}"
    print(f"\n✅ EC-07 PASS | status={res.status_code}")


# ──────────────────────────────────────────────────────────────
# GROUP 2 — TRACK / DATABASE EDGE CASES
# ──────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_EC08_invalid_career_track():
    """
    EC-08: Non-existent career track.
    Should return 404 with detail "Track not found".
    """
    async with AsyncClient(base_url=BASE_URL) as c:
        res = await post_strategy(c, payload(
            track="QuantumPhysics"
        ))
    assert res.status_code == 404, f"EC-08 FAIL: expected 404, got {res.status_code}"
    assert "not found" in res.json()["detail"].lower()
    print(f"\n✅ EC-08 PASS | 404 returned correctly")


@pytest.mark.asyncio
async def test_EC09_all_four_tracks():
    """
    EC-09: Each seeded track should return 200 with valid structure.
    """
    tracks = ["Data Science", "Cyber Security", "IOT", "Computer Graphics"]
    async with AsyncClient(base_url=BASE_URL) as c:
        for track in tracks:
            res = await post_strategy(c, payload(
                start="2026-03-01", end="2026-03-31",
                attended=5, target=75.0, track=track
            ))
            assert res.status_code == 200, f"EC-09 FAIL on track '{track}': {res.status_code}"
            body = res.json()
            assert "strategic_plan" in body
            print(f"  ✓ Track '{track}' → gap={body['attendance_math']['gap_to_fill']}")
    print(f"\n✅ EC-09 PASS | all 4 tracks OK")


@pytest.mark.asyncio
async def test_EC10_career_track_case_sensitivity():
    """
    EC-10: Wrong case e.g. "data science" (lowercase).
    Should return 404 (DB is case-sensitive on name field).
    """
    async with AsyncClient(base_url=BASE_URL) as c:
        res = await post_strategy(c, payload(track="data science"))
    assert res.status_code == 404, \
        f"EC-10 FAIL: expected 404 for lowercase track, got {res.status_code}"
    print(f"\n✅ EC-10 PASS | case sensitivity enforced")


# ──────────────────────────────────────────────────────────────
# GROUP 3 — HOLIDAY / WEEKEND LOGIC
# ──────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_EC11_range_is_all_weekends():
    """
    EC-11: Date range covers only Saturday and Sunday.
    Working days must be 0.
    """
    # 2026-03-21 is Saturday, 2026-03-22 is Sunday
    async with AsyncClient(base_url=BASE_URL) as c:
        res = await post_strategy(c, payload(
            start="2026-03-21", end="2026-03-22",
            attended=0, target=75.0, track="Data Science"
        ))
    assert res.status_code == 200
    total = res.json()["meta_data"]["total_working_days"]
    assert total == 0, f"EC-11 FAIL: expected 0 working days for weekend, got {total}"
    print(f"\n✅ EC-11 PASS | weekend-only range → 0 working days")


@pytest.mark.asyncio
async def test_EC12_republic_day_excluded():
    """
    EC-12: 26th January (Republic Day) should not be counted as working day.
    Range: Jan 26–27 2026.
    """
    async with AsyncClient(base_url=BASE_URL) as c:
        res = await post_strategy(c, payload(
            start="2026-01-26", end="2026-01-27",
            attended=0, target=75.0, track="IOT"
        ))
    assert res.status_code == 200
    body = res.json()
    total = body["meta_data"]["total_working_days"]
    # Jan 26 = holiday, Jan 27 = Tuesday → max 1 working day
    assert total <= 1, f"EC-12 FAIL: Republic Day should be excluded, got {total} working days"
    print(f"\n✅ EC-12 PASS | Republic Day excluded, working_days={total}")


@pytest.mark.asyncio
async def test_EC13_independence_day_excluded():
    """
    EC-13: 15th August (Independence Day) excluded.
    """
    async with AsyncClient(base_url=BASE_URL) as c:
        res = await post_strategy(c, payload(
            start="2026-08-15", end="2026-08-15",
            attended=0, target=75.0, track="Data Science"
        ))
    assert res.status_code == 200
    total = res.json()["meta_data"]["total_working_days"]
    assert total == 0, f"EC-13 FAIL: Independence Day should be excluded, got {total}"
    print(f"\n✅ EC-13 PASS | Independence Day excluded correctly")


# ──────────────────────────────────────────────────────────────
# GROUP 4 — DATE FORMAT / RESPONSE STRUCTURE
# ──────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_EC14_dates_formatted_dd_mm_yyyy():
    """
    EC-14: All returned dates must be in DD-MM-YYYY format.
    Not YYYY-MM-DD.
    """
    async with AsyncClient(base_url=BASE_URL) as c:
        res = await post_strategy(c, payload(
            start="2026-03-01", end="2026-05-30",
            attended=5, target=75.0, track="Data Science"
        ))
    assert res.status_code == 200
    plan = res.json()["strategic_plan"]
    all_dates = plan["career_priority_dates"] + plan["buffer_attendance_dates"]
    for d in all_dates:
        parts = d.split("-")
        assert len(parts) == 3, f"EC-14 FAIL: date '{d}' not split into 3 parts"
        assert len(parts[0]) == 2 and len(parts[2]) == 4, \
            f"EC-14 FAIL: date '{d}' is not DD-MM-YYYY format"
    print(f"\n✅ EC-14 PASS | {len(all_dates)} dates all in DD-MM-YYYY format")


@pytest.mark.asyncio
async def test_EC15_response_structure_complete():
    """
    EC-15: Response must contain all 3 required top-level keys.
    """
    async with AsyncClient(base_url=BASE_URL) as c:
        res = await post_strategy(c, payload())
    assert res.status_code == 200
    body = res.json()
    required_keys = ["meta_data", "attendance_math", "strategic_plan"]
    for key in required_keys:
        assert key in body, f"EC-15 FAIL: missing key '{key}'"
    # Check nested keys
    assert "career_priority_dates" in body["strategic_plan"]
    assert "buffer_attendance_dates" in body["strategic_plan"]
    assert "logic_explanation" in body["strategic_plan"]
    print(f"\n✅ EC-15 PASS | response structure complete")


@pytest.mark.asyncio
async def test_EC16_no_past_dates_in_output():
    """
    EC-16: Returned dates must all be today or in the future.
    """
    today = date.today()
    async with AsyncClient(base_url=BASE_URL) as c:
        res = await post_strategy(c, payload(
            start="2025-01-01", end="2026-12-31",
            attended=10, target=75.0, track="Data Science"
        ))
    assert res.status_code == 200
    plan = res.json()["strategic_plan"]
    all_dates = plan["career_priority_dates"] + plan["buffer_attendance_dates"]
    for d_str in all_dates:
        day, month, year = map(int, d_str.split("-"))
        d = date(year, month, day)
        assert d >= today, f"EC-16 FAIL: past date '{d_str}' appeared in suggestions"
    print(f"\n✅ EC-16 PASS | {len(all_dates)} suggested dates all in future")


# ──────────────────────────────────────────────────────────────
# GROUP 5 — NEGATIVE / VALIDATION INPUTS
# ──────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_EC17_negative_attended_count():
    """
    EC-17: Negative attended count — Pydantic should reject with 422.
    """
    async with AsyncClient(base_url=BASE_URL) as c:
        res = await post_strategy(c, payload(attended=-5))
    assert res.status_code == 422, \
        f"EC-17 FAIL: expected 422 for negative attended, got {res.status_code}"
    print(f"\n✅ EC-17 PASS | negative attended rejected with 422")


@pytest.mark.asyncio
async def test_EC18_target_above_100():
    """
    EC-18: target_percentage > 100 — Pydantic should reject with 422.
    """
    async with AsyncClient(base_url=BASE_URL) as c:
        res = await post_strategy(c, payload(target=150.0))
    assert res.status_code == 422, \
        f"EC-18 FAIL: expected 422 for target>100, got {res.status_code}"
    print(f"\n✅ EC-18 PASS | target>100 rejected with 422")


@pytest.mark.asyncio
async def test_EC19_target_zero():
    """
    EC-19: target_percentage = 0.
    gap should be 0 (already at or above 0%).
    """
    async with AsyncClient(base_url=BASE_URL) as c:
        res = await post_strategy(c, payload(
            attended=0, target=0.0, track="Data Science"
        ))
    # Pydantic allows ge=0, so this may pass or fail depending on ge= constraint
    if res.status_code == 200:
        gap = res.json()["attendance_math"]["gap_to_fill"]
        assert gap == 0, f"EC-19 FAIL: gap={gap} for target=0%"
    else:
        assert res.status_code == 422
    print(f"\n✅ EC-19 PASS | target=0% handled, status={res.status_code}")


@pytest.mark.asyncio
async def test_EC20_missing_required_field():
    """
    EC-20: Omit required field 'start_date'.
    Should return 422 Unprocessable Entity.
    """
    async with AsyncClient(base_url=BASE_URL) as c:
        res = await c.post("/calculate-strategy", json={
            "end_date": "2026-03-31",
            "current_attended": 10,
            "career_track": "Data Science"
        })
    assert res.status_code == 422, \
        f"EC-20 FAIL: expected 422 for missing field, got {res.status_code}"
    print(f"\n✅ EC-20 PASS | missing start_date rejected with 422")


# ──────────────────────────────────────────────────────────────
# GROUP 6 — RBAC / AUTH EDGE CASES
# ──────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_EC21_student_cannot_access_admin():
    """
    EC-21: Student token cannot call /admin/add-fest.
    """
    async with AsyncClient(base_url=BASE_URL) as c:
        # Login as student
        form = {"username": "2024001", "password": "123"}
        login_res = await c.post("/token", data=form)
        assert login_res.status_code == 200
        token = login_res.json()["access_token"]

        # Try admin endpoint
        res = await c.post(
            "/admin/add-fest",
            json={"event_name": "HackFest", "event_date": "2026-04-10"},
            headers={"Authorization": f"Bearer {token}"}
        )
    assert res.status_code == 403, \
        f"EC-21 FAIL: student got {res.status_code} on admin endpoint"
    print(f"\n✅ EC-21 PASS | student blocked from admin endpoint")


@pytest.mark.asyncio
async def test_EC22_teacher_cannot_access_admin():
    """
    EC-22: Teacher token cannot call /admin/add-fest.
    """
    async with AsyncClient(base_url=BASE_URL) as c:
        form = {"username": "teacher1", "password": "123"}
        login_res = await c.post("/token", data=form)
        assert login_res.status_code == 200
        token = login_res.json()["access_token"]

        res = await c.post(
            "/admin/add-fest",
            json={"event_name": "HackFest", "event_date": "2026-04-10"},
            headers={"Authorization": f"Bearer {token}"}
        )
    assert res.status_code == 403, \
        f"EC-22 FAIL: teacher got {res.status_code} on admin endpoint"
    print(f"\n✅ EC-22 PASS | teacher blocked from admin endpoint")


@pytest.mark.asyncio
async def test_EC23_no_token_on_protected_route():
    """
    EC-23: No Authorization header on /admin/add-fest (protected route in main2.py).
    Should return 401 (no token) — not 403 (wrong role).
    Note: /student/strategy exists only in main.py, not main2.py.
    """
    async with AsyncClient(base_url=BASE_URL) as c:
        res = await c.post(
            "/admin/add-fest",
            json={"event_name": "Test", "event_date": "2026-04-10"}
        )
    assert res.status_code == 401, \
        f"EC-23 FAIL: expected 401 for no token, got {res.status_code}"
    print(f"\n✅ EC-23 PASS | unauthenticated request rejected with 401")


@pytest.mark.asyncio
async def test_EC24_invalid_token():
    """
    EC-24: Garbage JWT token on /admin/add-fest.
    Should return 401.
    Note: /student/strategy exists only in main.py, not main2.py.
    """
    async with AsyncClient(base_url=BASE_URL) as c:
        res = await c.post(
            "/admin/add-fest",
            json={"event_name": "Test", "event_date": "2026-04-10"},
            headers={"Authorization": "Bearer this.is.garbage"}
        )
    assert res.status_code == 401, \
        f"EC-24 FAIL: expected 401 for invalid JWT, got {res.status_code}"
    print(f"\n✅ EC-24 PASS | invalid JWT rejected with 401")


@pytest.mark.asyncio
async def test_EC25_wrong_password_login():
    """
    EC-25: Correct username, wrong password.
    Should return 400.
    """
    async with AsyncClient(base_url=BASE_URL) as c:
        form = {"username": "2024001", "password": "wrongpass"}
        res = await c.post("/token", data=form)
    assert res.status_code == 400, \
        f"EC-25 FAIL: expected 400 for wrong password, got {res.status_code}"
    print(f"\n✅ EC-25 PASS | wrong password rejected")


# ──────────────────────────────────────────────────────────────
# GROUP 7 — FEASIBILITY MATH VERIFICATION
# ──────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_EC26_gap_uses_math_ceil():
    """
    EC-26: Verify gap uses math.ceil (not floor).
    75% of 7 working days = 5.25 → ceil = 6, not 5.
    """
    async with AsyncClient(base_url=BASE_URL) as c:
        res = await post_strategy(c, payload(
            start="2026-03-16", end="2026-03-20",  # Mon–Fri = 5 days
            attended=0, target=75.0, track="Data Science"
        ))
    assert res.status_code == 200
    body = res.json()
    total = body["meta_data"]["total_working_days"]
    gap = body["attendance_math"]["gap_to_fill"]
    import math
    expected_gap = math.ceil(0.75 * total)
    assert gap == expected_gap, \
        f"EC-26 FAIL: gap={gap}, expected ceil(0.75×{total})={expected_gap}"
    print(f"\n✅ EC-26 PASS | ceil math verified: gap={gap} for {total} working days")


@pytest.mark.asyncio
async def test_EC27_target_50_percent():
    """
    EC-27: Low target of 50% (Computer Graphics track, Dec 2025).
    gap should be 0 if attended=8 is already above 50%.
    """
    async with AsyncClient(base_url=BASE_URL) as c:
        res = await post_strategy(c, payload(
            start="2025-12-01", end="2025-12-31",
            attended=8, target=50.0, track="Computer Graphics"
        ))
    assert res.status_code == 200
    body = res.json()
    total = body["meta_data"]["total_working_days"]
    gap = body["attendance_math"]["gap_to_fill"]
    import math
    expected_gap = max(0, math.ceil(0.50 * total) - 8)
    assert gap == expected_gap, \
        f"EC-27 FAIL: gap={gap}, expected {expected_gap}"
    print(f"\n✅ EC-27 PASS | 50% target computed correctly, gap={gap}")


# ──────────────────────────────────────────────────────────────
# MAIN RUNNER — prints summary
# ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import subprocess, sys
    result = subprocess.run(
        ["pytest", __file__, "-v", "--tb=short", "--no-header"],
        capture_output=False
    )
    sys.exit(result.returncode)