import type { FieldErrors } from "react-hook-form";
import { toast } from "sonner";

export function toastFormErrors(errors: FieldErrors, _event?: unknown): void {
  for (const key of Object.keys(errors)) {
    const error = errors[key];
    if (
      error &&
      typeof error === "object" &&
      "message" in error &&
      typeof error.message === "string"
    ) {
      toast.error(error.message);
      return;
    }
  }
  toast.error("Please fix the form errors");
}
