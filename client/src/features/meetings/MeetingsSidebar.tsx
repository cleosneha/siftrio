"use client";

import { useState } from "react";
import { Video } from "lucide-react";
import { useMeetingsDrawer } from "./meetings-drawer-store";

export function MeetingsSidebar() {
  const { setOpen } = useMeetingsDrawer();
  const [hovering, setHovering] = useState(false);

  return (
    <div
      className="relative flex cursor-pointer items-center justify-center bg-muted/30 transition-colors hover:bg-muted/60"
      style={{ width: 32, height: 32, borderRadius: 6 }}
      onClick={() => setOpen(true)}
      onMouseEnter={() => setHovering(true)}
      onMouseLeave={() => setHovering(false)}
    >
      <Video className="h-4 w-4 text-muted-foreground" />
      {hovering && (
        <div className="absolute left-10 z-50 whitespace-nowrap rounded-md border bg-popover px-3 py-1.5 text-xs text-popover-foreground shadow-sm pointer-events-none">
          Show all meetings
        </div>
      )}
    </div>
  );
}
