"use client";

import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { apiService, AnalyticsData } from "@/lib/api";
import { 
  FileText, 
  MessageSquare, 
  Brain, 
  TrendingUp,
  Clock,
  Target,
  Award,
  Zap
} from "lucide-react";
import Link from "next/link";
import { StatsCard } from "@/components/stats-card";
import { RecentActivity } from "@/components/recent-activity";
import { QuickActions } from "@/components/quick-actions";

export default function Dashboard() {
  const [analytics, setAnalytics] = useState<AnalyticsData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchAnalytics = async () => {
      try {
        const response = await apiService.getAnalytics("cli_user");
        setAnalytics(response.data);
      } catch (error) {
        console.error("Failed to fetch analytics:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchAnalytics();
  }, []);

  if (loading) {
    return (
      <div className="space-y-8">
        <div className="text-center">
          <div className="w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto"></div>
          <p className="text-slate-400 mt-4">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Hero Section */}
      <div className="text-center space-y-4">
        <h1 className="text-4xl md:text-6xl font-bold">
          <span className="glow-text">Academic</span>{" "}
          <span className="text-white">Intelligence</span>
        </h1>
        <p className="text-xl text-slate-400 max-w-2xl mx-auto">
          Transform your learning experience with AI-powered document analysis,
          intelligent Q&A, and personalized study insights.
        </p>
        <div className="flex flex-col sm:flex-row gap-4 justify-center mt-8">
          <Link href="/upload">
            <Button size="lg" className="neo-button">
              <FileText className="w-5 h-5 mr-2" />
              Upload Document
            </Button>
          </Link>
          <Link href="/ask">
            <Button size="lg" variant="outline" className="border-blue-500 text-blue-400 hover:bg-blue-500/10">
              <MessageSquare className="w-5 h-5 mr-2" />
              Ask Questions
            </Button>
          </Link>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatsCard
          title="Total Questions"
          value={analytics?.total_questions || 0}
          icon={MessageSquare}
          trend="+12%"
          color="blue"
        />
        <StatsCard
          title="Documents"
          value={analytics?.unique_documents || 0}
          icon={FileText}
          trend="+5%"
          color="green"
        />
        <StatsCard
          title="Learning Sessions"
          value={analytics?.learning_sessions || 0}
          icon={Clock}
          trend="+8%"
          color="purple"
        />
        <StatsCard
          title="Comprehension"
          value={`${Math.round((analytics?.comprehension_score || 0) * 100)}%`}
          icon={Brain}
          trend="+15%"
          color="cyan"
        />
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Quick Actions */}
        <div className="lg:col-span-1">
          <QuickActions />
        </div>

        {/* Recent Activity */}
        <div className="lg:col-span-2">
          <RecentActivity />
        </div>
      </div>

      {/* Learning Progress */}
      <Card className="neo-card">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <TrendingUp className="w-5 h-5 text-blue-400" />
            Learning Progress
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-slate-400">Daily Goal</span>
                <span className="text-white">5 questions</span>
              </div>
              <div className="w-full bg-slate-700 rounded-full h-2">
                <div className="bg-gradient-to-r from-blue-500 to-cyan-400 h-2 rounded-full w-4/5"></div>
              </div>
            </div>
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-slate-400">Weekly Streak</span>
                <span className="text-white">7 days</span>
              </div>
              <div className="w-full bg-slate-700 rounded-full h-2">
                <div className="bg-gradient-to-r from-green-500 to-emerald-400 h-2 rounded-full w-full"></div>
              </div>
            </div>
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-slate-400">Complexity</span>
                <span className="text-white">Intermediate</span>
              </div>
              <div className="w-full bg-slate-700 rounded-full h-2">
                <div className="bg-gradient-to-r from-purple-500 to-pink-400 h-2 rounded-full w-3/5"></div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
