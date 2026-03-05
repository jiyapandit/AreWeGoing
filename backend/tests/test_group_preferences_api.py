def register_and_login(client, email: str, password: str = "Password123"):
    register_res = client.post("/api/v1/auth/register", json={"email": email, "password": password})
    assert register_res.status_code == 201
    login_res = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    assert login_res.status_code == 200
    token = login_res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_groups_preferences_status_codes(client):
    host_headers = register_and_login(client, "host@example.com")
    member_headers = register_and_login(client, "member@example.com")
    outsider_headers = register_and_login(client, "outsider@example.com")

    unauthorized = client.post(
        "/api/v1/groups",
        json={"name": "Trip Alpha", "is_public": False},
        headers={"Authorization": "Bearer badtoken"},
    )
    assert unauthorized.status_code == 401

    created = client.post("/api/v1/groups", json={"name": "Trip Alpha", "is_public": False}, headers=host_headers)
    assert created.status_code == 201
    group = created.json()
    group_id = group["id"]
    join_code = group["join_code"]

    join_not_found = client.post("/api/v1/groups/join", json={"join_code": "NOPE1234"}, headers=member_headers)
    assert join_not_found.status_code == 404

    join_ok = client.post("/api/v1/groups/join", json={"join_code": join_code}, headers=member_headers)
    assert join_ok.status_code == 200

    join_conflict = client.post("/api/v1/groups/join", json={"join_code": join_code}, headers=member_headers)
    assert join_conflict.status_code == 409

    pref_forbidden = client.put(
        f"/api/v1/groups/{group_id}/preferences",
        json={
            "destination_type": "city",
            "budget_min": 50,
            "budget_max": 120,
            "days": 3,
            "activities": ["culture", "food"],
            "transport_mode": "train",
            "dietary_preferences": ["veg"],
            "travel_pace": "balanced",
        },
        headers=outsider_headers,
    )
    assert pref_forbidden.status_code == 403

    pref_ok = client.put(
        f"/api/v1/groups/{group_id}/preferences",
        json={
            "destination_type": "city",
            "budget_min": 50,
            "budget_max": 120,
            "days": 3,
            "activities": ["culture", "food"],
            "transport_mode": "train",
            "dietary_preferences": ["veg"],
            "travel_pace": "balanced",
        },
        headers=member_headers,
    )
    assert pref_ok.status_code == 200

    status_ok = client.get(f"/api/v1/groups/{group_id}/preferences/status", headers=host_headers)
    assert status_ok.status_code == 200
    assert "completion_percent" in status_ok.json()

    members_ok = client.get(f"/api/v1/groups/{group_id}/members", headers=host_headers)
    assert members_ok.status_code == 200
    assert len(members_ok.json()["members"]) == 2
