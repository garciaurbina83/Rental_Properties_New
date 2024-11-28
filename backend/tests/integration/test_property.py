"""
Pruebas unitarias para el módulo de propiedades.
"""

import pytest
from httpx import AsyncClient
from fastapi import status

from app.core.database import get_db
from app.models.property import Property
from app.core.config import settings

# Asegurarnos de que estamos en modo test
settings.ENVIRONMENT = "test"

pytestmark = pytest.mark.asyncio

async def test_create_property(client: AsyncClient, auth_headers, test_property_data):
    """Test property creation"""
    response = await client.post(
        "/api/v1/properties",
        json=test_property_data,
        headers=auth_headers
    )
    
    if response.status_code != status.HTTP_201_CREATED:
        print(f"Response status code: {response.status_code}")
        print(f"Response body: {response.text}")
        print(f"Test property data: {test_property_data}")
        print(f"Auth headers: {auth_headers}")
        print(f"Response headers: {response.headers}")
    
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["name"] == test_property_data["name"]
    assert data["address"] == test_property_data["address"]
    assert "id" in data

async def test_get_property(client: AsyncClient, auth_headers, test_property_data):
    """Probar la obtención de una propiedad"""
    # Primero crear una propiedad
    create_response = await client.post(
        "/api/v1/properties",
        json=test_property_data,
        headers=auth_headers
    )
    property_id = create_response.json()["id"]

    # Obtener la propiedad creada
    response = await client.get(
        f"/api/v1/properties/{property_id}",
        headers=auth_headers
    )

    if response.status_code != status.HTTP_200_OK:
        print(f"Response status code: {response.status_code}")
        print(f"Response body: {response.text}")
        print(f"Property ID: {property_id}")
        print(f"Auth headers: {auth_headers}")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == property_id
    assert data["name"] == test_property_data["name"]
    assert data["address"] == test_property_data["address"]

async def test_list_properties(client: AsyncClient, auth_headers, test_property_data):
    """Probar el listado de propiedades"""
    # Crear algunas propiedades para listar
    for i in range(3):
        prop = test_property_data.copy()
        prop["name"] = f"Test Property {i}"
        await client.post(
            "/api/v1/properties",
            json=prop,
            headers=auth_headers
        )

    # Obtener la lista de propiedades
    response = await client.get(
        "/api/v1/properties",
        headers=auth_headers
    )

    if response.status_code != status.HTTP_200_OK:
        print(f"Response status code: {response.status_code}")
        print(f"Response body: {response.text}")
        print(f"Auth headers: {auth_headers}")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) >= 3  # Al menos las 3 propiedades que creamos
    assert all(isinstance(prop, dict) for prop in data)

async def test_update_property(client: AsyncClient, auth_headers, test_property_data):
    """Probar la actualización de una propiedad"""
    # Primero crear una propiedad
    create_response = await client.post(
        "/api/v1/properties",
        json=test_property_data,
        headers=auth_headers
    )
    property_id = create_response.json()["id"]

    # Actualizar la propiedad
    updated_data = {
        "name": "Updated Property",
        "monthly_rent": 1500.0
    }
    response = await client.patch(
        f"/api/v1/properties/{property_id}",
        json=updated_data,
        headers=auth_headers
    )

    if response.status_code != status.HTTP_200_OK:
        print(f"Response status code: {response.status_code}")
        print(f"Response body: {response.text}")
        print(f"Property ID: {property_id}")
        print(f"Updated data: {updated_data}")
        print(f"Auth headers: {auth_headers}")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == property_id
    assert data["name"] == updated_data["name"]
    assert data["monthly_rent"] == updated_data["monthly_rent"]

