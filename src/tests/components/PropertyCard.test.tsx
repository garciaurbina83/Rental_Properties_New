import React from 'react';
import { render, screen } from '../test-utils';
import PropertyCard from '@/components/PropertyCard';
import { formatPrice } from '@/utils/formatters';

const mockProperty = {
  id: '1',
  name: 'Test Property',
  description: 'A test property description',
  price: 1000000,
  status: 'For Sale',
  type: 'House',
  images: ['test-image.jpg'],
  features: {
    bedrooms: 3,
    bathrooms: 2,
    area: 2000,
  },
  location: {
    address: '123 Test St',
    city: 'Test City',
    state: 'TS',
    zipCode: '12345',
  },
  created_at: '2024-01-01T00:00:00Z',
  updated_at: '2024-01-01T00:00:00Z',
};

jest.mock('next/navigation', () => ({
  useRouter: () => ({
    prefetch: jest.fn(),
  }),
}));

describe('PropertyCard', () => {
  it('renders property information correctly', () => {
    render(<PropertyCard property={mockProperty} />);
    
    expect(screen.getByText(mockProperty.name)).toBeInTheDocument();
    expect(screen.getByText(formatPrice(mockProperty.price))).toBeInTheDocument();
    expect(screen.getByText(mockProperty.status)).toBeInTheDocument();
    expect(screen.getByText(mockProperty.type)).toBeInTheDocument();
    expect(screen.getByText(`${mockProperty.features.bedrooms} beds`)).toBeInTheDocument();
    expect(screen.getByText(`${mockProperty.features.bathrooms} baths`)).toBeInTheDocument();
    expect(screen.getByText(`${mockProperty.features.area} sqft`)).toBeInTheDocument();
  });

  it('renders optimized image with correct props', () => {
    render(<PropertyCard property={mockProperty} />);
    
    const image = screen.getByRole('img');
    expect(image).toHaveAttribute('src', expect.stringContaining(mockProperty.images[0]));
    expect(image).toHaveAttribute('alt', mockProperty.name);
    expect(image).toHaveAttribute('loading', 'lazy');
  });

  it('applies hover styles correctly', () => {
    render(<PropertyCard property={mockProperty} />);
    
    const link = screen.getByRole('link');
    expect(link).toHaveClass('group');
    expect(link).toHaveAttribute('href', `/properties/${mockProperty.id}`);
  });
});
