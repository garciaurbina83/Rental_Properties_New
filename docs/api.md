# API Documentation

## Properties API

### Property Types

Properties can be of two types:
- `PRINCIPAL`: Main properties that can contain units
- `UNIT`: Individual units that belong to a principal property

### Endpoints

#### Create Principal Property
```http
POST /api/v1/properties
```

Create a new principal property.

**Request Body:**
```json
{
  "name": "Casa Moderna Centro",
  "address": "Calle Principal 123",
  "city": "Ciudad de México",
  "state": "CDMX",
  "zip_code": "01234",
  "country": "México",
  "size": 150.5,
  "bedrooms": 3,
  "bathrooms": 2.5,
  "parking_spots": 2,
  "purchase_price": 500000.00,
  "current_value": 550000.00,
  "monthly_rent": 2500.00,
  "property_type": "principal"
}
```

**Response:** `201 Created`
```json
{
  "id": 1,
  "name": "Casa Moderna Centro",
  ...
  "property_type": "principal",
  "parent_property_id": null,
  "created_at": "2024-01-20T10:30:00Z",
  "updated_at": "2024-01-20T10:30:00Z"
}
```

#### Create Unit
```http
POST /api/v1/properties/{principal_id}/units
```

Create a new unit associated with a principal property.

**Parameters:**
- `principal_id`: ID of the principal property (required)

**Request Body:**
```json
{
  "name": "Unit 1A",
  "address": "Calle Principal 123, Unit 1A",
  "city": "Ciudad de México",
  "state": "CDMX",
  "zip_code": "01234",
  "country": "México",
  "size": 75.5,
  "bedrooms": 2,
  "bathrooms": 1.5,
  "parking_spots": 1,
  "monthly_rent": 1500.00,
  "property_type": "unit"
}
```

**Response:** `201 Created`
```json
{
  "id": 2,
  "name": "Unit 1A",
  ...
  "property_type": "unit",
  "parent_property_id": 1,
  "created_at": "2024-01-20T10:35:00Z",
  "updated_at": "2024-01-20T10:35:00Z"
}
```

#### Get Property with Units
```http
GET /api/v1/properties/{property_id}/with-units
```

Get a principal property along with all its units.

**Parameters:**
- `property_id`: ID of the principal property (required)

**Response:** `200 OK`
```json
{
  "id": 1,
  "name": "Casa Moderna Centro",
  ...
  "property_type": "principal",
  "units": [
    {
      "id": 2,
      "name": "Unit 1A",
      "property_type": "unit",
      "parent_property_id": 1,
      ...
    },
    {
      "id": 3,
      "name": "Unit 1B",
      "property_type": "unit",
      "parent_property_id": 1,
      ...
    }
  ]
}
```

#### Get Units by Principal Property
```http
GET /api/v1/properties/{principal_id}/units
```

Get all units belonging to a principal property.

**Parameters:**
- `principal_id`: ID of the principal property (required)

**Response:** `200 OK`
```json
[
  {
    "id": 2,
    "name": "Unit 1A",
    "property_type": "unit",
    "parent_property_id": 1,
    ...
  },
  {
    "id": 3,
    "name": "Unit 1B",
    "property_type": "unit",
    "parent_property_id": 1,
    ...
  }
]
```

### Business Rules

1. Property Types:
   - A property must be either `PRINCIPAL` or `UNIT`
   - Only `PRINCIPAL` properties can have units
   - `UNIT` properties cannot have sub-units

2. Property Relationships:
   - A `UNIT` must have a parent property
   - The parent property must be of type `PRINCIPAL`
   - A `PRINCIPAL` property can have multiple units

3. Property Operations:
   - When deleting a `PRINCIPAL` property, all its units are also marked as inactive
   - Units can only be created under active `PRINCIPAL` properties
   - Bulk updates respect the property hierarchy

### Error Responses

#### 400 Bad Request
```json
{
  "detail": "Units can only be created under principal properties"
}
```

#### 404 Not Found
```json
{
  "detail": "Property not found"
}
```

#### 422 Unprocessable Entity
```json
{
  "detail": "Invalid property type. Must be one of: principal, unit"
}
```
