"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import {
  Brain,
  FileText,
  MessageSquare,
  BarChart3,
  Upload,
  Search,
  Library,
  Settings,
} from "lucide-react";

const navItems = [
  { href: "/", label: "Dashboard", icon: BarChart3 },
  { href: "/upload", label: "Upload", icon: Upload },
  { href: "/ask", label: "Ask Questions", icon: MessageSquare },
  { href: "/library", label: "Library", icon: Library },
  { href: "/tutor", label: "AI Tutor", icon: Brain },
  { href: "/research", label: "Research", icon: Search },
  { href: "/analytics", label: "Analytics", icon: BarChart3 },
];

export function Navigation() {
  const pathname = usePathname();

  return (
    <nav className="border-b border-slate-700/50 bg-slate-900/20 backdrop-blur-lg">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          <Link href="/" className="flex items-center space-x-2">
            <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
              <FileText className="w-5 h-5 text-white" />
            </div>
            <span className="text-xl font-bold glow-text">
              Academic Analyzer
            </span>
          </Link>

          <div className="flex space-x-1">
            {navItems.map((item) => {
              const isActive = pathname === item.href;
              const Icon = item.icon;
              
              return (
                <Link key={item.href} href={item.href}>
                  <Button
                    variant={isActive ? "default" : "ghost"}
                    size="sm"
                    className={cn(
                      "flex items-center space-x-2",
                      isActive
                        ? "bg-gradient-to-r from-blue-600 to-purple-600 text-white shadow-neo"
                        : "text-slate-300 hover:text-white hover:bg-slate-800/50"
                    )}
                  >
                    <Icon className="w-4 h-4" />
                    <span className="hidden md:inline">{item.label}</span>
                  </Button>
                </Link>
              );
            })}
          </div>
        </div>
      </div>
    </nav>
  );
}
