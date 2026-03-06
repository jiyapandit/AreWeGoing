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
        json={"email": "outsider-invite@example.com"},
        headers=host_headers,
    )
    assert not_revocable_invite.status_code == 201
    not_revocable_id = not_revocable_invite.json()["id"]

    accept_invite = client.post(
        f"/api/v1/groups/invites/{not_revocable_id}/accept",
        headers=outsider_headers,
    )
    assert accept_invite.status_code == 200
    assert accept_invite.json()["status"] == "ACCEPTED"

    revoke_accepted = client.patch(
        f"/api/v1/groups/{group_id}/invites/{not_revocable_id}",
        json={"status": "REVOKED"},
        headers=host_headers,
    )
    assert_error_envelope(revoke_accepted, 409)


def test_invite_accept_flow_and_notifications(client):
    host_headers = register_and_login(client, "host-accept@example.com")
    invited_headers = register_and_login(client, "invited-accept@example.com")
    other_headers = register_and_login(client, "other-accept@example.com")

    created = client.post("/api/v1/groups", json={"name": "Accept Trip", "is_public": False}, headers=host_headers)
    assert created.status_code == 201
    group_id = created.json()["id"]

    invite_res = client.post(
        f"/api/v1/groups/{group_id}/invites",
        json={"email": "invited-accept@example.com"},
        headers=host_headers,
    )
    assert invite_res.status_code == 201
    invite_id = invite_res.json()["id"]

    my_invites = client.get("/api/v1/groups/invites/me", headers=invited_headers)
    assert my_invites.status_code == 200
    invite_ids = [row["id"] for row in my_invites.json()]
    assert invite_id in invite_ids

    forbidden_accept = client.post(f"/api/v1/groups/invites/{invite_id}/accept", headers=other_headers)
    assert_error_envelope(forbidden_accept, 403)

    accepted = client.post(f"/api/v1/groups/invites/{invite_id}/accept", headers=invited_headers)
    assert accepted.status_code == 200
    assert accepted.json()["status"] == "ACCEPTED"

    my_invites_after = client.get("/api/v1/groups/invites/me", headers=invited_headers)
    assert my_invites_after.status_code == 200
    invite_ids_after = [row["id"] for row in my_invites_after.json()]
    assert invite_id not in invite_ids_after

    host_notifications = client.get("/api/v1/notifications", headers=host_headers)
    assert host_notifications.status_code == 200
    kinds = [n["kind"] for n in host_notifications.json()]
    assert "INVITE_ACCEPTED" in kinds


def test_invite_delivery_webhook_and_status_tracking(client, monkeypatch):
    monkeypatch.setenv("INVITE_WEBHOOK_SECRET", "test-secret")
    host_headers = register_and_login(client, "host-webhook@example.com")

    created = client.post("/api/v1/groups", json={"name": "Webhook Trip", "is_public": False}, headers=host_headers)
    assert created.status_code == 201
    group_id = created.json()["id"]

    invite_res = client.post(
        f"/api/v1/groups/{group_id}/invites",
        json={"email": "someone-webhook@example.com"},
        headers=host_headers,
    )
    assert invite_res.status_code == 201
    invite_payload = invite_res.json()
    invite_id = invite_payload["id"]
    assert "delivery_status" in invite_payload
    assert "delivery_attempts" in invite_payload

    forbidden_webhook = client.post(
        "/api/v1/groups/invites/webhook",
        json={"invite_id": invite_id, "status": "DELIVERED"},
    )
    assert_error_envelope(forbidden_webhook, 403)

    webhook_ok = client.post(
        "/api/v1/groups/invites/webhook",
        headers={"x-invite-webhook-secret": "test-secret"},
        json={
            "invite_id": invite_id,
            "status": "DELIVERED",
            "provider": "smtp",
            "provider_message_id": "provider-msg-123",
        },
    )
    assert webhook_ok.status_code == 200
    assert webhook_ok.json()["delivery_status"] == "DELIVERED"
    assert webhook_ok.json()["delivery_provider_id"] == "provider-msg-123"


def test_group_metrics_snapshot_history(client):
    host_headers = register_and_login(client, "host-metrics@example.com")
    outsider_headers = register_and_login(client, "outsider-metrics@example.com")

    created = client.post("/api/v1/groups", json={"name": "Metrics Trend Trip", "is_public": False}, headers=host_headers)
    assert created.status_code == 201
    group_id = created.json()["id"]

    snapshot = client.post(f"/api/v1/groups/{group_id}/metrics/snapshot", headers=host_headers)
    assert snapshot.status_code == 201
    assert "preferenceCompletionPercent" in snapshot.json()
    assert "itineraryConfidenceScore" in snapshot.json()

    history = client.get(f"/api/v1/groups/{group_id}/metrics/history", headers=host_headers)
    assert history.status_code == 200
    assert isinstance(history.json(), list)
    assert len(history.json()) >= 1

    forbidden_snapshot = client.post(f"/api/v1/groups/{group_id}/metrics/snapshot", headers=outsider_headers)
    assert_error_envelope(forbidden_snapshot, 403)
