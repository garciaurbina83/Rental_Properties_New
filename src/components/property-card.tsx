'use client';

import { Property } from "@/types/property";
import { Card, CardContent, CardFooter, CardHeader } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Bed, Bath, Car, Maximize, Edit, Trash } from "lucide-react";
import Image from "next/image";
import { cn } from "@/lib/utils";

interface PropertyCardProps {
  property: Property;
  onEdit?: (property: Property) => void;
  onDelete?: (property: Property) => void;
  onClick?: (property: Property) => void;
}

const statusColors = {
  available: "bg-green-500/10 text-green-500",
  occupied: "bg-blue-500/10 text-blue-500",
  maintenance: "bg-yellow-500/10 text-yellow-500",
};

const statusText = {
  available: "Disponible",
  occupied: "Ocupado",
  maintenance: "Mantenimiento",
};

export default function PropertyCard({ 
  property, 
  onEdit, 
  onDelete,
  onClick 
}: PropertyCardProps) {
  const defaultImage = "/mock/properties/default-property.jpg";
  const imageUrl = property.images[0] || defaultImage;

  return (
    <Card 
      className={cn(
        "overflow-hidden transition-all duration-200",
        onClick && "cursor-pointer hover:shadow-lg"
      )}
      onClick={() => onClick?.(property)}
    >
      <CardHeader className="p-0">
        <div className="relative aspect-video w-full overflow-hidden">
          <Image
            src={imageUrl}
            alt={property.name}
            fill
            className="object-cover"
            sizes="(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw"
          />
          <Badge 
            className={cn(
              "absolute top-2 right-2",
              statusColors[property.status]
            )}
          >
            {statusText[property.status]}
          </Badge>
        </div>
      </CardHeader>
      <CardContent className="p-4">
        <div className="mb-2">
          <h3 className="font-semibold truncate">{property.name}</h3>
          <p className="text-sm text-muted-foreground truncate">
            {property.address.street}, {property.address.city}
          </p>
        </div>
        <div className="flex items-center gap-4 text-sm text-muted-foreground">
          <div className="flex items-center gap-1">
            <Bed className="h-4 w-4" />
            <span>{property.features.bedrooms}</span>
          </div>
          <div className="flex items-center gap-1">
            <Bath className="h-4 w-4" />
            <span>{property.features.bathrooms}</span>
          </div>
          <div className="flex items-center gap-1">
            <Car className="h-4 w-4" />
            <span>{property.features.parking}</span>
          </div>
          <div className="flex items-center gap-1">
            <Maximize className="h-4 w-4" />
            <span>{property.features.squareMeters}m²</span>
          </div>
        </div>
      </CardContent>
      <CardFooter className="p-4 pt-0 flex justify-between items-center">
        <p className="font-semibold">
          ${property.price.toLocaleString()}
        </p>
        <div className="flex gap-2">
          {onEdit && (
            <Button
              variant="ghost"
              size="icon"
              onClick={(e) => {
                e.stopPropagation();
                onEdit(property);
              }}
            >
              <Edit className="h-4 w-4" />
            </Button>
          )}
          {onDelete && (
            <Button
              variant="ghost"
              size="icon"
              onClick={(e) => {
                e.stopPropagation();
                onDelete(property);
              }}
            >
              <Trash className="h-4 w-4" />
            </Button>
          )}
        </div>
      </CardFooter>
    </Card>
  );
}
