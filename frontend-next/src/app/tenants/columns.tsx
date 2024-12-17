'use client';

import { useState, useEffect } from 'react';
import { ColumnDef } from "@tanstack/react-table"
import { Tenant } from "./types"
import { Button } from "@/components/ui/button"
import { format } from "date-fns"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { MoreHorizontal, User } from "lucide-react"
import { propertyService } from "@/services/propertyService"
import { useProperty } from '@/hooks/useProperty';
import { DataTableColumnHeader } from '@/components/ui/data-table-column-header';

export const columns: ColumnDef<Tenant>[] = [
  {
    accessorKey: "first_name",
    enableSorting: true,
    header: ({ column }) => (
      <DataTableColumnHeader column={column} title="Tenant" />
    ),
    cell: ({ row }) => {
      const tenant = row.original;
      return (
        <div className="flex items-center gap-2">
          <div className="h-8 w-8 rounded-full bg-orange-500/10 flex items-center justify-center">
            <User className="h-4 w-4 text-orange-500" />
          </div>
          <div className="flex flex-col">
            <span className="font-medium">{tenant.first_name} {tenant.last_name}</span>
            <span className="text-xs text-muted-foreground">
              ID: {tenant.id}
            </span>
          </div>
        </div>
      );
    },
  },
  {
    accessorKey: "property_id",
    enableSorting: true,
    header: ({ column }) => (
      <DataTableColumnHeader column={column} title="Property" />
    ),
    cell: ({ row }) => {
      const propertyId = row.getValue("property_id") as number;
      const { property, parentProperty, isLoading } = useProperty(propertyId);

      if (isLoading) {
        return <span className="text-muted-foreground">Loading...</span>;
      }

      if (!property) {
        return <span className="text-muted-foreground">-</span>;
      }

      // Si es una unidad, mostrar la dirección del edificio principal
      if (property.property_type === 'UNIT' && parentProperty) {
        return (
          <div className="flex flex-col">
            <span className="font-medium">{parentProperty.address}</span>
          </div>
        );
      }

      // Si es una propiedad principal, mostrar su dirección
      return (
        <div className="flex flex-col">
          <span className="font-medium">{property.address}</span>
        </div>
      );
    },
  },
  {
    id: "unit",
    enableSorting: true,
    header: ({ column }) => (
      <DataTableColumnHeader column={column} title="Unit" />
    ),
    cell: ({ row }) => {
      const propertyId = row.getValue("property_id") as number;
      const { property, isLoading } = useProperty(propertyId);

      if (isLoading) {
        return <span className="text-muted-foreground">Loading...</span>;
      }

      if (!property || property.property_type !== 'UNIT') {
        return <span className="text-muted-foreground">-</span>;
      }

      return (
        <div className="flex items-center">
          <span className="font-medium">{property.name}</span>
        </div>
      );
    },
  },
  {
    accessorKey: "lease_start",
    enableSorting: true,
    header: ({ column }) => (
      <DataTableColumnHeader column={column} title="Lease Period" />
    ),
    cell: ({ row }) => {
      const startDate = row.getValue("lease_start") as string;
      const endDate = row.original.lease_end as string;
      return (
        <div className="text-sm">
          <div className="text-muted-foreground">
            {startDate ? format(new Date(startDate), "MMM d, yyyy") : "-"} - 
            {endDate ? format(new Date(endDate), "MMM d, yyyy") : "-"}
          </div>
        </div>
      );
    },
  },
  {
    accessorKey: "monthly_rent",
    enableSorting: true,
    header: ({ column }) => (
      <DataTableColumnHeader column={column} title="Rent" />
    ),
    cell: ({ row }) => {
      const rent = parseFloat(row.getValue("monthly_rent"));
      return (
        <div className="flex items-center">
          <span className="font-medium">
            ${rent.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
          </span>
        </div>
      );
    },
  },
  {
    accessorKey: "deposit",
    enableSorting: true,
    header: ({ column }) => (
      <DataTableColumnHeader column={column} title="Deposit" />
    ),
    cell: ({ row }) => {
      const deposit = parseFloat(row.getValue("deposit"));
      return (
        <div className="flex items-center">
          <span className="font-medium">
            ${deposit.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
          </span>
        </div>
      );
    },
  },
  {
    id: "actions",
    header: "",
    cell: ({ row }) => {
      const tenant = row.original;
      return (
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="ghost" className="h-8 w-8 p-0">
              <span className="sr-only">Open menu</span>
              <MoreHorizontal className="h-4 w-4" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end">
            <DropdownMenuLabel>Actions</DropdownMenuLabel>
            <DropdownMenuItem onClick={() => navigator.clipboard.writeText(tenant.id.toString())}>
              Copy tenant ID
            </DropdownMenuItem>
            <DropdownMenuSeparator />
            <DropdownMenuItem onClick={() => window.dispatchEvent(new CustomEvent('EDIT_TENANT', { detail: tenant }))}>
              Edit tenant
            </DropdownMenuItem>
            <DropdownMenuItem 
              onClick={() => window.dispatchEvent(new CustomEvent('DELETE_TENANT', { detail: tenant }))}
              className="text-red-600"
            >
              Delete tenant
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      );
    },
  },
];

function getDayOfMonthSuffix(day: number) {
  if (day >= 11 && day <= 13) {
    return "th"
  }
  switch (day % 10) {
    case 1:
      return "st"
    case 2:
      return "nd"
    case 3:
      return "rd"
    default:
      return "th"
  }
}
