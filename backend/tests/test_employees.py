def test_create_employee(client, auth):
    resp = client.post("/api/employees", json={
        "first_name": "John", "last_name": "Smith",
        "email": "john@gsgi.com", "license_type": "D",
        "license_number": "D123456", "license_expiry": "2026-12-31",
        "pay_rate": 18.50
    }, headers=auth)
    assert resp.status_code == 200
    data = resp.json()
    assert data["full_name"] == "John Smith"
    assert data["license_type"] == "D"
    assert data["is_active"] is True


def test_list_employees_default_active_only(client, auth):
    # Create two employees
    for i in range(2):
        client.post("/api/employees", json={
            "first_name": f"Guard{i}", "last_name": "Test",
            "email": f"guard{i}@gsgi.com", "license_type": "D"
        }, headers=auth)
    resp = client.get("/api/employees", headers=auth)
    assert resp.status_code == 200
    assert len(resp.json()) == 2


def test_duplicate_email_rejected(client, auth):
    payload = {"first_name": "A", "last_name": "B",
               "email": "dup@gsgi.com", "license_type": "D"}
    client.post("/api/employees", json=payload, headers=auth)
    resp = client.post("/api/employees", json=payload, headers=auth)
    assert resp.status_code == 400


def test_get_employee_by_id(client, auth, sample_employee):
    emp_id = sample_employee["id"]
    resp = client.get(f"/api/employees/{emp_id}", headers=auth)
    assert resp.status_code == 200
    assert resp.json()["id"] == emp_id


def test_update_employee(client, auth, sample_employee):
    emp_id = sample_employee["id"]
    resp = client.put(f"/api/employees/{emp_id}",
                      json={"pay_rate": 22.0, "license_type": "G"},
                      headers=auth)
    assert resp.status_code == 200
    assert resp.json()["pay_rate"] == 22.0
    assert resp.json()["license_type"] == "G"


def test_deactivate_employee_hides_from_list(client, auth, sample_employee):
    emp_id = sample_employee["id"]
    client.delete(f"/api/employees/{emp_id}", headers=auth)
    resp = client.get("/api/employees", headers=auth)
    ids = [e["id"] for e in resp.json()]
    assert emp_id not in ids


def test_deactivated_employee_visible_with_flag(client, auth, sample_employee):
    emp_id = sample_employee["id"]
    client.delete(f"/api/employees/{emp_id}", headers=auth)
    resp = client.get("/api/employees?active_only=false", headers=auth)
    ids = [e["id"] for e in resp.json()]
    assert emp_id in ids


def test_get_nonexistent_employee_returns_404(client, auth):
    resp = client.get("/api/employees/9999", headers=auth)
    assert resp.status_code == 404
