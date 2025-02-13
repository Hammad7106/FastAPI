import pytest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient
from httpx import AsyncClient
from fastapi_project.main import app
from fastapi_project.database import get_db
from sqlalchemy.orm import Session


BASE_URL = "http://127.0.0.1:8000"

@pytest.mark.asyncio
async def test_health_check():
    async with AsyncClient(base_url=BASE_URL) as ac:
        response = await ac.get("/")

    assert response.status_code == 200
    assert response.json() == {"status": "I am Healthy"}



# Test Case for create a user

# @pytest.mark.asyncio
# async def test_create_user():
#     async with AsyncClient(base_url="http://127.0.0.1:8000") as ac:
#         payload = {
#             "email": "ka11@example.com",
#             "password": "1234",
#             "full_name": "Test User"
#         }
#         response = await ac.post("/users", json=payload)
#
#     assert response.status_code == 200
#     assert response.json() == {"message": "User created successfully"}


# Test case for getting acess token
async def get_access_token():
    async with AsyncClient(base_url=BASE_URL) as ac:
        login_payload = {
            "username": "ka11@example.com",  # Replace with valid test user
            "password": "1234"
        }
        response = await ac.post("/token", data=login_payload)

        assert response.status_code == 200
        access_token = response.json().get("access_token")
        assert access_token is not None

        return {"Authorization": f"Bearer {access_token}"}


# Test case for Create Candidate
@pytest.mark.asyncio
async def test_create_candidate():
    headers = await get_access_token()
    async with AsyncClient(base_url=BASE_URL) as ac:
        candidate_payload = {
            "name": "Test2 Candidate",
            "email": "candidate121@example.com",
            "phone": "1234567890",
            "position_applied": "Software Engineer"
        }
        response = await ac.post("/candidates", json=candidate_payload, headers=headers)

    assert response.status_code == 200
    assert response.json()["email"] == "candidate121@example.com"



# Test Case for Edit Candidate by ID
@pytest.mark.asyncio
async def test_get_candidate_by_id():
    headers = await get_access_token()
    async with AsyncClient(base_url=BASE_URL) as ac:
        candidate_id = 19  # Change this if needed
        response = await ac.post(f"/candidate/{candidate_id}", headers=headers)

        if response.status_code == 404:
            assert response.json()["detail"] == "Candidate Not Found"
        else:
            assert response.status_code == 200
            assert "email" in response.json()
            assert "name" in response.json()


# Test Case to Update Candidate
@pytest.mark.asyncio
async def test_update_candidate():
    headers = await get_access_token()
    async with AsyncClient(base_url=BASE_URL) as ac:
        # Step 2: Update an existing candidate
        candidate_id = 19  # Change this to a valid ID in your database
        update_payload = {
            "name": "Updated Namedsdaad",
            "email": "updated_email@example.com",
            "phone": "1234567890",
            "position_applied": "Software Engineer"
        }

        response = await ac.put(f"/candidates/{candidate_id}", json=update_payload, headers=headers)

        if response.status_code == 404:
            assert response.json()["detail"] == "Candidate not found"
        else:
            assert response.status_code == 200
            assert response.json()["name"] == update_payload["name"]
            assert response.json()["email"] == update_payload["email"]
            assert response.json()["position_applied"] == update_payload["position_applied"]


# # Test Case to Delete Candidate
# @pytest.mark.asyncio
# async def test_delete_candidate():
#     headers = await get_access_token()
#
#     async with AsyncClient(base_url=BASE_URL) as ac:
#         candidate_id = 20  # Change to a valid candidate ID
#         response = await ac.delete(f"/candidates/{candidate_id}", headers=headers)
#
#         if response.status_code == 404:
#             assert response.json()["detail"] == "Candidate not found"
#         else:
#             assert response.status_code == 200
#             assert response.json()["message"] == "Candidate deleted successfully"
