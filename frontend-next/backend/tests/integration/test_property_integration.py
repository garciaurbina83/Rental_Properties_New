"""
Pruebas unitarias para el módulo de propiedades.
"""

import pytest
from httpx import AsyncClient
from fastapi import status

from app.core.database import get_db
from app.models.property import Property, PropertyType
from app.core.config import settings

# Asegurarnos de que estamos en modo test
settings.ENVIRONMENT = "test"

pytestmark = pytest.mark.asyncio

@pytest.fixture
async def principal_property_data():
    return {
        "name": "Principal Property",
        "address": "123 Main St",
        "city": "Test City",
        "state": "TS",
        "zip_code": "12345",
        "country": "Test Country",
        "property_type": PropertyType.PRINCIPAL,
        "parent_property_id": None
    }

@pytest.fixture
async def unit_property_data():
    return {
        "name": "Unit 1",
        "address": "123 Main St Unit 1",
        "city": "Test City",
        "state": "TS",
        "zip_code": "12345",
        "country": "Test Country",
        "property_type": PropertyType.UNIT
    }

async def test_create_principal_property(client: AsyncClient, auth_headers, principal_property_data):
    """Test principal property creation"""
    response = await client.post(
        "/api/v1/properties",
        json=principal_property_data,
        headers=auth_headers
    )
    
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["name"] == principal_property_data["name"]
    assert data["property_type"] == PropertyType.PRINCIPAL
    assert data["parent_property_id"] is None

async def test_create_unit(client: AsyncClient, auth_headers, principal_property_data, unit_property_data):
    """Test unit creation"""
    # First create a principal property
    principal_response = await client.post(
        "/api/v1/properties",
        json=principal_property_data,
        headers=auth_headers
    )
    principal_id = principal_response.json()["id"]
    
    # Create a unit
    unit_property_data["parent_property_id"] = principal_id
    response = await client.post(
        f"/api/v1/properties/{principal_id}/units",
        json=unit_property_data,
        headers=auth_headers
    )
    
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["name"] == unit_property_data["name"]
    assert data["property_type"] == PropertyType.UNIT
    assert data["parent_property_id"] == principal_id

async def test_get_property_with_units(client: AsyncClient, auth_headers, principal_property_data, unit_property_data):
    """Test getting a principal property with its units"""
    # Create principal property
    principal_response = await client.post(
        "/api/v1/properties",
        json=principal_property_data,
        headers=auth_headers
    )
    principal_id = principal_response.json()["id"]
    
    # Create multiple units
    unit_property_data["parent_property_id"] = principal_id
    for i in range(3):
        unit_data = unit_property_data.copy()
        unit_data["name"] = f"Unit {i+1}"
        await client.post(
            f"/api/v1/properties/{principal_id}/units",
            json=unit_data,
            headers=auth_headers
        )
    
    # Get property with units
    response = await client.get(
        f"/api/v1/properties/{principal_id}/with-units",
        headers=auth_headers
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == principal_id
    assert data["property_type"] == PropertyType.PRINCIPAL
    assert len(data["units"]) == 3

async def test_get_units_by_principal(client: AsyncClient, auth_headers, principal_property_data, unit_property_data):
    """Test getting all units for a principal property"""
    # Create principal property
    principal_response = await client.post(
        "/api/v1/properties",
        json=principal_property_data,
        headers=auth_headers
    )
    principal_id = principal_response.json()["id"]
    
    # Create multiple units
    unit_property_data["parent_property_id"] = principal_id
    created_units = []
    for i in range(3):
        unit_data = unit_property_data.copy()
        unit_data["name"] = f"Unit {i+1}"
        unit_response = await client.post(
            f"/api/v1/properties/{principal_id}/units",
            json=unit_data,
            headers=auth_headers
        )
        created_units.append(unit_response.json())
    
    # Get all units
    response = await client.get(
        f"/api/v1/properties/{principal_id}/units",
        headers=auth_headers
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 3
    assert all(unit["parent_property_id"] == principal_id for unit in data)

async def test_create_unit_invalid_parent(client: AsyncClient, auth_headers, unit_property_data):
    """Test creating a unit with non-existent parent property"""
    unit_property_data["parent_property_id"] = 99999
    response = await client.post(
        "/api/v1/properties/99999/units",
        json=unit_property_data,
        headers=auth_headers
    )
    
    assert response.status_code == status.HTTP_404_NOT_FOUND

async def test_create_unit_with_unit_parent(client: AsyncClient, auth_headers, principal_property_data, unit_property_data):
    """Test creating a unit with another unit as parent"""
    # Create principal property
    principal_response = await client.post(
        "/api/v1/properties",
        json=principal_property_data,
        headers=auth_headers
    )
    principal_id = principal_response.json()["id"]
    
    # Create first unit
    unit_property_data["parent_property_id"] = principal_id
    unit_response = await client.post(
        f"/api/v1/properties/{principal_id}/units",
        json=unit_property_data,
        headers=auth_headers
    )
    unit_id = unit_response.json()["id"]
    
    # Try to create unit with unit as parent
    unit_property_data["name"] = "Sub Unit"
    response = await client.post(
        f"/api/v1/properties/{unit_id}/units",
        json=unit_property_data,
        headers=auth_headers
    )
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST

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
