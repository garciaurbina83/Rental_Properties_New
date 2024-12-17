'use client';

import { Property, PropertyType, PropertyStatus } from "@/types/property";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardFooter, CardHeader } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Edit, Trash2, Home, Building2, Bath, BedDouble, DoorClosed } from "lucide-react";
import { useParentProperty } from "@/hooks/useParentProperty";

const formatDate = (dateString: string) => {
  const date = new Date(dateString);
  return new Intl.DateTimeFormat('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  }).format(date);
};

interface PropertiesGridProps {
  properties: Property[];
  onEdit: (property: Property) => void;
  onDelete: (property: Property) => void;
}

const getStatusColor = (status: PropertyStatus) => {
  switch (status) {
    case PropertyStatus.AVAILABLE:
      return "bg-green-500/10 text-green-500 hover:bg-green-500/20";
    case PropertyStatus.RENTED:
      return "bg-blue-500/10 text-blue-500 hover:bg-blue-500/20";
    case PropertyStatus.MAINTENANCE:
      return "bg-yellow-500/10 text-yellow-500 hover:bg-yellow-500/20";
    case PropertyStatus.UNAVAILABLE:
      return "bg-red-500/10 text-red-500 hover:bg-red-500/20";
    default:
      return "bg-gray-500/10 text-gray-500 hover:bg-gray-500/20";
  }
};

const PropertyCard = ({ property, onEdit, onDelete }: { 
  property: Property; 
  onEdit: (property: Property) => void; 
  onDelete: (property: Property) => void; 
}) => {
  const { parentProperty } = useParentProperty(
    property.parent_property_id,
    property.property_type
  );

  return (
    <Card key={property.id} className="overflow-hidden">
      <CardHeader className="p-4 pb-2">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            {property.property_type === PropertyType.PRINCIPAL ? (
              <Building2 className="h-4 w-4 text-blue-500" />
            ) : (
              <DoorClosed className="h-4 w-4 text-green-500" />
            )}
            <h3 className="font-semibold">{property.name || 'No name'}</h3>
          </div>
          <Badge className={getStatusColor(property.status)}>
            {property.status}
          </Badge>
        </div>
      </CardHeader>
      <CardContent className="p-4 pt-2">
        <div className="space-y-2">
          <div className="flex flex-col">
            <div className="text-sm">
              {property.address}, {property.city}, {property.state} {property.zip_code}
            </div>
            {property.property_type === PropertyType.UNIT && parentProperty && (
              <div className="text-xs text-muted-foreground mt-1">
                Building: {parentProperty.address}, {parentProperty.city}
              </div>
            )}
          </div>
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-1 text-sm">
              <BedDouble className="h-4 w-4 text-purple-500" />
              <span>{property.bedrooms || 0} beds</span>
            </div>
            <div className="flex items-center gap-1 text-sm">
              <Bath className="h-4 w-4 text-orange-500" />
              <span>{property.bathrooms || 0} baths</span>
            </div>
          </div>
          <div className="text-xs text-muted-foreground">
            Last updated: {formatDate(property.updated_at)}
          </div>
        </div>
      </CardContent>
      <CardFooter className="p-4 pt-0 flex justify-end gap-2">
        <Button
          variant="ghost"
          size="sm"
          onClick={() => onEdit(property)}
          className="h-8"
        >
          <Edit className="h-4 w-4 text-blue-500" />
        </Button>
        <Button
          variant="ghost"
          size="sm"
          onClick={() => onDelete(property)}
          className="h-8 text-red-600 hover:text-red-600"
        >
          <Trash2 className="h-4 w-4 text-red-500" />
        </Button>
      </CardFooter>
    </Card>
  );
};

export function PropertiesGrid({ properties, onEdit, onDelete }: PropertiesGridProps) {
  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
      {properties.map((property) => (
        <PropertyCard
          key={property.id}
          property={property}
          onEdit={onEdit}
          onDelete={onDelete}
        />
      ))}
    </div>
  );
}
