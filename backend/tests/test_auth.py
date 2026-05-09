def test_register_returns_user(client):
    resp = client.post("/api/auth/register", json={
        "username": "angel", "email": "angel@gsgi.com",
        "password": "gsgi2024!", "role": "admin"
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["username"] == "angel"
    assert data["role"] == "admin"
    assert "hashed_password" not in data


def test_duplicate_username_rejected(client):
    payload = {"username": "angel", "email": "a@gsgi.com",
               "password": "gsgi2024!", "role": "admin"}
    client.post("/api/auth/register", json=payload)
    resp = client.post("/api/auth/register", json=payload)
    assert resp.status_code == 400


def test_login_returns_token(client):
    client.post("/api/auth/register", json={
        "username": "angel", "email": "angel@gsgi.com",
        "password": "gsgi2024!", "role": "admin"
    })
    resp = client.post("/api/auth/token", data={
        "username": "angel", "password": "gsgi2024!"
    })
    assert resp.status_code == 200
    assert "access_token" in resp.json()
    assert resp.json()["token_type"] == "bearer"


def test_wrong_password_returns_401(client):
    client.post("/api/auth/register", json={
        "username": "angel", "email": "angel@gsgi.com",
        "password": "gsgi2024!", "role": "admin"
    })
    resp = client.post("/api/auth/token", data={
        "username": "angel", "password": "wrongpass"
    })
    assert resp.status_code == 401


def test_me_returns_current_user(client, auth):
    resp = client.get("/api/auth/me", headers=auth)
    assert resp.status_code == 200
    assert resp.json()["username"] == "angel"
    assert "hashed_password" not in resp.json()


def test_protected_route_without_token_returns_401(client):
    resp = client.get("/api/employees")
    assert resp.status_code == 401
