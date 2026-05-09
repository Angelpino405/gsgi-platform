import pytest


@pytest.fixture
def sample_report(client, auth, sample_employee, sample_site):
    resp = client.post("/api/reports", json={
        "employee_id": sample_employee["id"],
        "site_id": sample_site["id"],
        "report_type": "DAR",
        "date": "2026-06-01",
        "content": "All clear. Gates checked at 0800, 1200, 1600. No incidents."
    }, headers=auth)
    return resp.json()


def test_create_dar(client, auth, sample_employee, sample_site):
    resp = client.post("/api/reports", json={
        "employee_id": sample_employee["id"],
        "site_id": sample_site["id"],
        "report_type": "DAR",
        "date": "2026-06-01",
        "content": "All clear. Gates checked at 0800, 1200, 1600."
    }, headers=auth)
    assert resp.status_code == 200
    data = resp.json()
    assert data["report_type"] == "DAR"
    assert data["employee_name"] == "John Smith"
    assert data["site_name"] == "Bridgewater Bay"


def test_create_incident_report(client, auth, sample_employee, sample_site):
    resp = client.post("/api/reports", json={
        "employee_id": sample_employee["id"],
        "site_id": sample_site["id"],
        "report_type": "Incident",
        "date": "2026-06-01",
        "content": "Vehicle break-in reported at north parking lot. Police notified."
    }, headers=auth)
    assert resp.status_code == 200
    assert resp.json()["report_type"] == "Incident"


def test_list_reports(client, auth, sample_employee, sample_site):
    for i in range(3):
        client.post("/api/reports", json={
            "employee_id": sample_employee["id"],
            "site_id": sample_site["id"],
            "report_type": "DAR",
            "date": f"2026-06-0{i+1}",
            "content": f"Report {i}"
        }, headers=auth)
    resp = client.get("/api/reports", headers=auth)
    assert resp.status_code == 200
    assert len(resp.json()) == 3


def test_filter_reports_by_site(client, auth, sample_employee, sample_site):
    client.post("/api/reports", json={
        "employee_id": sample_employee["id"],
        "site_id": sample_site["id"],
        "report_type": "DAR", "date": "2026-06-01", "content": "All clear."
    }, headers=auth)
    resp = client.get(f"/api/reports?site_id={sample_site['id']}", headers=auth)
    assert len(resp.json()) == 1


def test_get_report_by_id(client, auth, sample_report):
    report_id = sample_report["id"]
    resp = client.get(f"/api/reports/{report_id}", headers=auth)
    assert resp.status_code == 200
    assert resp.json()["id"] == report_id


def test_get_nonexistent_report_returns_404(client, auth):
    resp = client.get("/api/reports/9999", headers=auth)
    assert resp.status_code == 404
