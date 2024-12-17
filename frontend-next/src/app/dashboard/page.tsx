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
import { Header } from "@/components/header";

export default function DashboardPage() {
  return (
    <div className="flex-1 space-y-4 p-4 md:p-8 pt-6">
      <Header 
        title="Dashboard"
        description="Welcome back! Here's what's happening with your properties."
        searchPlaceholder="Search dashboard..."
      />
      
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

      {/* Recent Activity */}
      <div className="grid gap-4 grid-cols-1 md:grid-cols-2 lg:grid-cols-7">
        <Card className="col-span-4">
          <div className="flex flex-col space-y-3">
            <div className="px-6 py-4">
              <h3 className="text-lg font-semibold">Recent Activity</h3>
            </div>
            <div className="px-6 py-2 flex items-center justify-between hover:bg-gray-100 dark:hover:bg-gray-800">
              <div className="flex items-center space-x-4">
                <Avatar>
                  <AvatarImage src="/avatars/01.png" />
                  <AvatarFallback>JD</AvatarFallback>
                </Avatar>
                <div>
                  <p className="text-sm font-medium">Rent Payment Received</p>
                  <p className="text-sm text-gray-500">From John Doe</p>
                </div>
              </div>
              <Badge>+$2,500</Badge>
            </div>
            <div className="px-6 py-2 flex items-center justify-between hover:bg-gray-100 dark:hover:bg-gray-800">
              <div className="flex items-center space-x-4">
                <Avatar>
                  <AvatarImage src="/avatars/02.png" />
                  <AvatarFallback>MS</AvatarFallback>
                </Avatar>
                <div>
                  <p className="text-sm font-medium">Maintenance Request</p>
                  <p className="text-sm text-gray-500">By Mary Smith</p>
                </div>
              </div>
              <Badge variant="outline">Pending</Badge>
            </div>
            <div className="px-6 py-2 flex items-center justify-between hover:bg-gray-100 dark:hover:bg-gray-800">
              <div className="flex items-center space-x-4">
                <Avatar>
                  <AvatarImage src="/avatars/03.png" />
                  <AvatarFallback>RJ</AvatarFallback>
                </Avatar>
                <div>
                  <p className="text-sm font-medium">Lease Renewal</p>
                  <p className="text-sm text-gray-500">For Robert Johnson</p>
                </div>
              </div>
              <Badge variant="outline">Due in 5 days</Badge>
            </div>
          </div>
        </Card>

        {/* Quick Actions */}
        <Card className="col-span-3">
          <div className="flex flex-col space-y-3">
            <div className="px-6 py-4">
              <h3 className="text-lg font-semibold">Quick Actions</h3>
            </div>
            <div className="px-6 py-2">
              <Button className="w-full mb-2" variant="outline">
                <Plus className="mr-2 h-4 w-4" /> Add New Property
              </Button>
              <Button className="w-full mb-2" variant="outline">
                <FileText className="mr-2 h-4 w-4" /> Create Report
              </Button>
              <Button className="w-full mb-2" variant="outline">
                <Wrench className="mr-2 h-4 w-4" /> Schedule Maintenance
              </Button>
              <Button className="w-full" variant="outline">
                <AlertTriangle className="mr-2 h-4 w-4" /> Report Issue
              </Button>
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
}