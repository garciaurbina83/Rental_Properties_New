'use client';

import { Card } from "@/components/ui/card";

interface StatCardProps {
  title: string;
  value: string;
  description?: string;
  icon?: React.ReactNode;
  trend?: {
    value: number;
    isPositive: boolean;
  };
  className?: string;
}

export function StatCard({
  title,
  value,
  description,
  icon,
  trend,
  className,
}: StatCardProps) {
  return (
    <Card className={`p-6 bg-secondary ${className}`}>
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium text-muted-foreground">{title}</p>
          <div className="flex items-baseline gap-2">
            <h2 className="text-2xl font-bold">{value}</h2>
            {trend && (
              <span className={
                trend.isPositive ? "text-xs font-medium text-green-500" : "text-xs font-medium text-red-500"
              }>
                {trend.isPositive ? "+" : "-"}{trend.value}%
              </span>
            )}
          </div>
          {description && (
            <p className="text-sm text-muted-foreground">{description}</p>
          )}
        </div>
        {icon && (
          <div className="text-muted-foreground">
            {icon}
          </div>
        )}
      </div>
    </Card>
  );
}
