def register_and_login(client, email: str, password: str = "Password123"):
    register_res = client.post("/api/v1/auth/register", json={"email": email, "password": password})
    assert register_res.status_code == 201
    login_res = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    assert login_res.status_code == 200
    token = login_res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

def assert_error_envelope(response, expected_status: int):
    assert response.status_code == expected_status
    payload = response.json()
    assert set(payload.keys()) == {"errorCode", "message", "details"}
    assert isinstance(payload["errorCode"], str)
    assert isinstance(payload["message"], str)


def test_groups_preferences_status_codes(client):
    host_headers = register_and_login(client, "host@example.com")
    member_headers = register_and_login(client, "member@example.com")
    outsider_headers = register_and_login(client, "outsider@example.com")

    unauthorized = client.post(
        "/api/v1/groups",
        json={"name": "Trip Alpha", "is_public": False},
        headers={"Authorization": "Bearer badtoken"},
    )
    assert_error_envelope(unauthorized, 401)

    created = client.post("/api/v1/groups", json={"name": "Trip Alpha", "is_public": False}, headers=host_headers)
    assert created.status_code == 201
    group = created.json()
    group_id = group["id"]
    join_code = group["join_code"]

    join_not_found = client.post("/api/v1/groups/join", json={"join_code": "NOPE1234"}, headers=member_headers)
    assert_error_envelope(join_not_found, 404)

    join_ok = client.post("/api/v1/groups/join", json={"join_code": join_code}, headers=member_headers)
    assert join_ok.status_code == 200

    join_conflict = client.post("/api/v1/groups/join", json={"join_code": join_code}, headers=member_headers)
    assert_error_envelope(join_conflict, 409)

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
    assert_error_envelope(pref_forbidden, 403)

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
    assert_error_envelope(non_host_update, 403)

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
    assert_error_envelope(members_unauthorized, 401)

    members_forbidden = client.get(f"/api/v1/groups/{group_id}/members", headers=outsider_headers)
    assert_error_envelope(members_forbidden, 403)

    pref_me_not_found = client.get(f"/api/v1/groups/{group_id}/preferences/me", headers=host_headers)
    assert_error_envelope(pref_me_not_found, 404)

    pref_status_forbidden = client.get(f"/api/v1/groups/{group_id}/preferences/status", headers=outsider_headers)
    assert_error_envelope(pref_status_forbidden, 403)

    missing_membership_update = client.patch(
        f"/api/v1/groups/{group_id}/members/999999/status",
        json={"status": "ACTIVE"},
        headers=host_headers,
    )
    assert_error_envelope(missing_membership_update, 404)

    duplicate_join_request = client.post(f"/api/v1/groups/{group_id}/join-request", headers=member_headers)
    assert_error_envelope(duplicate_join_request, 409)

    invalid_payload = client.post("/api/v1/groups", json={"name": "", "is_public": False}, headers=host_headers)
    assert_error_envelope(invalid_payload, 422)
    assert invalid_payload.json()["errorCode"] == "VALIDATION_ERROR"


def test_invite_revoke_paths(client):
    host_headers = register_and_login(client, "host-invite@example.com")
    member_headers = register_and_login(client, "member-invite@example.com")
    outsider_headers = register_and_login(client, "outsider-invite@example.com")

    created = client.post("/api/v1/groups", json={"name": "Invite Trip", "is_public": True}, headers=host_headers)
    assert created.status_code == 201
    group_id = created.json()["id"]
    join_code = created.json()["join_code"]

    join_member = client.post("/api/v1/groups/join", json={"join_code": join_code}, headers=member_headers)
    assert join_member.status_code == 200

    invite_res = client.post(
        f"/api/v1/groups/{group_id}/invites",
        json={"email": "friend-invite@example.com"},
        headers=host_headers,
    )
    assert invite_res.status_code == 201
    invite_id = invite_res.json()["id"]

    non_host_revoke = client.patch(
        f"/api/v1/groups/{group_id}/invites/{invite_id}",
        json={"status": "REVOKED"},
        headers=outsider_headers,
    )
    assert_error_envelope(non_host_revoke, 403)

    host_revoke = client.patch(
        f"/api/v1/groups/{group_id}/invites/{invite_id}",
        json={"status": "REVOKED"},
        headers=host_headers,
    )
    assert host_revoke.status_code == 200
    assert host_revoke.json()["status"] == "REVOKED"

    already_revoked = client.patch(
        f"/api/v1/groups/{group_id}/invites/{invite_id}",
        json={"status": "REVOKED"},
        headers=host_headers,
    )
    assert already_revoked.status_code == 200
    assert already_revoked.json()["status"] == "REVOKED"

    missing_invite = client.patch(
        f"/api/v1/groups/{group_id}/invites/999999",
        json={"status": "REVOKED"},
        headers=host_headers,
    )
    assert_error_envelope(missing_invite, 404)

    not_revocable_invite = client.post(
        f"/api/v1/groups/{group_id}/invites",
        json={"email": "member-invite@example.com"},
        headers=host_headers,
    )
    assert not_revocable_invite.status_code == 201
    not_revocable_id = not_revocable_invite.json()["id"]

    accept_by_join = client.post("/api/v1/groups/join", json={"join_code": join_code}, headers=outsider_headers)
    assert accept_by_join.status_code == 200

    # mark invite as accepted to emulate accepted flow before revocation attempt
    # (existing API currently does not auto-update invite status on join)
    from db.session import SessionLocal
    from db.models.invite import Invite
    db = SessionLocal()
    try:
        invite = db.query(Invite).filter(Invite.id == not_revocable_id).first()
        invite.status = "ACCEPTED"
        db.add(invite)
        db.commit()
    finally:
        db.close()

    revoke_accepted = client.patch(
        f"/api/v1/groups/{group_id}/invites/{not_revocable_id}",
        json={"status": "REVOKED"},
        headers=host_headers,
    )
    assert_error_envelope(revoke_accepted, 409)
