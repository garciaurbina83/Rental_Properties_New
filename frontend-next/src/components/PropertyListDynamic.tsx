'use client';

import dynamic from 'next/dynamic';
import { Suspense } from 'react';
import { Property } from '@/schemas/property';

// Carga dinámica del componente PropertyCard
const PropertyCard = dynamic(() => import('./PropertyCard'), {
  loading: () => <PropertyCardSkeleton />,
  ssr: false,
});

interface PropertyListProps {
  properties: Property[];
  isLoading: boolean;
}

function PropertyCardSkeleton() {
  return (
    <div className="animate-pulse bg-gray-200 rounded-lg p-4 h-[300px]">
      <div className="bg-gray-300 h-40 rounded-lg mb-4"></div>
      <div className="space-y-3">
        <div className="h-4 bg-gray-300 rounded w-3/4"></div>
        <div className="h-4 bg-gray-300 rounded w-1/2"></div>
      </div>
    </div>
  );
}

export function PropertyListDynamic({ properties, isLoading }: PropertyListProps) {
  if (isLoading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {[...Array(6)].map((_, index) => (
          <PropertyCardSkeleton key={index} />
        ))}
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {properties.map((property) => (
        <Suspense key={property.id} fallback={<PropertyCardSkeleton />}>
          <PropertyCard property={property} />
        </Suspense>
      ))}
    </div>
  );
}
