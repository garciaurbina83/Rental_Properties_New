"""
Pruebas unitarias para el módulo de propiedades.
"""

import pytest
from httpx import AsyncClient
from fastapi import status

from app.core.database import get_db
from app.models.property import Property

pytestmark = pytest.mark.asyncio

async def test_create_property(client, auth_headers, test_property):
    """Probar la creación de una propiedad"""
    response = await client.post(
        "/api/v1/properties/",
        json=test_property,
        headers=auth_headers
    )
    
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["title"] == test_property["title"]
    assert data["description"] == test_property["description"]
    assert "id" in data

async def test_get_property(client, auth_headers, test_property):
    """Probar la obtención de una propiedad"""
    # Primero crear una propiedad
    create_response = await client.post(
        "/api/v1/properties/",
        json=test_property,
        headers=auth_headers
    )
    property_id = create_response.json()["id"]
    
    # Obtener la propiedad creada
    response = await client.get(
        f"/api/v1/properties/{property_id}",
        headers=auth_headers
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == property_id
    assert data["title"] == test_property["title"]

async def test_list_properties(client, auth_headers, test_property):
    """Probar el listado de propiedades"""
    # Crear algunas propiedades de prueba
    for i in range(3):
        prop = test_property.copy()
        prop["title"] = f"Test Property {i}"
        await client.post(
            "/api/v1/properties/",
            json=prop,
            headers=auth_headers
        )
    
    # Obtener el listado
    response = await client.get(
        "/api/v1/properties/",
        headers=auth_headers
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) >= 3
    assert all(isinstance(item["id"], str) for item in data)

async def test_update_property(client, auth_headers, test_property):
    """Probar la actualización de una propiedad"""
    # Crear una propiedad
    create_response = await client.post(
        "/api/v1/properties/",
        json=test_property,
        headers=auth_headers
    )
    property_id = create_response.json()["id"]
    
    # Actualizar la propiedad
    updated_data = {
        "title": "Updated Property",
        "price": 2000.00
    }
    response = await client.patch(
        f"/api/v1/properties/{property_id}",
        json=updated_data,
        headers=auth_headers
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["title"] == updated_data["title"]
    assert data["price"] == updated_data["price"]
    assert data["description"] == test_property["description"]

async def test_delete_property(client, auth_headers, test_property):
    """Probar la eliminación de una propiedad"""
    # Crear una propiedad
    create_response = await client.post(
        "/api/v1/properties/",
        json=test_property,
        headers=auth_headers
    )
    property_id = create_response.json()["id"]
    
    # Eliminar la propiedad
    response = await client.delete(
        f"/api/v1/properties/{property_id}",
        headers=auth_headers
    )
    
    assert response.status_code == status.HTTP_204_NO_CONTENT
    
    # Verificar que la propiedad fue eliminada
    get_response = await client.get(
        f"/api/v1/properties/{property_id}",
        headers=auth_headers
    )
    assert get_response.status_code == status.HTTP_404_NOT_FOUND

async def test_property_validation(client, auth_headers):
    """Probar la validación de datos de propiedad"""
    invalid_property = {
        "title": "",  # título vacío
        "price": -100,  # precio negativo
        "bedrooms": "invalid",  # tipo de dato incorrecto
    }
    
    response = await client.post(
        "/api/v1/properties/",
        json=invalid_property,
        headers=auth_headers
    )
    
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    data = response.json()
    assert "detail" in data

async def test_property_search(client, auth_headers, test_property):
    """Probar la búsqueda de propiedades"""
    # Crear propiedades con diferentes características
    properties = [
        {**test_property, "title": "Beach House", "price": 1000},
        {**test_property, "title": "Mountain Cabin", "price": 800},
        {**test_property, "title": "City Apartment", "price": 1200},
    ]
    
    for prop in properties:
        await client.post(
            "/api/v1/properties/",
            json=prop,
            headers=auth_headers
        )
    
    # Buscar por precio máximo
    response = await client.get(
        "/api/v1/properties/?max_price=1000",
        headers=auth_headers
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert all(item["price"] <= 1000 for item in data)
    
    # Buscar por término
    response = await client.get(
        "/api/v1/properties/?search=Beach",
        headers=auth_headers
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert any("Beach" in item["title"] for item in data)

async def test_unauthorized_access(client, test_property):
    """Probar el acceso no autorizado"""
    response = await client.post(
        "/api/v1/properties/",
        json=test_property
    )
    
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

async def test_property_pagination(client, auth_headers, test_property):
    """Probar la paginación de propiedades"""
    # Crear varias propiedades
    for i in range(15):
        prop = test_property.copy()
        prop["title"] = f"Test Property {i}"
        await client.post(
            "/api/v1/properties/",
            json=prop,
            headers=auth_headers
        )
    
    # Probar primera página
    response = await client.get(
        "/api/v1/properties/?skip=0&limit=10",
        headers=auth_headers
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 10
    
    # Probar segunda página
    response = await client.get(
        "/api/v1/properties/?skip=10&limit=10",
        headers=auth_headers
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) >= 5
