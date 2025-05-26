import { Card, CardContent } from "@/components/ui/card";
import { LucideIcon } from "lucide-react";

interface StatsCardProps {
  title: string;
  value: string | number;
  icon: LucideIcon;
  trend?: string;
  color: "blue" | "green" | "purple" | "cyan" | "red" | "yellow";
}

const colorClasses = {
  blue: "text-blue-400 bg-blue-500/20",
  green: "text-green-400 bg-green-500/20",
  purple: "text-purple-400 bg-purple-500/20",
  cyan: "text-cyan-400 bg-cyan-500/20",
  red: "text-red-400 bg-red-500/20",
  yellow: "text-yellow-400 bg-yellow-500/20",
};

export function StatsCard({ title, value, icon: Icon, trend, color }: StatsCardProps) {
  return (
    <Card className="neo-card">
      <CardContent className="p-6">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-slate-400 text-sm font-medium">{title}</p>
            <p className="text-2xl font-bold text-white mt-1">{value}</p>
            {trend && (
              <p className="text-green-400 text-sm mt-1">{trend}</p>
            )}
          </div>
          <div className={`w-12 h-12 rounded-full flex items-center justify-center ${colorClasses[color]}`}>
            <Icon className="w-6 h-6" />
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
