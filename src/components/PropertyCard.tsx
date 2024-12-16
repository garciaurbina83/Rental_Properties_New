'use client';

import Link from 'next/link';
import { Property } from '@/schemas/property';
import { OptimizedImage } from './OptimizedImage';
import { usePrefetch } from '@/hooks/usePrefetch';
import { formatPrice } from '@/utils/formatters';

interface PropertyCardProps {
  property: Property;
}

export default function PropertyCard({ property }: PropertyCardProps) {
  const { ref } = usePrefetch(`/properties/${property.id}`);

  return (
    <Link
      href={`/properties/${property.id}`}
      ref={ref}
      className="group block rounded-lg overflow-hidden shadow-lg hover:shadow-xl transition-shadow duration-300"
    >
      <div className="relative">
        <OptimizedImage
          src={property.images[0]}
          alt={property.name}
          width={400}
          height={300}
          className="w-full h-[250px] object-cover"
        />
        <div className="absolute top-2 right-2 bg-white px-2 py-1 rounded-full text-sm font-semibold">
          {property.status}
        </div>
      </div>
      
      <div className="p-4">
        <h3 className="text-lg font-semibold mb-2 group-hover:text-primary transition-colors">
          {property.name}
        </h3>
        
        <div className="flex justify-between items-center mb-2">
          <span className="text-xl font-bold text-primary">
            {formatPrice(property.price)}
          </span>
          <span className="text-sm text-gray-600">
            {property.type}
          </span>
        </div>
        
        <div className="flex items-center text-sm text-gray-600 space-x-4">
          <span>{property.features.bedrooms} beds</span>
          <span>{property.features.bathrooms} baths</span>
          <span>{property.features.area} sqft</span>
        </div>
      </div>
    </Link>
  );
}
