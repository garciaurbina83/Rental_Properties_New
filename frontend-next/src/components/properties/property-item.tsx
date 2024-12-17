'use client';

import { Property, PropertyType, PropertyStatus } from "@/types/property";
import { Building2, Home, MoreHorizontal } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Button } from "@/components/ui/button";

interface PropertyItemProps {
  property: Property;
  onEdit: (property: Property) => void;
  onDelete: (property: Property) => void;
}

export const PropertyItem = ({ property, onEdit, onDelete }: PropertyItemProps) => {
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

  return (
    <div className="grid grid-cols-7 gap-4 px-6 py-4 hover:bg-muted/50 transition-colors duration-200">
      <div className="flex items-center gap-3">
        <div className="h-8 w-8 rounded-full bg-muted flex items-center justify-center">
          {property.property_type === PropertyType.MAIN ? (
            <Building2 className="h-4 w-4 text-muted-foreground" />
          ) : (
            <Home className="h-4 w-4 text-muted-foreground" />
          )}
        </div>
        <span className="text-sm font-medium">{property.name}</span>
      </div>
      <div className="text-sm text-muted-foreground self-center col-span-2">
        {property.address}, {property.city}, {property.state} {property.zip_code}
      </div>
      <div className="self-center">
        <Badge className={getStatusColor(property.status)}>
          {property.status}
        </Badge>
      </div>
      <div className="text-sm text-muted-foreground self-center">
        {property.bedrooms || '-'}
      </div>
      <div className="text-sm text-muted-foreground self-center">
        {property.bathrooms || '-'}
      </div>
      <div className="flex justify-end">
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="ghost" className="h-8 w-8 p-0">
              <span className="sr-only">Open menu</span>
              <MoreHorizontal className="h-4 w-4" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end">
            <DropdownMenuLabel>Actions</DropdownMenuLabel>
            <DropdownMenuSeparator />
            <DropdownMenuItem onClick={() => onEdit(property)}>
              Edit property
            </DropdownMenuItem>
            <DropdownMenuItem 
              onClick={() => onDelete(property)}
              className="text-red-600 focus:text-red-600"
            >
              Delete property
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
    </div>
  );
};
