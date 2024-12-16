'use client';

import { useState } from 'react';
import { Property } from "@/types/property";
import { Card } from "@/components/ui/card";
import { PropertiesHeader } from "./properties-header";
import { PropertyItem } from "./property-item";

type SortConfig = {
  key: 'name' | 'address' | 'status' | 'bedrooms' | 'bathrooms' | 'updated_at';
  direction: 'asc' | 'desc';
} | null;

interface PropertiesTableProps {
  properties: Property[];
  onEdit: (property: Property) => void;
  onDelete: (property: Property) => void;
}

export function PropertiesTable({ properties, onEdit, onDelete }: PropertiesTableProps) {
  const [sortConfig, setSortConfig] = useState<SortConfig>(null);

  const handleSort = (key: SortConfig['key']) => {
    setSortConfig((currentConfig) => {
      if (!currentConfig || currentConfig.key !== key) {
        return { key, direction: 'asc' };
      }
      if (currentConfig.direction === 'asc') {
        return { key, direction: 'desc' };
      }
      return null;
    });
  };

  const sortedProperties = [...properties].sort((a, b) => {
    if (!sortConfig) return 0;

    const { key, direction } = sortConfig;
    let aValue = a[key];
    let bValue = b[key];

    if (key === 'bedrooms' || key === 'bathrooms') {
      aValue = aValue || 0;
      bValue = bValue || 0;
    }

    if (aValue < bValue) return direction === 'asc' ? -1 : 1;
    if (aValue > bValue) return direction === 'asc' ? 1 : -1;
    return 0;
  });

  return (
    <Card>
      <PropertiesHeader handleSort={handleSort} sortConfig={sortConfig} />
      <div className="divide-y">
        {sortedProperties.map((property) => (
          <PropertyItem
            key={property.id}
            property={property}
            onEdit={onEdit}
            onDelete={onDelete}
          />
        ))}
      </div>
    </Card>
  );
}
