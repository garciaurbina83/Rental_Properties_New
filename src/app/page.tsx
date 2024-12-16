'use client';

import { Command, CommandInput } from "@/components/ui/command";
import { Button } from "@/components/ui/button";
import { 
  Sun, 
  Bell, 
  Mail,
  Plus,
  FileText,
  Wrench,
  AlertTriangle,
  DollarSign,
  Percent,
  Building2,
  Users,
  CalendarClock,
  ArrowUpRight,
  ArrowDownRight,
  Clock
} from "lucide-react";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { StatCard } from "@/components/stat-card";
import { RevenueChart } from "@/components/revenue-chart";
import { PropertiesChart } from "@/components/properties-chart";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

export default function DashboardPage() {
  return (
    <div className="flex-1 space-y-4 p-4 md:p-8 pt-6">
      <div className="flex items-center justify-between">
        <h2 className="text-3xl font-bold tracking-tight">Dashboard</h2>
      </div>
      
      {/* Stats Cards */}
      <div className="grid gap-4 grid-cols-1 md:grid-cols-2 lg:grid-cols-3">
        <StatCard
          title="Revenue YTD"
          value="$245,500"
          trend={{ value: 12.5, isPositive: true }}
          icon={<DollarSign className="h-6 w-6" />}
          description="Compared to last year"
        />
        <StatCard
          title="Expenses YTD"
          value="$82,300"
          trend={{ value: 8.2, isPositive: false }}
          icon={<ArrowDownRight className="h-6 w-6" />}
          description="Compared to last year"
        />
        <StatCard
          title="Net Income YTD"
          value="$163,200"
          trend={{ value: 15.3, isPositive: true }}
          icon={<ArrowUpRight className="h-6 w-6" />}
          description="Compared to last year"
        />
      </div>

      {/* Charts */}
      <div className="grid gap-4 grid-cols-1 md:grid-cols-2 lg:grid-cols-7">
        <div className="col-span-4">
          <RevenueChart />
        </div>
        <div className="col-span-3">
          <PropertiesChart />
        </div>
      </div>

      {/* Tasks and Events */}
      <div className="grid gap-4 grid-cols-1 lg:grid-cols-2">
        <Card className="p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold">Recent Tasks</h3>
            <Badge variant="outline" className="text-xs">5 pending</Badge>
          </div>
          <div className="space-y-4">
            <div className="flex items-center gap-4">
              <CalendarClock className="h-4 w-4 text-muted-foreground" />
              <div className="flex-1">
                <p className="text-sm font-medium">Property inspection at 123 Main St</p>
                <p className="text-xs text-muted-foreground">Due in 2 days</p>
              </div>
              <Badge>High</Badge>
            </div>
            <div className="flex items-center gap-4">
              <CalendarClock className="h-4 w-4 text-muted-foreground" />
              <div className="flex-1">
                <p className="text-sm font-medium">Lease renewal for Unit 4B</p>
                <p className="text-xs text-muted-foreground">Due in 5 days</p>
              </div>
              <Badge>Medium</Badge>
            </div>
          </div>
        </Card>

        <Card className="p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold">Upcoming Events</h3>
            <Badge variant="outline" className="text-xs">3 this week</Badge>
          </div>
          <div className="space-y-4">
            <div className="flex items-center gap-4">
              <Clock className="h-4 w-4 text-muted-foreground" />
              <div className="flex-1">
                <p className="text-sm font-medium">Property showing</p>
                <p className="text-xs text-muted-foreground">Tomorrow at 2:00 PM</p>
              </div>
              <Avatar className="h-8 w-8">
                <AvatarImage src="/avatars/01.png" />
                <AvatarFallback>JD</AvatarFallback>
              </Avatar>
            </div>
            <div className="flex items-center gap-4">
              <Clock className="h-4 w-4 text-muted-foreground" />
              <div className="flex-1">
                <p className="text-sm font-medium">Maintenance review</p>
                <p className="text-xs text-muted-foreground">Dec 12 at 11:00 AM</p>
              </div>
              <Avatar className="h-8 w-8">
                <AvatarImage src="/avatars/02.png" />
                <AvatarFallback>AS</AvatarFallback>
              </Avatar>
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
}
