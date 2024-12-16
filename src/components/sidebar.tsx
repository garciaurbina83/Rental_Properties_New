'use client';

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import {
  Building2,
  LayoutDashboard,
  Users,
  ClipboardList,
  Wallet,
  Receipt,
  Wrench,
  BarChart3,
  Settings,
  LogOut,
} from "lucide-react";

const routes = [
  {
    label: "Dashboard",
    icon: LayoutDashboard,
    href: "/dashboard",
    color: "text-sky-500",
  },
  {
    label: "Properties",
    icon: Building2,
    href: "/properties",
    color: "text-violet-500",
  },
  {
    label: "Tenants",
    icon: Users,
    href: "/tenants",
    color: "text-pink-500",
  },
  {
    label: "Contracts",
    icon: ClipboardList,
    href: "/contracts",
    color: "text-orange-500",
  },
  {
    label: "Payments",
    icon: Wallet,
    href: "/payments",
    color: "text-green-500",
  },
  {
    label: "Expenses",
    icon: Receipt,
    href: "/expenses",
    color: "text-red-500",
  },
  {
    label: "Loans",
    icon: Wallet,
    href: "/loans",
    color: "text-blue-500",
  },
  {
    label: "Maintenance",
    icon: Wrench,
    href: "/maintenance",
    color: "text-yellow-500",
  },
  {
    label: "Analytics",
    icon: BarChart3,
    href: "/analytics",
    color: "text-purple-500",
  },
  {
    label: "Settings",
    icon: Settings,
    href: "/settings",
    color: "text-gray-500",
  },
];

const Sidebar = () => {
  const pathname = usePathname();

  return (
    <div className="space-y-4 py-4 flex flex-col h-full bg-[hsl(224,71%,8%)] text-white">
      <div className="px-3 py-2">
        <Link href="/dashboard" className="flex items-center pl-3 mb-14">
          <Building2 className="h-8 w-8 text-primary" />
          <h1 className="text-2xl font-bold ml-2">PropManager</h1>
        </Link>
        <div className="space-y-1">
          {routes.map((route) => (
            <Link
              key={route.href}
              href={route.href}
              className={cn(
                "text-sm group flex p-3 w-full justify-start font-medium cursor-pointer hover:bg-[hsl(224,71%,12%)] rounded-lg transition",
                pathname === route.href ? "bg-[hsl(224,71%,12%)] text-white" : "text-zinc-400"
              )}
            >
              <div className="flex items-center flex-1">
                <route.icon className={cn("h-5 w-5 mr-3", route.color)} />
                {route.label}
              </div>
            </Link>
          ))}
        </div>
      </div>
      <div className="mt-auto px-3 py-2">
        <Button
          variant="ghost"
          className="w-full justify-start gap-3 text-zinc-400 hover:text-white hover:bg-[hsl(224,71%,12%)]"
        >
          <LogOut className="h-5 w-5" />
          Logout
        </Button>
      </div>
    </div>
  );
};

export default Sidebar;
