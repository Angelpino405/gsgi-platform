def test_create_site(client, auth):
    resp = client.post("/api/sites", json={
        "name": "Bridgewater Bay", "client_name": "Bridgewater Bay POA",
        "address": "123 Main St", "city": "Naples", "state": "FL",
        "zip_code": "34110", "billing_rate": 25.0, "requires_armed": False
    }, headers=auth)
    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == "Bridgewater Bay"
    assert data["city"] == "Naples"
    assert data["is_active"] is True


def test_list_sites(client, auth):
    for i in range(3):
        client.post("/api/sites", json={
            "name": f"Site {i}", "client_name": f"Client {i}"
        }, headers=auth)
    resp = client.get("/api/sites", headers=auth)
    assert resp.status_code == 200
    assert len(resp.json()) == 3


def test_get_site_by_id(client, auth, sample_site):
    site_id = sample_site["id"]
    resp = client.get(f"/api/sites/{site_id}", headers=auth)
    assert resp.status_code == 200
    assert resp.json()["id"] == site_id


def test_update_site_post_orders(client, auth, sample_site):
    site_id = sample_site["id"]
    resp = client.put(f"/api/sites/{site_id}",
                      json={"post_orders": "Check all gates hourly.", "requires_armed": True},
                      headers=auth)
    assert resp.status_code == 200
    assert resp.json()["post_orders"] == "Check all gates hourly."
    assert resp.json()["requires_armed"] is True


def test_deactivate_site(client, auth, sample_site):
    site_id = sample_site["id"]
    client.delete(f"/api/sites/{site_id}", headers=auth)
    resp = client.get("/api/sites", headers=auth)
    ids = [s["id"] for s in resp.json()]
    assert site_id not in ids


def test_deactivated_site_visible_with_flag(client, auth, sample_site):
    site_id = sample_site["id"]
    client.delete(f"/api/sites/{site_id}", headers=auth)
    resp = client.get("/api/sites?active_only=false", headers=auth)
    ids = [s["id"] for s in resp.json()]
    assert site_id in ids


def test_get_nonexistent_site_returns_404(client, auth):
    resp = client.get("/api/sites/9999", headers=auth)
    assert resp.status_code == 404
