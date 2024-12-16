'use client';

import { Tenant } from '@/app/tenants/types';
import { Card, CardContent, CardFooter, CardHeader } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Edit, MoreHorizontal, Trash, User } from 'lucide-react';
import { format } from 'date-fns';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';

interface TenantsGridProps {
  tenants: Tenant[];
  isLoading?: boolean;
  onEdit: (tenant: Tenant) => void;
  onDelete: (tenant: Tenant) => void;
}

export function TenantsGrid({ tenants, isLoading, onEdit, onDelete }: TenantsGridProps) {
  if (isLoading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {[...Array(6)].map((_, i) => (
          <Card key={i} className="animate-pulse">
            <CardHeader className="h-[100px] bg-muted" />
            <CardContent className="py-4">
              <div className="h-4 w-3/4 bg-muted rounded mb-2" />
              <div className="h-4 w-1/2 bg-muted rounded" />
            </CardContent>
          </Card>
        ))}
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {tenants.map((tenant) => (
        <Card key={tenant.id} className="overflow-hidden transition-all duration-200 hover:shadow-lg">
          <CardHeader className="p-4">
            <div className="flex items-center gap-3">
              <div className="h-10 w-10 rounded-full bg-muted flex items-center justify-center">
                <User className="h-5 w-5 text-muted-foreground" />
              </div>
              <div>
                <h3 className="font-semibold">{tenant.first_name} {tenant.last_name}</h3>
                <p className="text-sm text-muted-foreground">ID: {tenant.id}</p>
              </div>
            </div>
          </CardHeader>
          <CardContent className="p-4 pt-0">
            <div className="space-y-2">
              <div>
                <p className="text-sm font-medium">Lease Period</p>
                <p className="text-sm text-muted-foreground">
                  {format(new Date(tenant.lease_start), 'MMM d, yyyy')} - 
                  {format(new Date(tenant.lease_end), 'MMM d, yyyy')}
                </p>
              </div>
              <div>
                <p className="text-sm font-medium">Monthly Rent</p>
                <p className="text-sm text-muted-foreground">
                  ${tenant.monthly_rent.toLocaleString()}
                  <span className="text-xs ml-1">
                    (Due: {tenant.payment_day}{getDayOfMonthSuffix(tenant.payment_day)})
                  </span>
                </p>
              </div>
              <div>
                <p className="text-sm font-medium">Security Deposit</p>
                <p className="text-sm text-muted-foreground">
                  ${tenant.deposit.toLocaleString()}
                </p>
              </div>
            </div>
          </CardContent>
          <CardFooter className="p-4 pt-0 flex justify-end">
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="ghost" size="icon">
                  <MoreHorizontal className="h-4 w-4" />
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end">
                <DropdownMenuLabel>Actions</DropdownMenuLabel>
                <DropdownMenuItem onClick={() => onEdit(tenant)}>
                  <Edit className="mr-2 h-4 w-4" />
                  Edit tenant
                </DropdownMenuItem>
                <DropdownMenuSeparator />
                <DropdownMenuItem 
                  onClick={() => onDelete(tenant)}
                  className="text-red-600 focus:text-red-600"
                >
                  <Trash className="mr-2 h-4 w-4" />
                  Delete tenant
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </CardFooter>
        </Card>
      ))}
    </div>
  );
}

function getDayOfMonthSuffix(day: number) {
  if (day >= 11 && day <= 13) {
    return 'th';
  }
  switch (day % 10) {
    case 1:  return 'st';
    case 2:  return 'nd';
    case 3:  return 'rd';
    default: return 'th';
  }
}
