import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Upload, MessageSquare, Brain, BarChart3 } from "lucide-react";
import Link from "next/link";

export function QuickActions() {
  return (
    <Card className="neo-card">
      <CardHeader>
        <CardTitle>Quick Actions</CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        <Link href="/upload" className="block">
          <Button variant="outline" size="sm" className="w-full justify-start">
            <Upload className="w-4 h-4 mr-2" />
            Upload Document
          </Button>
        </Link>
        <Link href="/ask" className="block">
          <Button variant="outline" size="sm" className="w-full justify-start">
            <MessageSquare className="w-4 h-4 mr-2" />
            Ask Question
          </Button>
        </Link>
        <Link href="/tutor" className="block">
          <Button variant="outline" size="sm" className="w-full justify-start">
            <Brain className="w-4 h-4 mr-2" />
            Chat with Tutor
          </Button>
        </Link>
        <Link href="/analytics" className="block">
          <Button variant="outline" size="sm" className="w-full justify-start">
            <BarChart3 className="w-4 h-4 mr-2" />
            View Analytics
          </Button>
        </Link>
      </CardContent>
    </Card>
  );
}
