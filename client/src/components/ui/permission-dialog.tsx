"use client";

import { useEffect, useState } from "react";
import { ShieldAlert } from "lucide-react";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";

const PERMISSION_EVENT = "permission-required";

function dispatchPermissionRequired(message?: string) {
  window.dispatchEvent(
    new CustomEvent<{ message?: string }>(PERMISSION_EVENT, { detail: { message } }),
  );
}

export function PermissionDialog() {
  const [open, setOpen] = useState(false);
  const [message, setMessage] = useState<string | null>(null);

  useEffect(() => {
    const handler = (event: Event) => {
      const detail = (event as CustomEvent<{ message?: string }>).detail;
      setMessage(detail?.message ?? null);
      setOpen(true);
    };
    window.addEventListener(PERMISSION_EVENT, handler);
    return () => window.removeEventListener(PERMISSION_EVENT, handler);
  }, []);

  return (
    <Dialog open={open} onOpenChange={(isOpen) => !isOpen && setOpen(false)}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <ShieldAlert className="h-4 w-4 text-destructive" />
            Permission required
          </DialogTitle>
          <DialogDescription>
            Admin/owner permissions are required for this action.
            {message && <span className="mt-1 block">{message}</span>}
          </DialogDescription>
        </DialogHeader>
        <DialogFooter>
          <Button onClick={() => setOpen(false)}>Got it</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}

export { dispatchPermissionRequired };
