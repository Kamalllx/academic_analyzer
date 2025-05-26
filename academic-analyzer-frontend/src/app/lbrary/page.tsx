"use client";

import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { 
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { apiService } from "@/lib/api";
import { toast } from "sonner";import { 
  FileText, 
  Archive, 
  Search,
  Filter,
  MoreVertical,
  Eye,
  Download,
  Trash2,
  Calendar,
  BarChart3,
  Upload
} from "lucide-react";
import Link from "next/link";

interface Document {
  document_id: string;
  filename: string;
  subject: string;
  upload_date: string;
  complexity_score: number;
  chunk_count: number;
  file_size_mb?: number;
  status?: string;
}

export default function LibraryPage() {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");
  const [sortBy, setSortBy] = useState("upload_date");
  const [filterBy, setFilterBy] = useState("all");

  useEffect(() => {
    const fetchDocuments = async () => {
      try {
        // For demo purposes, we'll create sample documents
        // In a real app, you'd fetch from your backend
        const sampleDocs: Document[] = [
          {
            document_id: "doc_001",
            filename: "Machine Learning Fundamentals.pdf",
            subject: "Machine Learning",
            upload_date: "2024-01-15T10:30:00Z",
            complexity_score: 0.75,
            chunk_count: 45,
            file_size_mb: 12.5,
            status: "active"
          },
          {
            document_id: "doc_002",
            filename: "Introduction to Neural Networks.pdf",
            subject: "Deep Learning",
            upload_date: "2024-01-10T14:20:00Z",
            complexity_score: 0.85,
            chunk_count: 38,
            file_size_mb: 8.7,
            status: "active"
          },
          {
            document_id: "doc_003",
            filename: "Data Science Methods.pdf",
            subject: "Data Science",
            upload_date: "2024-01-05T09:15:00Z",
            complexity_score: 0.65,
            chunk_count: 52,
            file_size_mb: 15.2,
            status: "active"
          }
        ];
        
        setDocuments(sampleDocs);
      } catch (error) {
        toast.error("Something went wrong.");
      } finally {
        setLoading(false);
      }
    };

    fetchDocuments();
  }, [toast]);

  const filteredDocuments = documents.filter(doc => {
    const matchesSearch = doc.filename.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         doc.subject.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesFilter = filterBy === "all" || doc.subject === filterBy;
    return matchesSearch && matchesFilter;
  });

  const sortedDocuments = [...filteredDocuments].sort((a, b) => {
    switch (sortBy) {
      case "upload_date":
        return new Date(b.upload_date).getTime() - new Date(a.upload_date).getTime();
      case "filename":
        return a.filename.localeCompare(b.filename);
      case "complexity":
        return b.complexity_score - a.complexity_score;
      default:
        return 0;
    }
  });

  const getComplexityLevel = (score: number) => {
    if (score < 0.4) return { label: "Basic", color: "bg-green-500" };
    if (score < 0.7) return { label: "Intermediate", color: "bg-yellow-500" };
    return { label: "Advanced", color: "bg-red-500" };
  };

  const subjects = [...new Set(documents.map(doc => doc.subject))];

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto space-y-8">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-4xl font-bold glow-text flex items-center gap-2">
            <Archive className="w-8 h-8 text-green-400" />
            Document Library
          </h1>
          <p className="text-slate-400 mt-2">Manage and explore your uploaded documents</p>
        </div>
        
        <Link href="/upload">
          <Button className="neo-button">
            <Upload className="w-4 h-4 mr-2" />
            Upload Document
          </Button>
        </Link>
      </div>

      {/* Stats Overview */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card className="neo-card">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-slate-400 text-sm">Total Documents</p>
                <p className="text-3xl font-bold text-white">{documents.length}</p>
              </div>
              <FileText className="w-8 h-8 text-blue-400" />
            </div>
          </CardContent>
        </Card>

        <Card className="neo-card">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-slate-400 text-sm">Total Subjects</p>
                <p className="text-3xl font-bold text-white">{subjects.length}</p>
              </div>
              <Archive className="w-8 h-8 text-green-400" />
            </div>
          </CardContent>
        </Card>

        <Card className="neo-card">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-slate-400 text-sm">Avg Complexity</p>
                <p className="text-3xl font-bold text-white">
                  {Math.round((documents.reduce((acc, doc) => acc + doc.complexity_score, 0) / documents.length) * 100)}%
                </p>
              </div>
              <BarChart3 className="w-8 h-8 text-purple-400" />
            </div>
          </CardContent>
        </Card>

        <Card className="neo-card">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-slate-400 text-sm">Total Size</p>
                <p className="text-3xl font-bold text-white">
                  {documents.reduce((acc, doc) => acc + (doc.file_size_mb || 0), 0).toFixed(1)}MB
                </p>
              </div>
              <Calendar className="w-8 h-8 text-cyan-400" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Search and Filter */}
      <Card className="neo-card">
        <CardContent className="p-6">
          <div className="flex flex-col sm:flex-row gap-4">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-slate-400" />
              <Input
                placeholder="Search documents..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10 neo-input"
              />
            </div>
            
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="outline" className="min-w-[120px]">
                  <Filter className="w-4 h-4 mr-2" />
                  {filterBy === "all" ? "All Subjects" : filterBy}
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent>
                <DropdownMenuItem onClick={() => setFilterBy("all")}>
                  All Subjects
                </DropdownMenuItem>
                {subjects.map(subject => (
                  <DropdownMenuItem key={subject} onClick={() => setFilterBy(subject)}>
                    {subject}
                  </DropdownMenuItem>
                ))}
              </DropdownMenuContent>
            </DropdownMenu>

            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="outline" className="min-w-[120px]">
                  Sort by: {sortBy.replace("_", " ")}
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent>
                <DropdownMenuItem onClick={() => setSortBy("upload_date")}>
                  Upload Date
                </DropdownMenuItem>
                <DropdownMenuItem onClick={() => setSortBy("filename")}>
                  Filename
                </DropdownMenuItem>
                <DropdownMenuItem onClick={() => setSortBy("complexity")}>
                  Complexity
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        </CardContent>
      </Card>

      {/* Documents Grid */}
      {sortedDocuments.length === 0 ? (
        <Card className="neo-card">
          <CardContent className="p-12 text-center">
            <FileText className="w-16 h-16 mx-auto text-slate-600 mb-4" />
            <h3 className="text-xl font-semibold text-white mb-2">No documents found</h3>
            <p className="text-slate-400 mb-6">
              {searchTerm || filterBy !== "all" 
                ? "Try adjusting your search or filter criteria."
                : "Upload your first document to get started."
              }
            </p>
            <Link href="/upload">
              <Button className="neo-button">
                <Upload className="w-4 h-4 mr-2" />
                Upload Document
              </Button>
            </Link>
          </CardContent>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {sortedDocuments.map((doc) => {
            const complexity = getComplexityLevel(doc.complexity_score);
            
            return (
              <Card key={doc.document_id} className="neo-card group hover:shadow-neo-lg transition-all duration-300">
                <CardHeader className="pb-3">
                  <div className="flex items-start justify-between">
                    <div className="flex-1 min-w-0">
                      <CardTitle className="text-base truncate" title={doc.filename}>
                        {doc.filename}
                      </CardTitle>
                      <p className="text-slate-400 text-sm mt-1">{doc.subject}</p>
                    </div>
                    
                    <DropdownMenu>
                      <DropdownMenuTrigger asChild>
                        <Button variant="ghost" size="sm" className="opacity-0 group-hover:opacity-100 transition-opacity">
                          <MoreVertical className="w-4 h-4" />
                        </Button>
                      </DropdownMenuTrigger>
                      <DropdownMenuContent>
                        <DropdownMenuItem>
                          <Eye className="w-4 h-4 mr-2" />
                          View Details
                        </DropdownMenuItem>
                        <DropdownMenuItem>
                          <Download className="w-4 h-4 mr-2" />
                          Download
                        </DropdownMenuItem>
                        <DropdownMenuItem className="text-red-400">
                          <Trash2 className="w-4 h-4 mr-2" />
                          Delete
                        </DropdownMenuItem>
                      </DropdownMenuContent>
                    </DropdownMenu>
                  </div>
                </CardHeader>
                
                <CardContent className="space-y-4">
                  <div className="flex items-center gap-2">
                    <Badge variant="outline" className="text-xs">
                      {doc.chunk_count} chunks
                    </Badge>
                    <Badge variant="outline" className={`text-xs ${complexity.color} text-white`}>
                      {complexity.label}
                    </Badge>
                  </div>
                  
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span className="text-slate-400">Uploaded:</span>
                      <span className="text-slate-300">
                        {new Date(doc.upload_date).toLocaleDateString()}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-400">Complexity:</span>
                      <span className="text-slate-300">
                        {Math.round(doc.complexity_score * 100)}%
                      </span>
                    </div>
                    {doc.file_size_mb && (
                      <div className="flex justify-between">
                        <span className="text-slate-400">Size:</span>
                        <span className="text-slate-300">{doc.file_size_mb.toFixed(1)} MB</span>
                      </div>
                    )}
                  </div>
                  
                  <div className="flex gap-2 pt-2">
                    <Link href={`/ask?doc=${doc.document_id}`} className="flex-1">
                      <Button size="sm" className="w-full neo-button">
                        <Eye className="w-4 h-4 mr-1" />
                        Ask Questions
                      </Button>
                    </Link>
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </div>
      )}
    </div>
  );
}
