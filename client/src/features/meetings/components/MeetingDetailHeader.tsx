"use client";

import { useRouter } from "next/navigation";
import { Menu, ArrowLeft, RefreshCw } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useAppContext } from "@/lib/app-context";

export function MeetingDetailHeader({
  title,
  date,
  generatedAt,
  isRegenerating,
  onRegenerate,
}: {
  title: string;
  date: string | null;
  generatedAt: string | null;
  isRegenerating: boolean;
  onRegenerate: () => void;
}) {
  const router = useRouter();
  const { setSidebarOpen } = useAppContext();

  return (
    <header className="flex items-center gap-3 px-4 py-3 md:px-6">
      <Button
        variant="ghost"
        size="icon"
        onClick={() => setSidebarOpen(true)}
        className="md:hidden"
      >
        <Menu className="h-5 w-5" />
      </Button>
      <Button variant="ghost" size="icon" onClick={() => router.back()}>
        <ArrowLeft className="h-5 w-5" />
      </Button>
      <div className="flex flex-1 items-center justify-between">
        <div>
          <h1 className="text-xl font-semibold">{title}</h1>
          {date && (
            <p className="text-sm text-muted-foreground">
              {new Date(date).toLocaleDateString()}
            </p>
          )}
        </div>
        <div className="flex items-center gap-2">
          {generatedAt && (
            <p className="text-xs text-muted-foreground">
              Generated {new Date(generatedAt).toLocaleDateString()}
            </p>
          )}
          <Button
            variant="outline"
            size="sm"
            onClick={onRegenerate}
            disabled={isRegenerating}
          >
            <RefreshCw
              className={`h-4 w-4 ${isRegenerating ? "animate-spin" : ""}`}
            />
            {isRegenerating ? "Generating..." : "Regenerate"}
          </Button>
        </div>
      </div>
    </header>
  );
}
