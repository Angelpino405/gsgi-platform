import pytest


@pytest.fixture
def sample_shift(client, auth, sample_employee, sample_site):
    resp = client.post("/api/schedules", json={
        "site_id": sample_site["id"],
        "employee_id": sample_employee["id"],
        "date": "2026-06-01",
        "start_time": "08:00",
        "end_time": "16:00"
    }, headers=auth)
    return resp.json()


def test_create_shift(client, auth, sample_employee, sample_site):
    resp = client.post("/api/schedules", json={
        "site_id": sample_site["id"],
        "employee_id": sample_employee["id"],
        "date": "2026-06-01",
        "start_time": "08:00",
        "end_time": "16:00"
    }, headers=auth)
    assert resp.status_code == 200
    data = resp.json()
    assert data["employee_name"] == "John Smith"
    assert data["site_name"] == "Bridgewater Bay"
    assert data["status"] == "scheduled"


def test_create_open_shift_no_employee(client, auth, sample_site):
    resp = client.post("/api/schedules", json={
        "site_id": sample_site["id"],
        "date": "2026-06-01",
        "start_time": "08:00",
        "end_time": "16:00"
    }, headers=auth)
    assert resp.status_code == 200
    assert resp.json()["employee_name"] == "OPEN"


def test_list_open_shifts(client, auth, sample_site):
    client.post("/api/schedules", json={
        "site_id": sample_site["id"],
        "date": "2026-06-01", "start_time": "08:00", "end_time": "16:00"
    }, headers=auth)
    resp = client.get("/api/schedules/open", headers=auth)
    assert resp.status_code == 200
    assert len(resp.json()) == 1


def test_list_shifts_filter_by_date(client, auth, sample_site, sample_employee):
    for d in ["2026-06-01", "2026-06-02", "2026-07-01"]:
        client.post("/api/schedules", json={
            "site_id": sample_site["id"], "employee_id": sample_employee["id"],
            "date": d, "start_time": "08:00", "end_time": "16:00"
        }, headers=auth)
    resp = client.get("/api/schedules?date_from=2026-06-01&date_to=2026-06-30", headers=auth)
    assert resp.status_code == 200
    assert len(resp.json()) == 2


def test_update_shift_assigns_employee(client, auth, sample_site, sample_employee):
    shift_resp = client.post("/api/schedules", json={
        "site_id": sample_site["id"],
        "date": "2026-06-01", "start_time": "08:00", "end_time": "16:00"
    }, headers=auth)
    shift_id = shift_resp.json()["id"]
    resp = client.put(f"/api/schedules/{shift_id}",
                      json={"employee_id": sample_employee["id"]},
                      headers=auth)
    assert resp.status_code == 200
    assert resp.json()["employee_name"] == "John Smith"


def test_cancel_shift(client, auth, sample_shift):
    shift_id = sample_shift["id"]
    resp = client.delete(f"/api/schedules/{shift_id}", headers=auth)
    assert resp.status_code == 200
    shifts = client.get(f"/api/schedules?date_from=2026-06-01&date_to=2026-06-01", headers=auth)
    statuses = [s["status"] for s in shifts.json()]
    assert "cancelled" in statuses


def test_clock_in_sets_shift_active(client, auth, sample_shift, sample_employee):
    resp = client.post("/api/schedules/clock/in", json={
        "employee_id": sample_employee["id"],
        "shift_id": sample_shift["id"],
        "latitude": 26.142, "longitude": -81.795
    }, headers=auth)
    assert resp.status_code == 200
    assert resp.json()["event_type"] == "in"
    shift = client.get("/api/schedules?date_from=2026-06-01&date_to=2026-06-01", headers=auth).json()[0]
    assert shift["status"] == "active"


def test_clock_out_sets_shift_completed(client, auth, sample_shift, sample_employee):
    client.post("/api/schedules/clock/in", json={
        "employee_id": sample_employee["id"], "shift_id": sample_shift["id"]
    }, headers=auth)
    resp = client.post("/api/schedules/clock/out", json={
        "employee_id": sample_employee["id"], "shift_id": sample_shift["id"]
    }, headers=auth)
    assert resp.status_code == 200
    assert resp.json()["event_type"] == "out"
    shift = client.get("/api/schedules?date_from=2026-06-01&date_to=2026-06-01", headers=auth).json()[0]
    assert shift["status"] == "completed"
