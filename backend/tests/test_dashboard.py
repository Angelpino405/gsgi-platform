from datetime import date


def test_dashboard_empty_state(client, auth):
    resp = client.get("/api/dashboard", headers=auth)
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_employees"] == 0
    assert data["total_sites"] == 0
    assert data["today_shifts_total"] == 0


def test_dashboard_counts_active_employees_and_sites(client, auth, sample_employee, sample_site):
    resp = client.get("/api/dashboard", headers=auth)
    data = resp.json()
    assert data["total_employees"] == 1
    assert data["total_sites"] == 1


def test_dashboard_shows_todays_shifts(client, auth, sample_employee, sample_site):
    today = date.today().isoformat()
    client.post("/api/schedules", json={
        "site_id": sample_site["id"],
        "employee_id": sample_employee["id"],
        "date": today, "start_time": "08:00", "end_time": "16:00"
    }, headers=auth)
    resp = client.get("/api/dashboard", headers=auth)
    data = resp.json()
    assert data["today_shifts_total"] == 1
    assert data["today_shifts_covered"] == 1
    assert data["today_shifts_open"] == 0


def test_dashboard_shows_open_shifts(client, auth, sample_site):
    today = date.today().isoformat()
    client.post("/api/schedules", json={
        "site_id": sample_site["id"],
        "date": today, "start_time": "08:00", "end_time": "16:00"
    }, headers=auth)
    resp = client.get("/api/dashboard", headers=auth)
    data = resp.json()
    assert data["today_shifts_open"] == 1
    assert data["today_shifts_covered"] == 0


def test_dashboard_upcoming_shifts_list(client, auth, sample_employee, sample_site):
    today = date.today().isoformat()
    client.post("/api/schedules", json={
        "site_id": sample_site["id"], "employee_id": sample_employee["id"],
        "date": today, "start_time": "08:00", "end_time": "16:00"
    }, headers=auth)
    resp = client.get("/api/dashboard", headers=auth)
    upcoming = resp.json()["upcoming_shifts"]
    assert len(upcoming) >= 1
    assert upcoming[0]["site"] == "Bridgewater Bay"
