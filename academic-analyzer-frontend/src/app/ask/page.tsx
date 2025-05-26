"use client";

import { useState, useRef, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { toast } from "sonner"; // Changed import
import { apiService } from "@/lib/api";
import { 
  MessageSquare, 
  Send, 
  FileText, 
  Star,
  Loader2,
  ThumbsUp,
  ThumbsDown,
  Copy,
  ExternalLink
} from "lucide-react";
import { ScrollArea } from "@/components/ui/scroll-area";

interface Message {
  id: string;
  type: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  sources?: Array<{
    document: string;
    chunk_id: string;
    relevance_score: number;
    preview: string;
  }>;
  tutor_explanation?: string;
  interaction_id?: string;
}

export default function AskPage() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [selectedDocument, setSelectedDocument] = useState("all");
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || loading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content: input,
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInput("");
    setLoading(true);

    try {
      const response = await apiService.askQuestion(input, selectedDocument, "cli_user");
      const data = response.data;

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: 'assistant',
        content: data.answer,
        timestamp: new Date(),
        sources: data.sources,
        tutor_explanation: data.tutor_explanation,
        interaction_id: data.interaction_id,
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      toast.error("Failed to get answer. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const handleFeedback = async (interactionId: string, rating: number) => {
    try {
      await apiService.submitFeedback(interactionId, rating);
      toast.success("Thank you for your feedback!");
    } catch (error) {
      toast.error("Failed to submit feedback.");
    }
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    toast.success("Answer copied to clipboard.");
  };

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      <div className="text-center space-y-4">
        <h1 className="text-4xl font-bold glow-text">Ask Questions</h1>
        <p className="text-slate-400 text-lg">
          Get instant answers from your uploaded documents with AI-powered analysis
        </p>
      </div>

      {/* Chat Container */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Chat Area */}
        <div className="lg:col-span-3">
          <Card className="neo-card h-[600px] flex flex-col">
            <CardHeader className="border-b border-slate-700/50">
              <CardTitle className="flex items-center gap-2">
                <MessageSquare className="w-5 h-5 text-blue-400" />
                Q&A Chat
              </CardTitle>
            </CardHeader>
            
            <CardContent className="flex-1 p-0">
              <ScrollArea className="h-full p-6">
                <div className="space-y-6">
                  {messages.length === 0 && (
                    <div className="text-center py-12">
                      <div className="w-16 h-16 mx-auto bg-blue-500/20 rounded-full flex items-center justify-center mb-4">
                        <MessageSquare className="w-8 h-8 text-blue-400" />
                      </div>
                      <h3 className="text-xl font-semibold text-white mb-2">
                        Start a conversation
                      </h3>
                      <p className="text-slate-400">
                        Ask any question about your uploaded documents
                      </p>
                    </div>
                  )}

                  {messages.map((message) => (
                    <div
                      key={message.id}
                      className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
                    >
                      <div
                        className={`max-w-[80%] rounded-lg p-4 ${
                          message.type === 'user'
                            ? 'bg-gradient-to-r from-blue-600 to-purple-600 text-white'
                            : 'glass-card'
                        }`}
                      >
                        <p className="whitespace-pre-wrap">{message.content}</p>
                        
                        {message.type === 'assistant' && (
                          <div className="mt-4 space-y-4">
                            {/* Sources */}
                            {message.sources && message.sources.length > 0 && (
                              <div className="border-t border-slate-600 pt-3">
                                <h4 className="text-sm font-semibold text-slate-300 mb-2">
                                  Sources:
                                </h4>
                                <div className="space-y-2">
                                  {message.sources.slice(0, 3).map((source, idx) => (
                                    <div key={idx} className="text-xs bg-slate-800/50 rounded p-2">
                                      <div className="flex items-center justify-between mb-1">
                                        <span className="font-medium text-blue-400">
                                          {source.document}
                                        </span>
                                        <Badge variant="outline" className="text-xs">
                                          {(source.relevance_score * 100).toFixed(0)}%
                                        </Badge>
                                      </div>
                                      <p className="text-slate-400">{source.preview}</p>
                                    </div>
                                  ))}
                                </div>
                              </div>
                            )}

                            {/* Tutor Explanation */}
                            {message.tutor_explanation && (
                              <div className="border-t border-slate-600 pt-3">
                                <h4 className="text-sm font-semibold text-slate-300 mb-2 flex items-center gap-1">
                                  <Star className="w-4 h-4 text-yellow-400" />
                                  Tutor Insight:
                                </h4>
                                <p className="text-sm text-slate-300">
                                  {message.tutor_explanation}
                                </p>
                              </div>
                            )}

                            {/* Actions */}
                            <div className="flex items-center gap-2 pt-2">
                              <Button
                                size="sm"
                                variant="ghost"
                                onClick={() => copyToClipboard(message.content)}
                              >
                                <Copy className="w-4 h-4" />
                              </Button>
                              {message.interaction_id && (
                                <>
                                  <Button
                                    size="sm"
                                    variant="ghost"
                                    onClick={() => handleFeedback(message.interaction_id!, 5)}
                                  >
                                    <ThumbsUp className="w-4 h-4" />
                                  </Button>
                                  <Button
                                    size="sm"
                                    variant="ghost"
                                    onClick={() => handleFeedback(message.interaction_id!, 2)}
                                  >
                                    <ThumbsDown className="w-4 h-4" />
                                  </Button>
                                </>
                              )}
                            </div>
                          </div>
                        )}
                        
                        <div className="text-xs text-slate-400 mt-2">
                          {message.timestamp.toLocaleTimeString()}
                        </div>
                      </div>
                    </div>
                  ))}

                  {loading && (
                    <div className="flex justify-start">
                      <div className="glass-card rounded-lg p-4">
                        <div className="flex items-center gap-2">
                          <Loader2 className="w-4 h-4 animate-spin" />
                          <span>Thinking...</span>
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
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  placeholder="Ask a question about your documents..."
                  className="flex-1 neo-input"
                  disabled={loading}
                />
                <Button
                  type="submit"
                  disabled={!input.trim() || loading}
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
          {/* Document Filter */}
          <Card className="neo-card">
            <CardHeader>
              <CardTitle className="text-sm">Document Scope</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                <Button
                  variant={selectedDocument === "all" ? "default" : "outline"}
                  size="sm"
                  className="w-full justify-start"
                  onClick={() => setSelectedDocument("all")}
                >
                  <FileText className="w-4 h-4 mr-2" />
                  All Documents
                </Button>
                {/* Add specific documents here */}
              </div>
            </CardContent>
          </Card>

          {/* Quick Questions */}
          <Card className="neo-card">
            <CardHeader>
              <CardTitle className="text-sm">Quick Questions</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              {[
                "What is the main topic of this document?",
                "Can you summarize the key points?",
                "What are the main conclusions?",
                "Explain the methodology used.",
              ].map((question, idx) => (
                <Button
                  key={idx}
                  variant="ghost"
                  size="sm"
                  className="w-full text-left h-auto p-2 text-xs"
                  onClick={() => setInput(question)}
                >
                  {question}
                </Button>
              ))}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
