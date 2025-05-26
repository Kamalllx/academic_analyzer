"use client";

import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { toast } from "sonner"; // Changed import
import { apiService } from "@/lib/api";
import { Upload, FileText, CheckCircle, Loader2 } from "lucide-react";

export default function UploadPage() {
  const [file, setFile] = useState<File | null>(null);
  const [subject, setSubject] = useState("");
  const [uploading, setUploading] = useState(false);
  const [uploadResult, setUploadResult] = useState<any>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (selectedFile) {
      if (selectedFile.type === "application/pdf") {
        setFile(selectedFile);
      } else {
        toast.error("Invalid file type. Please select a PDF file.");
      }
    }
  };

  const handleUpload = async () => {
    if (!file || !subject.trim()) {
      toast.error("Please select a file and enter a subject.");
      return;
    }

    setUploading(true);
    try {
      const response = await apiService.uploadPDF(file, subject, "cli_user");
      setUploadResult(response.data);
      toast.success("Upload successful! Your document has been processed and is ready for questions.");
      
      // Reset form
      setFile(null);
      setSubject("");
    } catch (error) {
      toast.error("Upload failed. There was an error uploading your document. Please try again.");
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      <div className="text-center space-y-4">
        <h1 className="text-4xl font-bold glow-text">Upload Document</h1>
        <p className="text-slate-400 text-lg">
          Upload your academic documents for AI-powered analysis and Q&A
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Upload Form */}
        <Card className="neo-card">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Upload className="w-5 h-5 text-blue-400" />
              Document Upload
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="space-y-2">
              <Label htmlFor="file">PDF Document</Label>
              <div className="border-2 border-dashed border-slate-600 rounded-lg p-8 text-center">
                <Input
                  id="file"
                  type="file"
                  accept=".pdf"
                  onChange={handleFileChange}
                  className="hidden"
                />
                <label htmlFor="file" className="cursor-pointer space-y-4">
                  <div className="w-16 h-16 mx-auto bg-blue-500/20 rounded-full flex items-center justify-center">
                    <FileText className="w-8 h-8 text-blue-400" />
                  </div>
                  <div>
                    <p className="text-white font-medium">
                      {file ? file.name : "Click to select PDF"}
                    </p>
                    <p className="text-slate-400 text-sm">
                      {file ? `${(file.size / 1024 / 1024).toFixed(2)} MB` : "Drag and drop or click to browse"}
                    </p>
                  </div>
                </label>
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="subject">Subject/Topic</Label>
              <Input
                id="subject"
                placeholder="e.g., Machine Learning, Physics, History..."
                value={subject}
                onChange={(e) => setSubject(e.target.value)}
                className="neo-input"
              />
            </div>

            <Button
              onClick={handleUpload}
              disabled={!file || !subject || uploading}
              className="w-full neo-button"
            >
              {uploading ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  Processing...
                </>
              ) : (
                <>
                  <Upload className="w-4 h-4 mr-2" />
                  Upload & Process
                </>
              )}
            </Button>
          </CardContent>
        </Card>

        {/* Upload Result */}
        {uploadResult && (
          <Card className="neo-card">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <CheckCircle className="w-5 h-5 text-green-400" />
                Processing Complete
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-slate-400">Document ID:</span>
                  <span className="text-white font-mono text-sm">
                    {uploadResult.document_id}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400">Text Chunks:</span>
                  <span className="text-white">{uploadResult.chunks}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400">Complexity Score:</span>
                  <span className="text-white">
                    {(uploadResult.complexity_score * 100).toFixed(1)}%
                  </span>
                </div>
              </div>

              <div className="pt-4 border-t border-slate-700">
                <p className="text-slate-300 mb-4">
                  Your document is ready! You can now:
                </p>
                <div className="space-y-2">
                  <Button variant="outline" size="sm" className="w-full" asChild>
                    <a href="/ask">Ask Questions About This Document</a>
                  </Button>
                  <Button variant="outline" size="sm" className="w-full" asChild>
                    <a href="/library">View in Document Library</a>
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Upload Guidelines */}
        <Card className="neo-card lg:col-span-2">
          <CardHeader>
            <CardTitle>Upload Guidelines</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-3">
                <h4 className="font-semibold text-green-400">✅ Supported</h4>
                <ul className="space-y-1 text-slate-300 text-sm">
                  <li>• PDF documents up to 50MB</li>
                  <li>• Academic papers and journals</li>
                  <li>• Textbooks and lecture notes</li>
                  <li>• Research articles</li>
                  <li>• Technical documentation</li>
                </ul>
              </div>
              <div className="space-y-3">
                <h4 className="font-semibold text-red-400">❌ Not Supported</h4>
                <ul className="space-y-1 text-slate-300 text-sm">
                  <li>• Scanned images without OCR</li>
                  <li>• Password-protected PDFs</li>
                  <li>• Corrupted or damaged files</li>
                  <li>• Non-academic content</li>
                  <li>• Copyrighted material without permission</li>
                </ul>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
