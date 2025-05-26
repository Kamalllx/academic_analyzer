"use client";

import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { apiService } from "@/lib/api";
import { toast } from "sonner";import { 
  Search, 
  BookOpen, 
  ExternalLink,
  Lightbulb,
  Bookmark,
  Star,
  TrendingUp,
  FileText,
  Globe
} from "lucide-react";

export default function ResearchPage() {
  const [topic, setTopic] = useState("");
  const [suggestions, setSuggestions] = useState("");
  const [loading, setLoading] = useState(false);
  const [searchHistory, setSearchHistory] = useState<string[]>([]);

  const trendingTopics = [
    "Machine Learning", "Artificial Intelligence", "Climate Change", 
    "Quantum Computing", "Blockchain", "Neuroscience", "Space Exploration"
  ];

  const researchAreas = [
    { name: "Computer Science", icon: "💻", papers: "2.3M" },
    { name: "Medicine", icon: "🏥", papers: "1.8M" },
    { name: "Physics", icon: "⚛️", papers: "1.5M" },
    { name: "Biology", icon: "🧬", papers: "1.2M" },
    { name: "Psychology", icon: "🧠", papers: "980K" },
    { name: "Economics", icon: "📊", papers: "750K" },
  ];

  const handleSearch = async () => {
    if (!topic.trim()) return;
    
    setLoading(true);
    try {
      const res = await apiService.getResearchSuggestions(topic);
      setSuggestions(res.data.suggestions);
      
      // Add to search history
      if (!searchHistory.includes(topic)) {
        setSearchHistory(prev => [topic, ...prev.slice(0, 9)]);
      }
      
      toast.success("Operation completed successfully.");
    } catch (error) {
        toast.error("Something went wrong.");
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    handleSearch();
  };

  return (
    <div className="max-w-6xl mx-auto space-y-8">
      <div className="text-center space-y-4">
        <h1 className="text-4xl font-bold glow-text flex items-center justify-center gap-2">
          <BookOpen className="w-8 h-8 text-purple-400" />
          Research Assistant
        </h1>
        <p className="text-slate-400 text-lg">
          Discover relevant research, papers, and academic resources for any topic
        </p>
      </div>

      {/* Search Section */}
      <Card className="neo-card">
        <CardContent className="p-6">
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="flex gap-3">
              <Input
                placeholder="Enter research topic or question..."
                value={topic}
                onChange={(e) => setTopic(e.target.value)}
                disabled={loading}
                className="flex-1 neo-input text-lg"
              />
              <Button
                type="submit"
                disabled={loading || !topic.trim()}
                className="neo-button px-8"
              >
                {loading ? (
                  "Searching..."
                ) : (
                  <>
                    <Search className="w-4 h-4 mr-2" />
                    Search
                  </>
                )}
              </Button>
            </div>
            
            {/* Trending Topics */}
            <div className="flex flex-wrap gap-2">
              <span className="text-sm text-slate-400 mr-2">Trending:</span>
              {trendingTopics.slice(0, 5).map((trending, idx) => (
                <Badge
                  key={idx}
                  variant="outline"
                  className="cursor-pointer hover:bg-blue-500/20 hover:border-blue-500"
                  onClick={() => setTopic(trending)}
                >
                  {trending}
                </Badge>
              ))}
            </div>
          </form>
        </CardContent>
      </Card>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
        {/* Main Content */}
        <div className="lg:col-span-3">
          {suggestions ? (
            <Tabs defaultValue="suggestions" className="space-y-6">
              <TabsList className="grid w-full grid-cols-3 bg-slate-800/50">
                <TabsTrigger value="suggestions">Research Suggestions</TabsTrigger>
                <TabsTrigger value="papers">Related Papers</TabsTrigger>
                <TabsTrigger value="resources">Resources</TabsTrigger>
              </TabsList>

              <TabsContent value="suggestions" className="space-y-6">
                <Card className="neo-card">
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Lightbulb className="w-5 h-5 text-yellow-400" />
                      Research Suggestions for "{topic}"
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="prose prose-invert max-w-none">
                      <div className="text-slate-200 whitespace-pre-wrap leading-relaxed">
                        {suggestions}
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </TabsContent>

              <TabsContent value="papers" className="space-y-6">
                <Card className="neo-card">
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <FileText className="w-5 h-5 text-blue-400" />
                      Related Academic Papers
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    {/* Simulated paper results */}
                    {[1, 2, 3].map((_, idx) => (
                      <div key={idx} className="p-4 bg-slate-800/50 rounded-lg border border-slate-700/50">
                        <h4 className="font-semibold text-white mb-2">
                          A Comprehensive Analysis of {topic} in Modern Applications
                        </h4>
                        <p className="text-slate-400 text-sm mb-3">
                          Smith, J., Johnson, M., & Williams, R. (2024)
                        </p>
                        <p className="text-slate-300 text-sm mb-3">
                          This study examines various aspects of {topic} with focus on practical applications and theoretical foundations...
                        </p>
                        <div className="flex items-center justify-between">
                          <div className="flex gap-2">
                            <Badge variant="outline">Impact Factor: 4.2</Badge>
                            <Badge variant="outline">Citations: 156</Badge>
                          </div>
                          <Button size="sm" variant="outline">
                            <ExternalLink className="w-4 h-4 mr-1" />
                            View Paper
                          </Button>
                        </div>
                      </div>
                    ))}
                  </CardContent>
                </Card>
              </TabsContent>

              <TabsContent value="resources" className="space-y-6">
                <Card className="neo-card">
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Globe className="w-5 h-5 text-green-400" />
                      Learning Resources
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    {/* Simulated resource results */}
                    {[
                      { type: "Course", platform: "Coursera", title: `Introduction to ${topic}` },
                      { type: "Tutorial", platform: "Khan Academy", title: `${topic} Fundamentals` },
                      { type: "Book", platform: "Academic Press", title: `Advanced ${topic} Theory` },
                      { type: "Video", platform: "YouTube", title: `${topic} Explained` },
                    ].map((resource, idx) => (
                      <div key={idx} className="p-4 bg-slate-800/50 rounded-lg border border-slate-700/50">
                        <div className="flex items-center justify-between">
                          <div>
                            <h4 className="font-semibold text-white">{resource.title}</h4>
                            <p className="text-slate-400 text-sm">{resource.platform}</p>
                          </div>
                          <div className="flex items-center gap-2">
                            <Badge variant="outline">{resource.type}</Badge>
                            <Button size="sm" variant="outline">
                              <ExternalLink className="w-4 h-4" />
                            </Button>
                          </div>
                        </div>
                      </div>
                    ))}
                  </CardContent>
                </Card>
              </TabsContent>
            </Tabs>
          ) : (
            /* Welcome State */
            <Card className="neo-card">
              <CardContent className="p-12 text-center">
                <div className="w-24 h-24 mx-auto bg-gradient-to-br from-purple-500/20 to-pink-500/20 rounded-full flex items-center justify-center mb-6 animate-float">
                  <Search className="w-12 h-12 text-purple-400" />
                </div>
                <h3 className="text-2xl font-semibold text-white mb-4">
                  Start Your Research Journey
                </h3>
                <p className="text-slate-400 mb-8 max-w-md mx-auto">
                  Enter a topic above to get personalized research suggestions, academic papers, and learning resources.
                </p>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 max-w-2xl mx-auto">
                  <div className="p-4 bg-slate-800/50 rounded-lg">
                    <BookOpen className="w-8 h-8 text-blue-400 mx-auto mb-2" />
                    <h4 className="font-semibold text-white mb-1">Academic Papers</h4>
                    <p className="text-slate-400 text-sm">Find relevant research papers and publications</p>
                  </div>
                  <div className="p-4 bg-slate-800/50 rounded-lg">
                    <Lightbulb className="w-8 h-8 text-yellow-400 mx-auto mb-2" />
                    <h4 className="font-semibold text-white mb-1">Research Ideas</h4>
                    <p className="text-slate-400 text-sm">Get suggestions for research directions</p>
                  </div>
                  <div className="p-4 bg-slate-800/50 rounded-lg">
                    <Globe className="w-8 h-8 text-green-400 mx-auto mb-2" />
                    <h4 className="font-semibold text-white mb-1">Learning Resources</h4>
                    <p className="text-slate-400 text-sm">Discover courses, tutorials, and books</p>
                  </div>
                  <div className="p-4 bg-slate-800/50 rounded-lg">
                    <TrendingUp className="w-8 h-8 text-purple-400 mx-auto mb-2" />
                    <h4 className="font-semibold text-white mb-1">Trend Analysis</h4>
                    <p className="text-slate-400 text-sm">Understand current research trends</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Research Areas */}
          <Card className="neo-card">
            <CardHeader>
              <CardTitle className="text-sm">Research Areas</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              {researchAreas.map((area, idx) => (
                <div
                  key={idx}
                  className="flex items-center justify-between p-2 hover:bg-slate-800/50 rounded cursor-pointer"
                  onClick={() => setTopic(area.name)}
                >
                  <div className="flex items-center gap-2">
                    <span className="text-lg">{area.icon}</span>
                    <span className="text-sm text-slate-300">{area.name}</span>
                  </div>
                  <span className="text-xs text-slate-500">{area.papers}</span>
                </div>
              ))}
            </CardContent>
          </Card>

          {/* Search History */}
          {searchHistory.length > 0 && (
            <Card className="neo-card">
              <CardHeader>
                <CardTitle className="text-sm flex items-center gap-2">
                  <Bookmark className="w-4 h-4 text-blue-400" />
                  Recent Searches
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-2">
                {searchHistory.slice(0, 5).map((search, idx) => (
                  <Button
                    key={idx}
                    variant="ghost"
                    size="sm"
                    className="w-full justify-start text-left h-auto p-2"
                    onClick={() => setTopic(search)}
                  >
                    <span className="text-xs truncate">{search}</span>
                  </Button>
                ))}
              </CardContent>
            </Card>
          )}

          {/* Quick Tips */}
          <Card className="neo-card">
            <CardHeader>
              <CardTitle className="text-sm flex items-center gap-2">
                <Star className="w-4 h-4 text-yellow-400" />
                Research Tips
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="text-xs text-slate-400 space-y-2">
                <p>• Use specific keywords for better results</p>
                <p>• Check publication dates for current research</p>
                <p>• Cross-reference multiple sources</p>
                <p>• Look for peer-reviewed articles</p>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
