import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { MessageSquare, FileText, Clock } from "lucide-react";

const recentActivities = [
  {
    id: 1,
    type: "question",
    content: "What is gradient descent in machine learning?",
    document: "ML_Fundamentals.pdf",
    timestamp: "2 hours ago",
  },
  {
    id: 2,
    type: "upload",
    content: "Uploaded new document",
    document: "Neural_Networks.pdf",
    timestamp: "1 day ago",
  },
  {
    id: 3,
    type: "question",
    content: "Explain backpropagation algorithm",
    document: "Deep_Learning.pdf",
    timestamp: "2 days ago",
  },
];

export function RecentActivity() {
  return (
    <Card className="neo-card">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Clock className="w-5 h-5 text-blue-400" />
          Recent Activity
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {recentActivities.map((activity) => (
          <div key={activity.id} className="flex items-start gap-3 p-3 bg-slate-800/50 rounded-lg">
            <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
              activity.type === "question" ? "bg-blue-500/20" : "bg-green-500/20"
            }`}>
              {activity.type === "question" ? (
                <MessageSquare className="w-4 h-4 text-blue-400" />
              ) : (
                <FileText className="w-4 h-4 text-green-400" />
              )}
            </div>
            <div className="flex-1">
              <p className="text-slate-300 text-sm">{activity.content}</p>
              <div className="flex items-center gap-2 mt-1">
                <Badge variant="outline" className="text-xs">
                  {activity.document}
                </Badge>
                <span className="text-slate-500 text-xs">{activity.timestamp}</span>
              </div>
            </div>
          </div>
        ))}
      </CardContent>
    </Card>
  );
}