async def test_delete_property(client: AsyncClient, auth_headers, test_property_data):
    """Probar la eliminación de una propiedad"""
    # Primero crear una propiedad
    create_response = await client.post(
        "/api/v1/properties",
        json=test_property_data,
        headers=auth_headers
    )
    property_id = create_response.json()["id"]

    # Eliminar la propiedad
    response = await client.delete(
        f"/api/v1/properties/{property_id}",
        headers=auth_headers
    )

    if response.status_code != status.HTTP_204_NO_CONTENT:
        print(f"Response status code: {response.status_code}")
        print(f"Response body: {response.text}")
        print(f"Property ID: {property_id}")
        print(f"Auth headers: {auth_headers}")
    
    assert response.status_code == status.HTTP_204_NO_CONTENT

    # Verificar que la propiedad fue eliminada
    get_response = await client.get(
        f"/api/v1/properties/{property_id}",
        headers=auth_headers
    )

    if get_response.status_code != status.HTTP_404_NOT_FOUND:
        print(f"Response status code: {get_response.status_code}")
        print(f"Response body: {get_response.text}")
        print(f"Property ID: {property_id}")
        print(f"Auth headers: {auth_headers}")
    
    assert get_response.status_code == status.HTTP_404_NOT_FOUND

async def test_property_validation(client: AsyncClient, auth_headers):
    """Probar la validación de datos de propiedad"""
    # Probar con datos inválidos
    invalid_property = {
        "name": "",  # Nombre vacío
        "address": "123 Test St",
        "city": "Test City",
        "state": "Test State",
        "zip_code": "12345",
        "country": "Test Country",
        "size": -100,  # Tamaño negativo
        "bedrooms": -1,  # Número negativo de habitaciones
        "bathrooms": 0,  # Número inválido de baños
        "parking_spots": -2,  # Número negativo de estacionamientos
        "purchase_price": -50000,  # Precio negativo
        "current_value": -60000,  # Valor negativo
        "monthly_rent": -500,  # Renta negativa
        "status": "invalid_status",  # Estado inválido
    }

    response = await client.post(
        "/api/v1/properties",
        json=invalid_property,
        headers=auth_headers
    )

    if response.status_code != status.HTTP_422_UNPROCESSABLE_ENTITY:
        print(f"Response status code: {response.status_code}")
        print(f"Response body: {response.text}")
        print(f"Invalid property data: {invalid_property}")
        print(f"Auth headers: {auth_headers}")
    
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

async def test_property_search(client: AsyncClient, auth_headers, test_property_data):
    """Probar la búsqueda de propiedades"""
    # Crear algunas propiedades con diferentes características
    properties = [
        {**test_property_data, "name": "Luxury Villa", "city": "Miami"},
        {**test_property_data, "name": "Beach House", "city": "Miami"},
        {**test_property_data, "name": "Mountain Cabin", "city": "Denver"}
    ]
    
    for prop in properties:
        await client.post(
            "/api/v1/properties",
            json=prop,
            headers=auth_headers
        )

    # Buscar propiedades en Miami
    response = await client.get(
        "/api/v1/properties",
        params={"city": "Miami"},
        headers=auth_headers
    )

    if response.status_code != status.HTTP_200_OK:
        print(f"Response status code: {response.status_code}")
        print(f"Response body: {response.text}")
        print(f"Search params: {{'city': 'Miami'}}")
        print(f"Auth headers: {auth_headers}")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 2
    assert all(prop["city"] == "Miami" for prop in data)

async def test_unauthorized_access(client: AsyncClient, test_property_data):
    """Probar el acceso no autorizado"""
    response = await client.post(
        "/api/v1/properties",
        json=test_property_data
    )

    if response.status_code != status.HTTP_401_UNAUTHORIZED:
        print(f"Response status code: {response.status_code}")
        print(f"Response body: {response.text}")
        print(f"Test property data: {test_property_data}")
    
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

async def test_property_pagination(client: AsyncClient, auth_headers, test_property_data):
    """Probar la paginación de propiedades"""
    # Crear varias propiedades
    properties = []
    for i in range(15):
        prop = test_property_data.copy()
        prop["name"] = f"Test Property {i}"
        response = await client.post(
            "/api/v1/properties",
            json=prop,
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_201_CREATED
        properties.append(response.json())

    # Probar primera página
    response = await client.get(
        "/api/v1/properties",
        params={"skip": 0, "limit": 10},
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 10

    # Probar segunda página
    response = await client.get(
        "/api/v1/properties",
        params={"skip": 10, "limit": 10},
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 5

    # Probar límite mayor que el total de elementos
    response = await client.get(
        "/api/v1/properties",
        params={"skip": 0, "limit": 20},
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 15
