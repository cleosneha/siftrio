"use client";

import { useParams } from "next/navigation";
import { Menu, ArrowLeft } from "lucide-react";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { useProject } from "@/hooks/useProjects";
import { useAppContext } from "@/lib/app-context";

export default function ProjectPage() {
  const params = useParams();
  const projectId = params.projectId as string;
  const { setSidebarOpen } = useAppContext();

  const { data: projectData } = useProject(projectId);
  const project = projectData?.data;

  const statusVariant: Record<
    string,
    "default" | "secondary" | "outline" | "destructive" | "ghost" | "link"
  > = {
    active: "default",
    completed: "secondary",
    archived: "outline",
  };

  return (
    <>
      <header className="flex items-center gap-3 border-b px-4 py-3 md:px-6">
        <Button
          variant="ghost"
          size="icon"
          onClick={() => setSidebarOpen(true)}
          className="md:hidden"
        >
          <Menu className="h-5 w-5" />
        </Button>
        <Link href="/dashboard">
          <Button variant="ghost" size="icon">
            <ArrowLeft className="h-5 w-5" />
          </Button>
        </Link>
        <div className="flex flex-1 items-center justify-between">
          <div>
            <h1 className="text-xl font-semibold">
              {project?.name ?? "Loading..."}
            </h1>
            {project?.description && (
              <p className="text-sm text-muted-foreground">
                {project.description}
              </p>
            )}
          </div>
          {project?.status && (
            <Badge variant={statusVariant[project.status] ?? "outline"}>
              {project.status}
            </Badge>
          )}
        </div>
      </header>

      <div className="flex-1 p-4 md:p-6">
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          <Card>
            <CardHeader>
              <CardTitle>Meetings</CardTitle>
            </CardHeader>
            <CardContent>
              <CardDescription>
                No meetings yet. Meetings will appear here once integrated.
              </CardDescription>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Knowledge Base</CardTitle>
            </CardHeader>
            <CardContent>
              <CardDescription>
                Knowledge base is empty. Documents and insights will appear
                here.
              </CardDescription>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Project Memory Chat</CardTitle>
            </CardHeader>
            <CardContent>
              <CardDescription>
                Chat with the project memory. Conversations will be available
                here.
              </CardDescription>
            </CardContent>
          </Card>
        </div>
      </div>
    </>
  );
}
