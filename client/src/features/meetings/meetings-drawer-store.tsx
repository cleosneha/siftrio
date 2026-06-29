"use client";

import { createContext, useContext, useState, type ReactNode } from "react";

export interface Meeting {
  id: string;
  title: string;
  meeting_date?: string | null;
  transcript?: string | null;
}

interface MeetingsDrawerContextType {
  open: boolean;
  meetings: Meeting[];
  setOpen: (open: boolean) => void;
  setMeetings: (meetings: Meeting[]) => void;
}

const MeetingsDrawerContext = createContext<MeetingsDrawerContextType | null>(null);

export function MeetingsDrawerProvider({ children }: { children: ReactNode }) {
  const [open, setOpen] = useState(false);
  const [meetings, setMeetings] = useState<Meeting[]>([]);

  return (
    <MeetingsDrawerContext.Provider value={{ open, meetings, setOpen, setMeetings }}>
      {children}
    </MeetingsDrawerContext.Provider>
  );
}

export function useMeetingsDrawer() {
  const ctx = useContext(MeetingsDrawerContext);
  if (!ctx) throw new Error("useMeetingsDrawer must be used within MeetingsDrawerProvider");
  return ctx;
}
