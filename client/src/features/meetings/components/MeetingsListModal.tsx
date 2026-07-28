"use client";

import { useState, useMemo, useEffect } from "react";
import Link from "next/link";
import {
  Search,
  Calendar,
  ChevronLeft,
  ChevronRight,
  Video,
  VideoOff,
} from "lucide-react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from "@/components/ui/dialog";
import type { Meeting } from "@/types";

function useDebounce<T>(value: T, delay: number): T {
  const [debounced, setDebounced] = useState(value);
  useEffect(() => {
    const timer = setTimeout(() => setDebounced(value), delay);
    return () => clearTimeout(timer);
  }, [value, delay]);
  return debounced;
}

interface MeetingsListModalProps {
  open: boolean;
  onClose: () => void;
  meetings: Meeting[];
}

export function MeetingsListModal({
  open,
  onClose,
  meetings,
}: MeetingsListModalProps) {
  const [search, setSearch] = useState("");
  const [dateFrom, setDateFrom] = useState("");
  const [dateTo, setDateTo] = useState("");
  const [sortOrder, setSortOrder] = useState<"latest" | "oldest">("latest");
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(10);

  const debouncedSearch = useDebounce(search, 250);

  useEffect(() => {
    setPage(1);
  }, [debouncedSearch, dateFrom, dateTo, sortOrder, pageSize]);

  useEffect(() => {
    if (!open) {
      setSearch("");
      setDateFrom("");
      setDateTo("");
      setSortOrder("latest");
      setPage(1);
      setPageSize(10);
    }
  }, [open]);

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
  const paginated = filtered.slice(
    (safePage - 1) * pageSize,
    safePage * pageSize,
  );

  return (
    <Dialog open={open} onOpenChange={(o) => !o && onClose()}>
      <DialogContent className="sm:max-w-5xl">
        <DialogHeader>
          <DialogTitle>Meetings</DialogTitle>
          <DialogDescription>
            Browse and search meetings in this project.
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-3">
          <div className="flex flex-wrap items-center gap-3">
            <div className="relative min-w-[200px] flex-1">
              <Search className="absolute left-2.5 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <Input
                placeholder="Search by title..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="h-9 pl-9"
              />
            </div>

            <div className="flex items-center gap-2">
              <Calendar className="h-4 w-4 shrink-0 text-muted-foreground" />
              <input
                type="date"
                value={dateFrom}
                onChange={(e) => setDateFrom(e.target.value)}
                className="h-9 rounded-md border border-input bg-transparent px-3 text-sm"
              />
              <span className="text-sm text-muted-foreground">-</span>
              <input
                type="date"
                value={dateTo}
                onChange={(e) => setDateTo(e.target.value)}
                className="h-9 rounded-md border border-input bg-transparent px-3 text-sm"
              />
            </div>

            <Select value={sortOrder} onValueChange={(v) => setSortOrder(v as "latest" | "oldest")}>
              <SelectTrigger className="w-36">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="latest">Latest first</SelectItem>
                <SelectItem value="oldest">Oldest first</SelectItem>
              </SelectContent>
            </Select>

            <Select value={String(pageSize)} onValueChange={(v) => setPageSize(Number(v))}>
              <SelectTrigger className="w-20">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="5">5</SelectItem>
                <SelectItem value="10">10</SelectItem>
                <SelectItem value="15">15</SelectItem>
                <SelectItem value="20">20</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <ScrollArea className="h-[400px]">
            {paginated.length === 0 ? (
              <div className="flex h-full items-center justify-center">
                <p className="text-sm text-muted-foreground">
                  {meetings.length === 0 ? "No meetings yet" : "No matches"}
                </p>
              </div>
            ) : (
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b text-left text-muted-foreground">
                    <th className="pb-2 font-medium">Title</th>
                    <th className="pb-2 font-medium">Date</th>
                    <th className="pb-2 font-medium">Provider</th>
                    <th className="pb-2 font-medium">Transcript</th>
                  </tr>
                </thead>
                <tbody>
                  {paginated.map((m) => (
                    <tr
                      key={m.id}
                      className="border-b last:border-0"
                    >
                      <td className="py-2.5">
                        <Link
                          href={`/meetings/${m.id}`}
                          onClick={onClose}
                          className="flex items-center gap-2 font-medium text-foreground hover:text-primary"
                        >
                          <Video className="h-4 w-4 shrink-0 text-muted-foreground" />
                          <span className="truncate">{m.title}</span>
                        </Link>
                      </td>
                      <td className="py-2.5 text-muted-foreground">
                        {m.meeting_date
                          ? new Date(m.meeting_date).toLocaleDateString(
                              undefined,
                              {
                                year: "numeric",
                                month: "short",
                                day: "numeric",
                              },
                            )
                          : "—"}
                      </td>
                      <td className="py-2.5">
                        <span className="inline-flex items-center gap-1 text-muted-foreground">
                          {m.meeting_provider === "google_meet" ? (
                            <Video className="h-3.5 w-3.5" />
                          ) : (
                            <VideoOff className="h-3.5 w-3.5" />
                          )}
                          {m.meeting_provider === "google_meet"
                            ? "Google Meet"
                            : "Manual"}
                        </span>
                      </td>
                      <td className="py-2.5">
                        {m.transcript_status ? (
                          <span
                            className={`inline-block rounded-full px-2 py-0.5 text-xs font-medium ${
                              m.transcript_status === "completed"
                                ? "bg-green-100 text-green-700"
                                : m.transcript_status === "failed"
                                  ? "bg-red-100 text-red-700"
                                  : "bg-yellow-100 text-yellow-700"
                            }`}
                          >
                            {m.transcript_status}
                          </span>
                        ) : (
                          <span className="text-muted-foreground">—</span>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </ScrollArea>

          <div className="flex items-center justify-between">
            <span className="text-xs text-muted-foreground">
              {filtered.length} meeting{filtered.length !== 1 ? "s" : ""}
            </span>
            <div className="flex items-center gap-2">
              <Button
                variant="outline"
                size="sm"
                disabled={safePage <= 1}
                onClick={() => setPage((p) => Math.max(1, p - 1))}
              >
                <ChevronLeft className="h-4 w-4" />
              </Button>
              <span className="text-xs text-muted-foreground">
                {safePage} / {totalPages}
              </span>
              <Button
                variant="outline"
                size="sm"
                disabled={safePage >= totalPages}
                onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
              >
                <ChevronRight className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}
