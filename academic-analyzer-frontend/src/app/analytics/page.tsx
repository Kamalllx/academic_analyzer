"use client";

import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Progress } from "@/components/ui/progress";
import { apiService } from "@/lib/api";
import { toast } from "sonner";import { 
  BarChart3, 
  Clock, 
  TrendingUp, 
  Brain,
  Target,
  Calendar,
  BookOpen,
  Award,
  Activity
} from "lucide-react";

export default function AnalyticsPage() {
  const [analytics, setAnalytics] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [timeRange, setTimeRange] = useState("30days");


  useEffect(() => {
    const fetchAnalytics = async () => {
      try {
        const response = await apiService.getAnalytics("cli_user", timeRange);
        setAnalytics(response.data);
      } catch (error) {
        toast.error("Something went wrong.");
      } finally {
        setLoading(false);
      }
    };

    fetchAnalytics();
  }, [timeRange, toast]);

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
      </div>
    );
  }

  if (!analytics) {
    return (
      <div className="text-center space-y-4">
        <Brain className="w-16 h-16 mx-auto text-slate-600" />
        <p className="text-slate-400">No analytics data available.</p>
      </div>
    );
  }

  return (
    <div className="space-y-8 max-w-7xl mx-auto">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-4xl font-bold glow-text">Learning Analytics</h1>
          <p className="text-slate-400 mt-2">Track your learning progress and insights</p>
        </div>
        
        <div className="flex gap-2">
          {["7days", "30days", "90days"].map((range) => (
            <Button
              key={range}
              variant={timeRange === range ? "default" : "outline"}
              size="sm"
              onClick={() => setTimeRange(range)}
              className={timeRange === range ? "neo-button" : ""}
            >
              {range === "7days" ? "7 Days" : range === "30days" ? "30 Days" : "90 Days"}
            </Button>
          ))}
        </div>
      </div>

      {/* Key Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card className="neo-card">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-slate-400 text-sm">Total Questions</p>
                <p className="text-3xl font-bold text-white">{analytics.total_questions}</p>
                <p className="text-green-400 text-sm">+12% from last period</p>
              </div>
              <div className="w-12 h-12 bg-blue-500/20 rounded-full flex items-center justify-center">
                <BarChart3 className="w-6 h-6 text-blue-400" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="neo-card">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-slate-400 text-sm">Documents Accessed</p>
                <p className="text-3xl font-bold text-white">{analytics.unique_documents}</p>
                <p className="text-green-400 text-sm">+5% from last period</p>
              </div>
              <div className="w-12 h-12 bg-green-500/20 rounded-full flex items-center justify-center">
                <BookOpen className="w-6 h-6 text-green-400" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="neo-card">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-slate-400 text-sm">Learning Sessions</p>
                <p className="text-3xl font-bold text-white">{analytics.learning_sessions}</p>
                <p className="text-green-400 text-sm">+8% from last period</p>
              </div>
              <div className="w-12 h-12 bg-purple-500/20 rounded-full flex items-center justify-center">
                <Clock className="w-6 h-6 text-purple-400" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="neo-card">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-slate-400 text-sm">Comprehension</p>
                <p className="text-3xl font-bold text-white">
                  {Math.round((analytics.comprehension_score || 0) * 100)}%
                </p>
                <p className="text-green-400 text-sm">+15% from last period</p>
              </div>
              <div className="w-12 h-12 bg-cyan-500/20 rounded-full flex items-center justify-center">
                <Brain className="w-6 h-6 text-cyan-400" />
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Analytics Tabs */}
      <Tabs defaultValue="overview" className="space-y-6">
        <TabsList className="grid w-full grid-cols-4 bg-slate-800/50">
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="progress">Progress</TabsTrigger>
          <TabsTrigger value="topics">Topics</TabsTrigger>
          <TabsTrigger value="insights">Insights</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card className="neo-card">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Activity className="w-5 h-5 text-blue-400" />
                  Daily Activity
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex justify-between text-sm">
                    <span className="text-slate-400">Average per day</span>
                    <span className="text-white">{analytics.avg_questions_per_day?.toFixed(1)} questions</span>
                  </div>
                  <Progress value={Math.min((analytics.avg_questions_per_day / 10) * 100, 100)} className="h-2" />
                  
                  <div className="grid grid-cols-2 gap-4 pt-4">
                    <div className="text-center">
                      <p className="text-2xl font-bold text-blue-400">{analytics.total_questions}</p>
                      <p className="text-slate-400 text-sm">Total Questions</p>
                    </div>
                    <div className="text-center">
                      <p className="text-2xl font-bold text-green-400">{analytics.learning_sessions}</p>
                      <p className="text-slate-400 text-sm">Study Sessions</p>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card className="neo-card">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Target className="w-5 h-5 text-green-400" />
                  Learning Goals
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div>
                    <div className="flex justify-between text-sm mb-2">
                      <span className="text-slate-400">Daily Goal (5 questions)</span>
                      <span className="text-white">80%</span>
                    </div>
                    <Progress value={80} className="h-2" />
                  </div>
                  
                  <div>
                    <div className="flex justify-between text-sm mb-2">
                      <span className="text-slate-400">Weekly Goal (30 questions)</span>
                      <span className="text-white">65%</span>
                    </div>
                    <Progress value={65} className="h-2" />
                  </div>
                  
                  <div>
                    <div className="flex justify-between text-sm mb-2">
                      <span className="text-slate-400">Complexity Growth</span>
                      <span className="text-white">
                        {analytics.complexity_trend === 'increasing' ? '📈' : 
                         analytics.complexity_trend === 'stable' ? '📊' : '📉'} 
                        {analytics.complexity_trend}
                      </span>
                    </div>
                    <Progress value={analytics.avg_question_complexity * 100} className="h-2" />
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="progress" className="space-y-6">
          <Card className="neo-card">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <TrendingUp className="w-5 h-5 text-purple-400" />
                Learning Progress Timeline
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="text-center p-4 bg-slate-800/50 rounded-lg">
                    <Award className="w-8 h-8 mx-auto text-yellow-400 mb-2" />
                    <p className="text-lg font-semibold">Beginner</p>
                    <p className="text-slate-400 text-sm">0-50 questions</p>
                  </div>
                  <div className="text-center p-4 bg-gradient-to-r from-blue-600/20 to-purple-600/20 rounded-lg border border-blue-500/30">
                    <Award className="w-8 h-8 mx-auto text-blue-400 mb-2" />
                    <p className="text-lg font-semibold">Intermediate</p>
                    <p className="text-slate-400 text-sm">51-200 questions</p>
                  </div>
                  <div className="text-center p-4 bg-slate-800/50 rounded-lg">
                    <Award className="w-8 h-8 mx-auto text-purple-400 mb-2" />
                    <p className="text-lg font-semibold">Advanced</p>
                    <p className="text-slate-400 text-sm">200+ questions</p>
                  </div>
                </div>
                
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span className="text-slate-400">Progress to Advanced</span>
                    <span className="text-white">{analytics.total_questions}/200</span>
                  </div>
                  <Progress value={(analytics.total_questions / 200) * 100} className="h-3" />
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="topics" className="space-y-6">
          <Card className="neo-card">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <BookOpen className="w-5 h-5 text-green-400" />
                Topics Studied
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {analytics.main_topics?.map((topic: string, idx: number) => (
                  <div key={idx} className="flex items-center justify-between p-3 bg-slate-800/50 rounded-lg">
                    <span className="text-slate-300">{topic}</span>
                    <div className="w-16 h-2 bg-slate-700 rounded-full overflow-hidden">
                      <div 
                        className="h-full bg-gradient-to-r from-blue-500 to-purple-500 rounded-full"
                        style={{ width: `${Math.random() * 100}%` }}
                      />
                    </div>
                  </div>
                )) || []}
              </div>
              
              {(!analytics.main_topics || analytics.main_topics.length === 0) && (
                <div className="text-center py-8">
                  <BookOpen className="w-12 h-12 mx-auto text-slate-600 mb-4" />
                  <p className="text-slate-400">No topics studied yet. Start asking questions!</p>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="insights" className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <Card className="neo-card">
              <CardHeader>
                <CardTitle>Performance Insights</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-start gap-3">
                  <div className="w-2 h-2 bg-green-400 rounded-full mt-2"></div>
                  <div>
                    <p className="text-slate-300">
                      Your question complexity has {analytics.complexity_trend === 'increasing' ? 'increased' : 'remained stable'} over time
                    </p>
                  </div>
                </div>
                <div className="flex items-start gap-3">
                  <div className="w-2 h-2 bg-blue-400 rounded-full mt-2"></div>
                  <div>
                    <p className="text-slate-300">
                      Most active learning happens during your current session times
                    </p>
                  </div>
                </div>
                <div className="flex items-start gap-3">
                  <div className="w-2 h-2 bg-purple-400 rounded-full mt-2"></div>
                  <div>
                    <p className="text-slate-300">
                      Comprehension score of {Math.round((analytics.comprehension_score || 0) * 100)}% shows good understanding
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card className="neo-card">
              <CardHeader>
                <CardTitle>Recommendations</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-start gap-3">
                  <div className="w-2 h-2 bg-yellow-400 rounded-full mt-2"></div>
                  <div>
                    <p className="text-slate-300">
                      Try exploring more complex topics to challenge yourself
                    </p>
                  </div>
                </div>
                <div className="flex items-start gap-3">
                  <div className="w-2 h-2 bg-cyan-400 rounded-full mt-2"></div>
                  <div>
                    <p className="text-slate-300">
                      Maintain your current study consistency for better retention
                    </p>
                  </div>
                </div>
                <div className="flex items-start gap-3">
                  <div className="w-2 h-2 bg-pink-400 rounded-full mt-2"></div>
                  <div>
                    <p className="text-slate-300">
                      Consider using the AI tutor for deeper explanations
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
}
