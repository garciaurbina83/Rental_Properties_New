'use client';

import { Property } from "@/types/property";
import PropertyCard from "./property-card";

interface PropertiesGridProps {
  properties: Property[];
  onEdit?: (property: Property) => void;
  onDelete?: (property: Property) => void;
  onClick?: (property: Property) => void;
}

export default function PropertiesGrid({ 
  properties,
  onEdit,
  onDelete,
  onClick
}: PropertiesGridProps) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
      {properties.map((property) => (
        <PropertyCard
          key={property.id}
          property={property}
          onEdit={onEdit}
          onDelete={onDelete}
          onClick={onClick}
        />
      ))}
    </div>
  );
}
