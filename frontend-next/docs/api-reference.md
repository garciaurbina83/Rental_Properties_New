# API Reference

## Endpoints

### Properties

#### GET /api/properties
Obtiene lista de propiedades con filtros opcionales.

**Query Parameters:**
- `status`: Estado de la propiedad (available, rented, maintenance)
- `type`: Tipo de propiedad (house, apartment, office)
- `minPrice`: Precio mínimo
- `maxPrice`: Precio máximo
- `page`: Número de página
- `limit`: Elementos por página

**Response:**
```typescript
interface Property {
  id: string;
  title: string;
  description: string;
  address: string;
  price: number;
  status: 'available' | 'rented' | 'maintenance';
  type: 'house' | 'apartment' | 'office';
  images: string[];
  features: string[];
  createdAt: string;
  updatedAt: string;
}

interface PropertiesResponse {
  data: Property[];
  pagination: {
    total: number;
    page: number;
    limit: number;
    totalPages: number;
  };
}
```

#### GET /api/properties/:id
Obtiene detalles de una propiedad específica.

#### POST /api/properties
Crea una nueva propiedad.

**Request Body:**
```typescript
interface CreatePropertyRequest {
  title: string;
  description: string;
  address: string;
  price: number;
  type: 'house' | 'apartment' | 'office';
  features: string[];
  images?: string[];
}
```

### Contracts

#### GET /api/contracts
Obtiene lista de contratos.

**Query Parameters:**
- `status`: Estado del contrato (active, pending, finished)
- `propertyId`: ID de la propiedad
- `tenantId`: ID del inquilino
- `page`: Número de página
- `limit`: Elementos por página

**Response:**
```typescript
interface Contract {
  id: string;
  propertyId: string;
  tenantId: string;
  startDate: string;
  endDate: string;
  monthlyRent: number;
  status: 'active' | 'pending' | 'finished';
  documents: string[];
  createdAt: string;
  updatedAt: string;
}
```

## Hooks Personalizados

### useProperties
```typescript
const {
  properties,
  isLoading,
  error,
  filterProperties,
  sortProperties,
  pagination,
} = useProperties(options?: {
  initialFilters?: PropertyFilters;
  initialSort?: SortOptions;
});
```

### useContract
```typescript
const {
  contract,
  isLoading,
  error,
  updateContract,
  terminateContract,
} = useContract(contractId: string);
```

### useAuth
```typescript
const {
  user,
  isLoading,
  isAuthenticated,
  signIn,
  signOut,
} = useAuth();
```

## Componentes Comunes

### PropertyCard
```typescript
interface PropertyCardProps {
  property: Property;
  onClick?: (property: Property) => void;
  variant?: 'default' | 'compact';
}
```

### ContractForm
```typescript
interface ContractFormProps {
  propertyId: string;
  onSubmit: (data: ContractFormData) => void;
  onCancel: () => void;
  initialData?: Partial<ContractFormData>;
}
```

### FilterPanel
```typescript
interface FilterPanelProps {
  filters: PropertyFilters;
  onChange: (filters: PropertyFilters) => void;
  onReset: () => void;
}
```

## Utilidades

### formatCurrency
```typescript
function formatCurrency(amount: number, currency?: string): string;
```

### formatDate
```typescript
function formatDate(date: string | Date, format?: string): string;
```

### validateContract
```typescript
function validateContract(data: ContractFormData): ValidationResult;
```

## Constantes

### Property Status
```typescript
export const PROPERTY_STATUS = {
  AVAILABLE: 'available',
  RENTED: 'rented',
  MAINTENANCE: 'maintenance',
} as const;
```

### Contract Status
```typescript
export const CONTRACT_STATUS = {
  ACTIVE: 'active',
  PENDING: 'pending',
  FINISHED: 'finished',
} as const;
```

## Tipos Comunes

```typescript
interface PropertyFilters {
  status?: PropertyStatus;
  type?: PropertyType;
  minPrice?: number;
  maxPrice?: number;
  features?: string[];
}

interface SortOptions {
  field: keyof Property;
  direction: 'asc' | 'desc';
}

interface ValidationResult {
  isValid: boolean;
  errors: Record<string, string>;
}
```
