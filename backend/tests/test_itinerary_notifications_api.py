def register_and_login(client, email: str, password: str = "Password123"):
    register_res = client.post("/api/v1/auth/register", json={"email": email, "password": password})
    assert register_res.status_code == 201
    login_res = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    assert login_res.status_code == 200
    token = login_res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def create_group_and_join(client):
    host_headers = register_and_login(client, "i_host@example.com")
    member_headers = register_and_login(client, "i_member@example.com")
    outsider_headers = register_and_login(client, "i_outsider@example.com")

    created = client.post("/api/v1/groups", json={"name": "Itinerary Squad", "is_public": False}, headers=host_headers)
    assert created.status_code == 201
    group = created.json()
    group_id = group["id"]

    joined = client.post("/api/v1/groups/join", json={"join_code": group["join_code"]}, headers=member_headers)
    assert joined.status_code == 200
    return group_id, host_headers, member_headers, outsider_headers


def test_itinerary_vote_lock_and_notifications_statuses(client):
    group_id, host_headers, member_headers, outsider_headers = create_group_and_join(client)

    unauthorized = client.post(
        f"/api/v1/groups/{group_id}/itinerary/generate",
        headers={"Authorization": "Bearer badtoken"},
    )
    assert unauthorized.status_code == 401

    forbidden = client.post(f"/api/v1/groups/{group_id}/itinerary/generate", headers=outsider_headers)
    assert forbidden.status_code == 403

    not_found = client.get(f"/api/v1/groups/{group_id}/itinerary", headers=host_headers)
    assert not_found.status_code == 404

    vote_before_generate = client.post(
        f"/api/v1/groups/{group_id}/vote",
        json={"value": "APPROVE"},
        headers=host_headers,
    )
    assert vote_before_generate.status_code == 404

    generated = client.post(f"/api/v1/groups/{group_id}/itinerary/generate", headers=host_headers)
    assert generated.status_code == 200

    vote_invalid_state = client.post(
        f"/api/v1/groups/{group_id}/vote",
        json={"value": "APPROVE"},
        headers=member_headers,
    )
    assert vote_invalid_state.status_code == 409

    to_review = client.post(f"/api/v1/groups/{group_id}/itinerary/review", headers=member_headers)
    assert to_review.status_code == 200

    vote_ok = client.post(
        f"/api/v1/groups/{group_id}/vote",
        json={"value": "APPROVE"},
        headers=member_headers,
    )
    assert vote_ok.status_code == 200

    vote_duplicate = client.post(
        f"/api/v1/groups/{group_id}/vote",
        json={"value": "CHANGES"},
        headers=member_headers,
    )
    assert vote_duplicate.status_code == 409

    lock_forbidden = client.post(f"/api/v1/groups/{group_id}/itinerary/lock", headers=member_headers)
    assert lock_forbidden.status_code == 403

    lock_ok = client.post(f"/api/v1/groups/{group_id}/itinerary/lock", headers=host_headers)
    assert lock_ok.status_code == 200

    generate_after_lock = client.post(f"/api/v1/groups/{group_id}/itinerary/generate", headers=host_headers)
    assert generate_after_lock.status_code == 409

    notes = client.get("/api/v1/notifications", headers=member_headers)
    assert notes.status_code == 200
    assert isinstance(notes.json(), list)
    assert len(notes.json()) > 0

    note_not_found = client.patch("/api/v1/notifications/999999/read", headers=member_headers)
    assert note_not_found.status_code == 404
