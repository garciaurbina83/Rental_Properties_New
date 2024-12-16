'use client';

import { ColumnDef } from '@tanstack/react-table';
import { Property, PropertyType, PropertyStatus } from '@/types/property';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Building2, Home, MoreHorizontal } from 'lucide-react';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';

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

export const columns: ColumnDef<Property>[] = [
  {
    accessorKey: 'name',
    header: 'Property',
    cell: ({ row }) => {
      const property = row.original;
      return (
        <div className="flex items-center gap-2">
          <div className="h-8 w-8 rounded-full bg-muted flex items-center justify-center">
            {property.property_type === PropertyType.MAIN ? (
              <Building2 className="h-4 w-4 text-muted-foreground" />
            ) : (
              <Home className="h-4 w-4 text-muted-foreground" />
            )}
          </div>
          <span className="font-medium">{property.name}</span>
        </div>
      );
    },
  },
  {
    accessorKey: 'address',
    header: 'Address',
    cell: ({ row }) => {
      const property = row.original;
      return (
        <div className="text-sm text-muted-foreground">
          {property.address}, {property.city}, {property.state} {property.zip_code}
        </div>
      );
    },
  },
  {
    accessorKey: 'status',
    header: 'Status',
    cell: ({ row }) => {
      const status = row.getValue('status') as PropertyStatus;
      return (
        <Badge className={getStatusColor(status)}>
          {status}
        </Badge>
      );
    },
  },
  {
    accessorKey: 'bedrooms',
    header: 'Beds',
    cell: ({ row }) => {
      const bedrooms = row.getValue('bedrooms');
      return (
        <div className="text-sm text-muted-foreground">
          {bedrooms || '-'}
        </div>
      );
    },
  },
  {
    accessorKey: 'bathrooms',
    header: 'Baths',
    cell: ({ row }) => {
      const bathrooms = row.getValue('bathrooms');
      return (
        <div className="text-sm text-muted-foreground">
          {bathrooms || '-'}
        </div>
      );
    },
  },
  {
    id: 'actions',
    cell: ({ row }) => {
      const property = row.original;
      return (
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
              {property.property_type === PropertyType.MAIN && (
                <DropdownMenuItem 
                  onClick={() => window.dispatchEvent(new CustomEvent('ADD_UNIT', { detail: property.id }))}
                >
                  Add unit
                </DropdownMenuItem>
              )}
              <DropdownMenuItem 
                onClick={() => window.dispatchEvent(new CustomEvent('EDIT_PROPERTY', { detail: property }))}
              >
                Edit property
              </DropdownMenuItem>
              <DropdownMenuItem 
                onClick={() => window.dispatchEvent(new CustomEvent('DELETE_PROPERTY', { detail: property }))}
                className="text-red-600 focus:text-red-600"
              >
                Delete property
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      );
    },
  },
];
