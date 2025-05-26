"use client";

import { useState, useRef, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { apiService } from "@/lib/api";
import { toast } from "sonner";import { 
  Loader2, 
  MessageSquare, 
  Brain, 
  Send,
  BookOpen,
  Lightbulb,
  Target,
  Clock
} from "lucide-react";
import { ScrollArea } from "@/components/ui/scroll-area";

interface TutorMessage {
  id: string;
  type: 'user' | 'tutor';
  content: string;
  timestamp: Date;
  category?: string;
}

export default function TutorPage() {
  const [messages, setMessages] = useState<TutorMessage[]>([]);
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const quickPrompts = [
    { text: "Help me understand this concept better", category: "Understanding", icon: Lightbulb },
    { text: "Create a study plan for this topic", category: "Planning", icon: Target },
    { text: "Explain this in simpler terms", category: "Simplification", icon: BookOpen },
    { text: "Give me practice questions", category: "Practice", icon: MessageSquare },
  ];

  const handleSend = async (inputMessage?: string) => {
    const messageToSend = inputMessage || message;
    if (!messageToSend.trim() || loading) return;

    const userMessage: TutorMessage = {
      id: Date.now().toString(),
      type: 'user',
      content: messageToSend,
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setMessage("");
    setLoading(true);

    try {
      const res = await apiService.chatTutor(messageToSend);
      const tutorMessage: TutorMessage = {
        id: (Date.now() + 1).toString(),
        type: 'tutor',
        content: res.data.response,
        timestamp: new Date(),
        category: "Response"
      };
      
      setMessages(prev => [...prev, tutorMessage]);
    } catch (error) {
        toast.error("Something went wrong.");
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    handleSend();
  };

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      <div className="text-center space-y-4">
        <h1 className="text-4xl font-bold glow-text flex items-center justify-center gap-2">
          <Brain className="w-8 h-8 text-blue-400" />
          AI Tutor
        </h1>
        <p className="text-slate-400 text-lg">
          Get personalized learning assistance and study guidance
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Chat Area */}
        <div className="lg:col-span-3">
          <Card className="neo-card h-[600px] flex flex-col">
            <CardHeader className="border-b border-slate-700/50">
              <CardTitle className="flex items-center gap-2">
                <MessageSquare className="w-5 h-5 text-blue-400" />
                Chat with AI Tutor
              </CardTitle>
            </CardHeader>
            
            <CardContent className="flex-1 p-0">
              <ScrollArea className="h-full p-6">
                <div className="space-y-6">
                  {messages.length === 0 && (
                    <div className="text-center py-12">
                      <div className="w-16 h-16 mx-auto bg-gradient-to-br from-blue-500/20 to-purple-500/20 rounded-full flex items-center justify-center mb-4 animate-float">
                        <Brain className="w-8 h-8 text-blue-400" />
                      </div>
                      <h3 className="text-xl font-semibold text-white mb-2">
                        Hello! I'm your AI Tutor
                      </h3>
                      <p className="text-slate-400 mb-6">
                        I'm here to help you learn, understand concepts, and improve your study skills.
                        Ask me anything about your academic journey!
                      </p>
                      
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-3 max-w-md mx-auto">
                        {quickPrompts.map((prompt, idx) => (
                          <Button
                            key={idx}
                            variant="outline"
                            size="sm"
                            className="h-auto p-3 text-left border-slate-600 hover:border-blue-500"
                            onClick={() => handleSend(prompt.text)}
                          >
                            <div className="flex items-center gap-2">
                              <prompt.icon className="w-4 h-4 text-blue-400" />
                              <span className="text-xs">{prompt.text}</span>
                            </div>
                          </Button>
                        ))}
                      </div>
                    </div>
                  )}

                  {messages.map((msg) => (
                    <div
                      key={msg.id}
                      className={`flex ${msg.type === 'user' ? 'justify-end' : 'justify-start'}`}
                    >
                      <div
                        className={`max-w-[80%] rounded-lg p-4 ${
                          msg.type === 'user'
                            ? 'bg-gradient-to-r from-blue-600 to-purple-600 text-white'
                            : 'glass-card'
                        }`}
                      >
                        {msg.type === 'tutor' && (
                          <div className="flex items-center gap-2 mb-2">
                            <Brain className="w-4 h-4 text-blue-400" />
                            <span className="text-sm font-medium text-blue-400">AI Tutor</span>
                            {msg.category && (
                              <Badge variant="outline" className="text-xs">
                                {msg.category}
                              </Badge>
                            )}
                          </div>
                        )}
                        
                        <p className="whitespace-pre-wrap text-sm leading-relaxed">
                          {msg.content}
                        </p>
                        
                        <div className="text-xs text-slate-400 mt-2">
                          {msg.timestamp.toLocaleTimeString()}
                        </div>
                      </div>
                    </div>
                  ))}

                  {loading && (
                    <div className="flex justify-start">
                      <div className="glass-card rounded-lg p-4">
                        <div className="flex items-center gap-2">
                          <Loader2 className="w-4 h-4 animate-spin text-blue-400" />
                          <span className="text-slate-300">Thinking...</span>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
                <div ref={messagesEndRef} />
              </ScrollArea>
            </CardContent>

            {/* Input Form */}
            <div className="border-t border-slate-700/50 p-4">
              <form onSubmit={handleSubmit} className="flex gap-2">
                <Input
                  value={message}
                  onChange={(e) => setMessage(e.target.value)}
                  placeholder="Ask the AI tutor anything about your studies..."
                  className="flex-1 neo-input"
                  disabled={loading}
                />
                <Button
                  type="submit"
                  disabled={!message.trim() || loading}
                  className="neo-button"
                >
                  <Send className="w-4 h-4" />
                </Button>
              </form>
            </div>
          </Card>
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Quick Actions */}
          <Card className="neo-card">
            <CardHeader>
              <CardTitle className="text-sm">Quick Actions</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              {quickPrompts.map((prompt, idx) => (
                <Button
                  key={idx}
                  variant="ghost"
                  size="sm"
                  className="w-full justify-start h-auto p-2"
                  onClick={() => handleSend(prompt.text)}
                >
                  <prompt.icon className="w-4 h-4 mr-2 text-blue-400" />
                  <span className="text-xs text-left">{prompt.text}</span>
                </Button>
              ))}
            </CardContent>
          </Card>

          {/* Study Tips */}
          <Card className="neo-card">
            <CardHeader>
              <CardTitle className="text-sm flex items-center gap-2">
                <Lightbulb className="w-4 h-4 text-yellow-400" />
                Study Tips
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="space-y-2">
                <h4 className="text-xs font-semibold text-slate-300">Today's Tip</h4>
                <p className="text-xs text-slate-400">
                  Break complex topics into smaller, manageable chunks for better understanding.
                </p>
              </div>
              
              <div className="space-y-2">
                <h4 className="text-xs font-semibold text-slate-300">Recommended</h4>
                <ul className="text-xs text-slate-400 space-y-1">
                  <li>• Review concepts before bed</li>
                  <li>• Use active recall techniques</li>
                  <li>• Take regular study breaks</li>
                </ul>
              </div>
            </CardContent>
          </Card>

          {/* Session Stats */}
          <Card className="neo-card">
            <CardHeader>
              <CardTitle className="text-sm flex items-center gap-2">
                <Clock className="w-4 h-4 text-green-400" />
                This Session
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="flex justify-between text-xs">
                <span className="text-slate-400">Messages:</span>
                <span className="text-white">{messages.length}</span>
              </div>
              <div className="flex justify-between text-xs">
                <span className="text-slate-400">Duration:</span>
                <span className="text-white">
                  {messages.length > 0 ? 
                    Math.round((Date.now() - messages[0]?.timestamp.getTime()) / 60000) : 0} min
                </span>
              </div>
              <div className="flex justify-between text-xs">
                <span className="text-slate-400">Topic Focus:</span>
                <span className="text-white">General</span>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
