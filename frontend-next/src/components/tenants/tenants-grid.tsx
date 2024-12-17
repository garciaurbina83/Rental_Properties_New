'use client';

import { Tenant } from "@/app/tenants/types";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardFooter, CardHeader } from "@/components/ui/card";
import { Edit, Trash2, User, Calendar, DollarSign } from "lucide-react";
import { format } from "date-fns";

const formatCurrency = (amount: string) => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD'
  }).format(parseFloat(amount));
};

interface TenantsGridProps {
  tenants: Tenant[];
  onEdit: (tenant: Tenant) => void;
  onDelete: (tenant: Tenant) => void;
}

export function TenantsGrid({ tenants, onEdit, onDelete }: TenantsGridProps) {
  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
      {tenants.map((tenant) => (
        <Card key={tenant.id} className="overflow-hidden">
          <CardHeader className="p-4 pb-2">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <User className="h-4 w-4 text-muted-foreground" />
                <h3 className="font-semibold">{tenant.first_name} {tenant.last_name}</h3>
              </div>
            </div>
          </CardHeader>
          <CardContent className="p-4 pt-2">
            <div className="space-y-2">
              <div className="text-sm text-muted-foreground">
                Property ID: {tenant.property_id}
              </div>
              <div className="flex items-center gap-4">
                <div className="flex items-center gap-1 text-sm">
                  <Calendar className="h-4 w-4 text-muted-foreground" />
                  <span>
                    {format(new Date(tenant.lease_start), "MMM d, yyyy")} - {format(new Date(tenant.lease_end), "MMM d, yyyy")}
                  </span>
                </div>
              </div>
              <div className="flex items-center gap-4">
                <div className="flex items-center gap-1 text-sm">
                  <DollarSign className="h-4 w-4 text-muted-foreground" />
                  <span>Rent: {formatCurrency(tenant.monthly_rent)}</span>
                </div>
              </div>
              <div className="text-xs text-muted-foreground">
                Payment Day: {tenant.payment_day}{getDayOfMonthSuffix(tenant.payment_day)}
              </div>
            </div>
          </CardContent>
          <CardFooter className="p-4 pt-0 flex justify-end gap-2">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => onEdit(tenant)}
              className="h-8"
            >
              <Edit className="h-4 w-4" />
            </Button>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => onDelete(tenant)}
              className="h-8 text-red-600 hover:text-red-600"
            >
              <Trash2 className="h-4 w-4" />
            </Button>
          </CardFooter>
        </Card>
      ))}
    </div>
  );
}

function getDayOfMonthSuffix(day: number) {
  if (day >= 11 && day <= 13) {
    return "th";
  }
  switch (day % 10) {
    case 1:
      return "st";
    case 2:
      return "nd";
    case 3:
      return "rd";
    default:
      return "th";
  }
}
