import pytest
from httpx import AsyncClient
from app.schemas.user import UserResponse # Importar el schema

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
    user_data = UserResponse(**response.json()) # Convertir a UserResponse
    assert user_data.email == payload["email"]
    assert user_data.full_name == payload["full_name"]
    assert user_data.id is not None # id es UUID, se puede chequear que no sea None
    assert user_data.created_at is not None # created_at es datetime

@pytest.mark.asyncio
async def test_login_and_get_current_user_e2e(client_global: AsyncClient):
    # Crear usuario
    user_payload = {"email": "login_e2e@example.com", "password": "pass12345", "full_name": "Login E2E"}
    response = await client_global.post("/api/v1/users/", json=user_payload)
    assert response.status_code == 201

    # Login usando formulario OAuth2
    form_data = {"username": user_payload["email"], "password": user_payload["password"]}
    token_response = await client_global.post("/api/v1/auth/login", data=form_data)
    assert token_response.status_code == 200

    # Importar Token y convertir
    from app.schemas.token import Token
    token_data = Token(**token_response.json())
    assert token_data.token_type == "bearer"
    access_token = token_data.access_token # Usar el atributo

    # Obtener usuario actual
    headers = {"Authorization": f"Bearer {access_token}"}
    me_response = await client_global.get("/api/v1/users/me", headers=headers)
    assert me_response.status_code == 200
    me_data = UserResponse(**me_response.json()) # Convertir a UserResponse
    assert me_data.email == user_payload["email"]

@pytest.mark.asyncio
async def test_update_and_delete_user_e2e(client_global: AsyncClient):
    # Crear y loguear usuario
    payload = {"email": "upd_e2e@example.com", "password": "updpass123", "full_name": "Upd E2E"}
    create_response = await client_global.post("/api/v1/users/", json=payload)
    assert create_response.status_code == 201
    user_data = UserResponse(**create_response.json()) # Convertir a UserResponse

    from app.schemas.token import Token # Mover import si se usa en múltiples tests
    form = {"username": payload["email"], "password": payload["password"]}
    token_res = await client_global.post("/api/v1/auth/login", data=form)
    assert token_res.status_code == 200
    token_data = Token(**token_res.json()) # Convertir a Token
    headers = {"Authorization": f"Bearer {token_data.access_token}"}

    # Actualizar
    update_payload = {"full_name": "Updated E2E", "is_active": False}
    update_response = await client_global.put(f"/api/v1/users/{user_data.id}", headers=headers, json=update_payload)
    assert update_response.status_code == 200
    updated_user_data = UserResponse(**update_response.json()) # Convertir a UserResponse
    assert updated_user_data.full_name == "Updated E2E"
    assert updated_user_data.is_active is False

    # Borrar
    delete_response = await client_global.delete(f"/api/v1/users/{user_data.id}", headers=headers)
    assert delete_response.status_code == 204
    # Verificar no hay contenido
    assert delete_response.text == ""
