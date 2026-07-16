"use client";

import { useState, useMemo, useEffect, useCallback } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { Video, ChevronLeft, ChevronRight, Search, Calendar, X } from "lucide-react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import { cn } from "@/lib/utils";
import { useMeetingsDrawer } from "./meetings-drawer-store";

const SIDEBAR_WIDTH = 256;
const DRAWER_WIDTH = 288;
const MOBILE_BREAKPOINT = 768;

function useMediaQuery(query: string): boolean {
  const [matches, setMatches] = useState(() =>
    typeof window !== "undefined" ? window.matchMedia(query).matches : false,
  );

  useEffect(() => {
    const mq = window.matchMedia(query);
    const handler = (e: MediaQueryListEvent) => setMatches(e.matches);
    mq.addEventListener("change", handler);
    return () => mq.removeEventListener("change", handler);
  }, [query]);

  return matches;
}

function useDebounce<T>(value: T, delay: number): T {
  const [debounced, setDebounced] = useState(value);
  useEffect(() => {
    const timer = setTimeout(() => setDebounced(value), delay);
    return () => clearTimeout(timer);
  }, [value, delay]);
  return debounced;
}

export function MeetingsDrawer() {
  const isMobile = useMediaQuery(`(max-width: ${MOBILE_BREAKPOINT - 1}px)`);
  const { open, meetings, setOpen } = useMeetingsDrawer();
  const [search, setSearch] = useState("");
  const [dateFrom, setDateFrom] = useState("");
  const [dateTo, setDateTo] = useState("");
  const [sortOrder, setSortOrder] = useState<"latest" | "oldest">("latest");
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(10);
  const pathname = usePathname();

  const debouncedSearch = useDebounce(search, 250);

  useEffect(() => {
    const id = setTimeout(() => setPage(1), 0);
    return () => clearTimeout(id);
  }, [debouncedSearch, dateFrom, dateTo, sortOrder, pageSize]);

  const handleClose = useCallback(() => {
    setOpen(false);
  }, [setOpen]);

  useEffect(() => {
    if (!open) return;
    const handler = (e: KeyboardEvent) => {
      if (e.key === "Escape") handleClose();
    };
    document.addEventListener("keydown", handler);
    document.body.style.overflow = "hidden";
    return () => {
      document.removeEventListener("keydown", handler);
      document.body.style.overflow = "";
    };
  }, [open, handleClose]);

  const filtered = useMemo(() => {
    let result = [...meetings];
    if (debouncedSearch) {
      const q = debouncedSearch.toLowerCase();
      result = result.filter((m) => m.title.toLowerCase().includes(q));
    }
    if (dateFrom) {
      const from = new Date(dateFrom).getTime();
      result = result.filter((m) => {
        if (!m.meeting_date) return false;
        return new Date(m.meeting_date).getTime() >= from;
      });
    }
    if (dateTo) {
      const to = new Date(dateTo).getTime();
      result = result.filter((m) => {
        if (!m.meeting_date) return false;
        return new Date(m.meeting_date).getTime() <= to;
      });
    }
    result.sort((a, b) => {
      const da = a.meeting_date ? new Date(a.meeting_date).getTime() : 0;
      const db = b.meeting_date ? new Date(b.meeting_date).getTime() : 0;
      return sortOrder === "latest" ? db - da : da - db;
    });
    return result;
  }, [meetings, debouncedSearch, dateFrom, dateTo, sortOrder]);

  const totalPages = Math.max(1, Math.ceil(filtered.length / pageSize));
  const safePage = Math.min(page, totalPages);
  const paginated = filtered.slice((safePage - 1) * pageSize, safePage * pageSize);

  const drawerContent = (
    <>
      <div className="flex items-center justify-between px-3 py-2.5">
        <span className="text-sm font-medium">Meetings</span>
        <Button variant="ghost" size="icon-sm" onClick={handleClose}>
          <X className="h-4 w-4" />
        </Button>
      </div>

      <div className="space-y-2 p-3">
        <div className="relative">
          <Search className="absolute left-2 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-muted-foreground" />
          <Input
            placeholder="Search meetings..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="h-7 pl-7 text-xs"
          />
        </div>

        <div className="flex items-center gap-1.5">
          <Calendar className="h-3 w-3 shrink-0 text-muted-foreground" />
          <input
            type="date"
            value={dateFrom}
            onChange={(e) => setDateFrom(e.target.value)}
            className="h-7 w-full min-w-0 rounded-md border border-input bg-transparent px-2 text-xs"
          />
          <span className="text-xs text-muted-foreground">-</span>
          <input
            type="date"
            value={dateTo}
            onChange={(e) => setDateTo(e.target.value)}
            className="h-7 w-full min-w-0 rounded-md border border-input bg-transparent px-2 text-xs"
          />
        </div>

        <div className="flex items-center gap-2">
          <select
            value={sortOrder}
            onChange={(e) => setSortOrder(e.target.value as "latest" | "oldest")}
            className="h-7 flex-1 rounded-md border border-input bg-transparent px-2 text-xs"
          >
            <option value="latest">Latest first</option>
            <option value="oldest">Oldest first</option>
          </select>
          <select
            value={pageSize}
            onChange={(e) => setPageSize(Number(e.target.value))}
            className="h-7 w-16 rounded-md border border-input bg-transparent px-1 text-xs"
          >
            <option value={5}>5</option>
            <option value={10}>10</option>
            <option value={15}>15</option>
            <option value={20}>20</option>
          </select>
        </div>
      </div>

      <ScrollArea className="flex-1">
        {paginated.length === 0 ? (
          <p className="p-4 text-center text-xs text-muted-foreground">
            {meetings.length === 0 ? "No meetings yet" : "No matches"}
          </p>
        ) : (
          <div className="space-y-0.5 p-2">
            {paginated.map((m) => {
              const isActive = pathname === `/meetings/${m.id}`;
              return (
                <Link
                  key={m.id}
                  href={`/meetings/${m.id}`}
                  onClick={handleClose}
                  className={cn(
                    "flex items-center gap-2 rounded-md px-2.5 py-1.5 text-xs transition-colors",
                    isActive
                      ? "bg-accent font-medium text-accent-foreground"
                      : "text-muted-foreground hover:bg-accent hover:text-accent-foreground",
                  )}
                >
                  <Video className="h-3 w-3 shrink-0" />
                  <span className="truncate">{m.title}</span>
                  {m.meeting_date && (
                    <span className="shrink-0 text-[10px] text-muted-foreground/60">
                      {new Date(m.meeting_date).toLocaleDateString(undefined, {
                        month: "short",
                        day: "numeric",
                      })}
                    </span>
                  )}
                </Link>
              );
            })}
          </div>
        )}
      </ScrollArea>

      <div className="flex items-center justify-between px-3 py-2">
        <Button
          variant="ghost"
          size="xs"
          disabled={safePage <= 1}
          onClick={() => setPage((p) => Math.max(1, p - 1))}
        >
          <ChevronLeft className="h-3 w-3" />
        </Button>
        <span className="text-[11px] text-muted-foreground">
          {safePage} / {totalPages}
        </span>
        <Button
          variant="ghost"
          size="xs"
          disabled={safePage >= totalPages}
          onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
        >
          <ChevronRight className="h-3 w-3" />
        </Button>
      </div>
    </>
  );

  if (isMobile) {
    return (
      <>
        {/* full-viewport overlay */}
        <div
          className={cn(
            "fixed inset-0 z-30 bg-black/40 transition-opacity duration-200",
            open ? "opacity-100" : "pointer-events-none opacity-0",
          )}
          onClick={handleClose}
        />

        {/* slide-in drawer from right edge */}
        <div
          className={cn(
            "fixed top-0 right-0 z-40 h-full w-[85vw] max-w-sm bg-popover shadow-xl transition-transform duration-200",
            open ? "translate-x-0" : "translate-x-full",
          )}
        >
          <div className="flex h-full flex-col">
            {drawerContent}
          </div>
        </div>
      </>
    );
  }

  return (
    <>
      {/* overlay — covers main content from right edge of drawer */}
      <div
        className={cn(
          "fixed inset-y-0 z-30 bg-black/40 transition-opacity duration-200",
          open ? "opacity-100" : "pointer-events-none opacity-0",
        )}
        style={{ left: SIDEBAR_WIDTH + DRAWER_WIDTH }}
        onClick={handleClose}
      />

      {/* drawer — anchored at right edge of workspace sidebar, expands rightward */}
      <div
        className="fixed top-0 z-40 h-full overflow-hidden transition-[width] duration-200"
        style={{
          left: SIDEBAR_WIDTH,
          width: open ? DRAWER_WIDTH : 0,
        }}
      >
        <div
          className="flex h-full flex-col bg-popover shadow-xl"
          style={{ width: DRAWER_WIDTH }}
        >
          {drawerContent}
        </div>
      </div>
    </>
  );
}
