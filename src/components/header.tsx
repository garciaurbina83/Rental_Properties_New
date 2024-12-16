'use client';

import { Button } from "@/components/ui/button";
import { Command, CommandInput } from "@/components/ui/command";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Sun, Bell, Mail, Gift } from "lucide-react";
import { cn } from "@/lib/utils";

interface HeaderProps {
  title: string;
  description?: string;
  showSearch?: boolean;
  searchPlaceholder?: string;
  children?: React.ReactNode;
}

export function Header({
  title,
  description,
  showSearch = true,
  searchPlaceholder = "Search...",
  children,
}: HeaderProps) {
  return (
    <div className="flex flex-col gap-6 mb-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold mb-2">{title}</h1>
          {description && (
            <p className="text-muted-foreground">{description}</p>
          )}
        </div>
        <div className="flex items-center gap-6">
          {showSearch && (
            <div className="w-[300px]">
              <Command className="rounded-lg border shadow-md">
                <CommandInput placeholder={searchPlaceholder} />
              </Command>
            </div>
          )}
          <div className="flex items-center gap-4">
            <Button 
              variant="ghost" 
              size="icon" 
              className={cn(
                "rounded-lg text-gray-400 hover:text-white hover:bg-muted transition-colors",
                "h-9 w-9"
              )}
            >
              <Sun className="h-5 w-5" />
            </Button>
            <Button 
              variant="ghost" 
              size="icon" 
              className={cn(
                "rounded-lg text-gray-400 hover:text-white hover:bg-muted transition-colors relative",
                "h-9 w-9"
              )}
            >
              <Bell className="h-5 w-5" />
              <span className="absolute top-1.5 right-1.5 h-2 w-2 rounded-full bg-primary"></span>
            </Button>
            <Button 
              variant="ghost" 
              size="icon" 
              className={cn(
                "rounded-lg text-gray-400 hover:text-white hover:bg-muted transition-colors relative",
                "h-9 w-9"
              )}
            >
              <Mail className="h-5 w-5" />
              <span className="absolute top-1.5 right-1.5 h-2 w-2 rounded-full bg-destructive"></span>
            </Button>
            <Button 
              variant="ghost" 
              size="icon" 
              className={cn(
                "rounded-lg text-gray-400 hover:text-white hover:bg-muted transition-colors relative",
                "h-9 w-9"
              )}
            >
              <Gift className="h-5 w-5" />
              <span className="absolute top-1.5 right-1.5 h-2 w-2 rounded-full bg-blue-500"></span>
            </Button>
            <div className="flex items-center gap-2 ml-2 text-gray-400 hover:text-white transition-colors cursor-pointer">
              <Avatar>
                <AvatarImage src="/avatar.png" />
                <AvatarFallback>JD</AvatarFallback>
              </Avatar>
              <div className="flex flex-col">
                <span className="text-sm font-medium">John Doe</span>
                <span className="text-xs text-muted-foreground">Admin</span>
              </div>
            </div>
          </div>
        </div>
      </div>
      {children}
    </div>
  );
}
