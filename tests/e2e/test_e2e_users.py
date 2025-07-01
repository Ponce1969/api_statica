import pytest
from httpx import AsyncClient

# Usamos los fixtures globales definidos en tests/conftest.py

@pytest.mark.asyncio
async def test_create_user_e2e(client_global: AsyncClient):
    payload = {
        "email": "new_e2e@example.com",
        "password": "newpassword123",
        "full_name": "New User E2E"
    }
    response = await client_global.post("/api/v1/users/", json=payload)
    # ———————————— añade esto ————————————
    print(">>> VALIDATION DETAIL:", response.json())
    # ————————————————————————————————————————
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == payload["email"]
    assert data["full_name"] == payload["full_name"]
    assert "id" in data
    assert "created_at" in data

@pytest.mark.asyncio
async def test_login_and_get_current_user_e2e(client_global: AsyncClient):
    # Crear usuario
    user_payload = {"email": "login_e2e@example.com", "password": "pass12345", "full_name": "Login E2E"}
    response = await client_global.post("/api/v1/users/", json=user_payload)
    assert response.status_code == 201

    # Login usando formulario OAuth2
    form_data = {"username": user_payload["email"], "password": user_payload["password"]}
    response = await client_global.post("/api/v1/auth/login", data=form_data)
    assert response.status_code == 200
    token = response.json()["access_token"]
    assert response.json()["token_type"] == "bearer"

    # Obtener usuario actual
    headers = {"Authorization": f"Bearer {token}"}
    response = await client_global.get("/api/v1/users/me", headers=headers)
    assert response.status_code == 200
    me_data = response.json()
    assert me_data["email"] == user_payload["email"]

@pytest.mark.asyncio
async def test_update_and_delete_user_e2e(client_global: AsyncClient):
    # Crear y loguear usuario
    payload = {"email": "upd_e2e@example.com", "password": "updpass123", "full_name": "Upd E2E"}
    response = await client_global.post("/api/v1/users/", json=payload)
    assert response.status_code == 201
    user = response.json()
    form = {"username": payload["email"], "password": payload["password"]}
    token_res = await client_global.post("/api/v1/auth/login", data=form)
    assert token_res.status_code == 200
    token = token_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Actualizar
    update_payload = {"full_name": "Updated E2E", "is_active": False}
    response = await client_global.put(f"/api/v1/users/{user['id']}", headers=headers, json=update_payload)
    assert response.status_code == 200
    updated = response.json()
    assert updated["full_name"] == "Updated E2E"
    assert updated["is_active"] is False

    # Borrar
    response = await client_global.delete(f"/api/v1/users/{user['id']}", headers=headers)
    assert response.status_code == 204
    # Verificar no hay contenido
    assert response.text == ""
