'use client';

import { useState } from 'react';
import { PropertyCreate, PropertyType, PropertyStatus } from '@/types/property';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Select } from './ui/select';
import { Box, VStack, FormControl } from '@chakra-ui/react';

interface PropertyFormProps {
  onSubmit: (data: PropertyCreate) => void;
  onCancel: () => void;
}

const propertyTypeOptions = Object.entries(PropertyType).map(([key, value]) => ({
  value,
  label: key.charAt(0).toUpperCase() + key.slice(1).toLowerCase()
}));

const propertyStatusOptions = Object.entries(PropertyStatus).map(([key, value]) => ({
  value,
  label: key.charAt(0).toUpperCase() + key.slice(1).toLowerCase()
}));

export default function PropertyForm({ onSubmit, onCancel }: PropertyFormProps) {
  const [formData, setFormData] = useState<PropertyCreate>({
    name: '',
    description: '',
    property_type: PropertyType.HOUSE,
    status: PropertyStatus.AVAILABLE,
    address: '',
    city: '',
    state: '',
    country: '',
    postal_code: '',
    price: 0,
    bedrooms: 0,
    bathrooms: 0,
    square_meters: 0,
    year_built: undefined,
    parking_spots: 0,
    has_garden: false,
    has_pool: false,
    is_furnished: false,
    is_pet_friendly: false,
    available_from: undefined
  });

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value, type } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'number' ? Number(value) : value
    }));
  };

  const handleSelectChange = (name: string) => (value: string) => {
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit(formData);
  };

  return (
    <Box as="form" onSubmit={handleSubmit}>
      <VStack spacing={4}>
        <FormControl>
          <Label>Name</Label>
          <Input
            name="name"
            value={formData.name}
            onChange={handleChange}
            required
          />
        </FormControl>

        <FormControl>
          <Label>Description</Label>
          <Input
            name="description"
            value={formData.description}
            onChange={handleChange}
          />
        </FormControl>

        <FormControl>
          <Select
            label="Property Type"
            name="property_type"
            value={formData.property_type}
            onChange={(e) => handleSelectChange('property_type')(e.target.value)}
            options={propertyTypeOptions}
            required
          />
        </FormControl>

        <FormControl>
          <Select
            label="Status"
            name="status"
            value={formData.status}
            onChange={(e) => handleSelectChange('status')(e.target.value)}
            options={propertyStatusOptions}
            required
          />
        </FormControl>

        <FormControl>
          <Label>Address</Label>
          <Input
            name="address"
            value={formData.address}
            onChange={handleChange}
            required
          />
        </FormControl>

        <FormControl>
          <Label>City</Label>
          <Input
            name="city"
            value={formData.city}
            onChange={handleChange}
            required
          />
        </FormControl>

        <FormControl>
          <Label>State</Label>
          <Input
            name="state"
            value={formData.state}
            onChange={handleChange}
            required
          />
        </FormControl>

        <FormControl>
          <Label>Country</Label>
          <Input
            name="country"
            value={formData.country}
            onChange={handleChange}
            required
          />
        </FormControl>

        <FormControl>
          <Label>Postal Code</Label>
          <Input
            name="postal_code"
            value={formData.postal_code}
            onChange={handleChange}
            required
          />
        </FormControl>

        <FormControl>
          <Label>Price</Label>
          <Input
            type="number"
            name="price"
            value={formData.price}
            onChange={handleChange}
            required
          />
        </FormControl>

        <FormControl>
          <Label>Bedrooms</Label>
          <Input
            type="number"
            name="bedrooms"
            value={formData.bedrooms}
            onChange={handleChange}
            required
          />
        </FormControl>

        <FormControl>
          <Label>Bathrooms</Label>
          <Input
            type="number"
            name="bathrooms"
            value={formData.bathrooms}
            onChange={handleChange}
            required
          />
        </FormControl>

        <FormControl>
          <Label>Square Meters</Label>
          <Input
            type="number"
            name="square_meters"
            value={formData.square_meters}
            onChange={handleChange}
            required
          />
        </FormControl>

        <FormControl>
          <Label>Year Built</Label>
          <Input
            type="number"
            name="year_built"
            value={formData.year_built || ''}
            onChange={handleChange}
          />
        </FormControl>

        <FormControl>
          <Label>Parking Spots</Label>
          <Input
            type="number"
            name="parking_spots"
            value={formData.parking_spots}
            onChange={handleChange}
            required
          />
        </FormControl>

        <Box>
          <Button type="submit">Submit</Button>
          <Button variant="outline" onClick={onCancel}>
            Cancel
          </Button>
        </Box>
      </VStack>
    </Box>
  );
}
