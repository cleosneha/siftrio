"use client";

import { Menu, Plus } from "lucide-react";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { useWorkspaces } from "@/features/workspaces/hooks/useWorkspaces";
import { useAppContext } from "@/lib/app-context";

export default function DashboardPage() {
  const { setSidebarOpen, setShowCreateWorkspace } = useAppContext();
  const { data: workspacesData } = useWorkspaces();
  const workspaces = workspacesData?.data ?? [];

  return (
    <>
      <header className="flex items-center gap-3 px-4 py-3 md:px-6">
        <Button
          variant="ghost"
          size="icon"
          onClick={() => setSidebarOpen(true)}
          className="md:hidden"
        >
          <Menu className="h-5 w-5" />
        </Button>
        <h1 className="text-xl font-semibold">Dashboard</h1>
      </header>

      <div className="flex-1 p-4 md:p-6">
        <div className="mb-6">
          <h2 className="text-lg font-medium">Workspaces</h2>
          <p className="text-sm text-muted-foreground">
            Select a workspace to view its clients and projects
          </p>
        </div>

        {workspaces.length === 0 ? (
          <div className="flex flex-col items-center justify-center rounded-lg border-2 border-dashed p-12 text-center">
            <h3 className="mb-2 text-lg font-medium">No workspaces yet</h3>
            <p className="mb-4 text-sm text-muted-foreground">
              Create your first workspace to get started
            </p>
            <Button onClick={() => setShowCreateWorkspace(true)}>
              <Plus className="h-4 w-4" />
              Create Workspace
            </Button>
          </div>
        ) : (
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {workspaces.map((workspace) => (
              <Link key={workspace.id} href={`/workspaces/${workspace.id}`}>
                <Card className="transition-shadow hover:shadow-sm">
                  <CardHeader>
                    <CardTitle>{workspace.name}</CardTitle>
                    {workspace.description && (
                      <CardDescription className="line-clamp-2">
                        {workspace.description}
                      </CardDescription>
                    )}
                  </CardHeader>
                </Card>
              </Link>
            ))}
          </div>
        )}
      </div>
    </>
  );
}
