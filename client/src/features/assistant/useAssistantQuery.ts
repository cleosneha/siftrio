"use client";

import { useMutation } from "@tanstack/react-query";
import { assistantService } from "./assistant.service";

export function useAssistantQuery() {
  return useMutation({
    mutationFn: (question: string) => assistantService.query(question),
  });
}
