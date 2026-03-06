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


def test_full_group_planning_happy_path(client):
    host_headers = register_and_login(client, "e2e_host@example.com")
    member_headers = register_and_login(client, "e2e_member@example.com")

    create_group = client.post(
        "/api/v1/groups",
        json={"name": "E2E Alpine Trip", "is_public": False},
        headers=host_headers,
    )
    assert create_group.status_code == 201
    group = create_group.json()
    group_id = group["id"]
    join_code = group["join_code"]

    join_group = client.post("/api/v1/groups/join", json={"join_code": join_code}, headers=member_headers)
    assert join_group.status_code == 200

    host_prefs = client.put(
        f"/api/v1/groups/{group_id}/preferences",
        json={
            "destination_type": "mountains",
            "budget_min": 100,
            "budget_max": 220,
            "days": 3,
            "activities": ["hiking", "food"],
            "transport_mode": "car",
            "dietary_preferences": ["veg"],
            "travel_pace": "balanced",
        },
        headers=host_headers,
    )
    assert host_prefs.status_code == 200

    member_prefs = client.put(
        f"/api/v1/groups/{group_id}/preferences",
        json={
            "destination_type": "mountains",
            "budget_min": 90,
            "budget_max": 210,
            "days": 4,
            "activities": ["hiking", "culture"],
            "transport_mode": "car",
            "dietary_preferences": ["halal"],
            "travel_pace": "balanced",
        },
        headers=member_headers,
    )
    assert member_prefs.status_code == 200

    pref_status = client.get(f"/api/v1/groups/{group_id}/preferences/status", headers=host_headers)
    assert pref_status.status_code == 200
    assert pref_status.json()["completion_percent"] == 100

    generated = client.post(f"/api/v1/groups/{group_id}/itinerary/generate", headers=host_headers)
    assert generated.status_code == 200
    assert generated.json()["state"] == "DRAFT"

    to_review = client.post(f"/api/v1/groups/{group_id}/itinerary/review", headers=host_headers)
    assert to_review.status_code == 200
    assert to_review.json()["state"] == "REVIEW"

    host_vote = client.post(
        f"/api/v1/groups/{group_id}/vote",
        json={"value": "APPROVE"},
        headers=host_headers,
    )
    assert host_vote.status_code == 200

    member_vote = client.post(
        f"/api/v1/groups/{group_id}/vote",
        json={"value": "APPROVE"},
        headers=member_headers,
    )
    assert member_vote.status_code == 200

    lock = client.post(f"/api/v1/groups/{group_id}/itinerary/lock", headers=host_headers)
    assert lock.status_code == 200
    assert lock.json()["state"] == "LOCKED"

    vote_after_lock = client.post(
        f"/api/v1/groups/{group_id}/vote",
        json={"value": "CHANGES"},
        headers=member_headers,
    )
    assert_error_envelope(vote_after_lock, 409)

    regenerate_after_lock = client.post(f"/api/v1/groups/{group_id}/itinerary/generate", headers=host_headers)
    assert_error_envelope(regenerate_after_lock, 409)

