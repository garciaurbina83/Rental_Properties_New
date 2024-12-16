'use client';

import { ArrowUpIcon, ArrowDownIcon } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { cn } from "@/lib/utils";

interface StatsCardProps {
  title: string;
  amount: string;
  trend: number;
  type: "earning" | "spending" | "neutral";
  Icon?: React.ElementType;
  subtext?: string;
}

export default function StatsCard({ title, amount, trend, type, Icon, subtext }: StatsCardProps) {
  return (
    <Card className="gradient-card border-0 relative overflow-hidden group transition-all duration-300 hover:translate-y-[-2px]">
      <div className={cn(
        "absolute inset-0 opacity-10 transition-opacity duration-300 group-hover:opacity-20",
        type === "earning" 
          ? "bg-gradient-to-br from-emerald-500 to-emerald-700"
          : type === "spending" 
            ? "bg-gradient-to-br from-rose-500 to-rose-700"
            : "bg-gradient-to-br from-gray-500 to-gray-700"
      )} />
      <CardContent className="p-6">
        <div className="flex flex-col space-y-1">
          <div className="flex items-center gap-2">
            {Icon && <Icon className="h-5 w-5 text-muted-foreground" />}
            <p className="text-sm font-medium text-muted-foreground">{title}</p>
          </div>
          <div className="flex items-center justify-between">
            <h2 className="text-2xl font-bold tracking-tight">
              {type === "earning" ? "+" : type === "spending" ? "-" : ""}${amount}
            </h2>
            <span
              className={cn(
                "flex items-center gap-1 text-sm font-medium transition-colors",
                trend > 0
                  ? "text-emerald-400"
                  : "text-rose-400"
              )}
            >
              {trend > 0 ? (
                <ArrowUpIcon className="h-4 w-4" />
              ) : (
                <ArrowDownIcon className="h-4 w-4" />
              )}
              {Math.abs(trend)}%
            </span>
          </div>
          {subtext && (
            <p className="text-sm font-medium text-muted-foreground">{subtext}</p>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
