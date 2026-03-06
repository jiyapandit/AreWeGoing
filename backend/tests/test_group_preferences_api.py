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


def test_public_join_request_host_approve_reject(client):
    host_headers = register_and_login(client, "host2@example.com")
    requester_headers = register_and_login(client, "requester@example.com")
    outsider_headers = register_and_login(client, "outsider2@example.com")

    created = client.post("/api/v1/groups", json={"name": "Public Trip", "is_public": True}, headers=host_headers)
    assert created.status_code == 201
    group_id = created.json()["id"]

    join_request = client.post(f"/api/v1/groups/{group_id}/join-request", headers=requester_headers)
    assert join_request.status_code == 201
    membership_id = join_request.json()["membership_id"]

    non_host_update = client.patch(
        f"/api/v1/groups/{group_id}/members/{membership_id}/status",
        json={"status": "ACTIVE"},
        headers=outsider_headers,
    )
    assert non_host_update.status_code == 403

    host_approve = client.patch(
        f"/api/v1/groups/{group_id}/members/{membership_id}/status",
        json={"status": "ACTIVE"},
        headers=host_headers,
    )
    assert host_approve.status_code == 200
    assert host_approve.json()["status"] == "ACTIVE"

    members = client.get(f"/api/v1/groups/{group_id}/members", headers=host_headers)
    assert members.status_code == 200
    pending = [m for m in members.json()["members"] if m["status"] == "PENDING"]
    assert len(pending) == 0


def test_members_and_preferences_error_paths(client):
    host_headers = register_and_login(client, "host3@example.com")
    member_headers = register_and_login(client, "member3@example.com")
    outsider_headers = register_and_login(client, "outsider3@example.com")

    created = client.post("/api/v1/groups", json={"name": "Edge Trip", "is_public": True}, headers=host_headers)
    assert created.status_code == 201
    group_id = created.json()["id"]
    join_code = created.json()["join_code"]

    join_ok = client.post("/api/v1/groups/join", json={"join_code": join_code}, headers=member_headers)
    assert join_ok.status_code == 200

    members_unauthorized = client.get(
        f"/api/v1/groups/{group_id}/members",
        headers={"Authorization": "Bearer badtoken"},
    )
    assert members_unauthorized.status_code == 401

    members_forbidden = client.get(f"/api/v1/groups/{group_id}/members", headers=outsider_headers)
    assert members_forbidden.status_code == 403

    pref_me_not_found = client.get(f"/api/v1/groups/{group_id}/preferences/me", headers=host_headers)
    assert pref_me_not_found.status_code == 404

    pref_status_forbidden = client.get(f"/api/v1/groups/{group_id}/preferences/status", headers=outsider_headers)
    assert pref_status_forbidden.status_code == 403

    missing_membership_update = client.patch(
        f"/api/v1/groups/{group_id}/members/999999/status",
        json={"status": "ACTIVE"},
        headers=host_headers,
    )
    assert missing_membership_update.status_code == 404

    duplicate_join_request = client.post(f"/api/v1/groups/{group_id}/join-request", headers=member_headers)
    assert duplicate_join_request.status_code == 409
