'use client';

import { Card } from "@/components/ui/card";
import { ArrowUpRight, ArrowDownRight, TrendingUp } from "lucide-react";
import { cn } from "@/lib/utils";

type PropertyPerformance = {
  id: number;
  name: string;
  location: string;
  occupancyRate: number;
  monthlyRevenue: number;
  revenueChange: number;
  maintenanceCosts: number;
  roi: number;
};

export default function PropertyPerformance() {
  const properties: PropertyPerformance[] = [
    {
      id: 1,
      name: "Apartamento 301",
      location: "Zona Norte",
      occupancyRate: 100,
      monthlyRevenue: 1500,
      revenueChange: 5.2,
      maintenanceCosts: 150,
      roi: 8.5,
    },
    {
      id: 2,
      name: "Casa 123",
      location: "Zona Sur",
      occupancyRate: 100,
      monthlyRevenue: 2000,
      revenueChange: -2.1,
      maintenanceCosts: 300,
      roi: 7.2,
    },
    {
      id: 3,
      name: "Local Comercial 45",
      location: "Centro",
      occupancyRate: 100,
      monthlyRevenue: 3000,
      revenueChange: 8.4,
      maintenanceCosts: 200,
      roi: 12.5,
    },
  ];

  return (
    <Card className="p-6">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-lg font-medium">Rendimiento por Propiedad</h3>
        <TrendingUp className="h-5 w-5 text-muted-foreground" />
      </div>
      <div className="space-y-4">
        {properties.map((property) => (
          <div
            key={property.id}
            className="p-4 rounded-lg hover:bg-accent/5 transition-colors"
          >
            <div className="flex items-start justify-between mb-2">
              <div>
                <h4 className="font-medium">{property.name}</h4>
                <p className="text-sm text-muted-foreground">{property.location}</p>
              </div>
              <div className="text-right">
                <div className="font-medium">${property.monthlyRevenue}</div>
                <div className="flex items-center text-sm">
                  {property.revenueChange > 0 ? (
                    <>
                      <ArrowUpRight className="h-4 w-4 text-green-500" />
                      <span className="text-green-500">
                        {property.revenueChange}%
                      </span>
                    </>
                  ) : (
                    <>
                      <ArrowDownRight className="h-4 w-4 text-red-500" />
                      <span className="text-red-500">
                        {property.revenueChange}%
                      </span>
                    </>
                  )}
                </div>
              </div>
            </div>
            <div className="grid grid-cols-3 gap-4 mt-4">
              <div>
                <p className="text-sm text-muted-foreground">Ocupación</p>
                <p className="font-medium">{property.occupancyRate}%</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Mantenimiento</p>
                <p className="font-medium">${property.maintenanceCosts}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">ROI</p>
                <p className="font-medium">{property.roi}%</p>
              </div>
            </div>
          </div>
        ))}
      </div>
    </Card>
  );
}
