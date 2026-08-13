import { toast } from "sonner";

interface ErrorResponseLike {
  response?: {
    status?: number;
    data?: { message?: string };
  };
}

export function isForbiddenError(error: unknown): boolean {
  return (error as ErrorResponseLike | undefined)?.response?.status === 403;
}

export function notifyError(error: unknown, fallback: string): void {
  if (isForbiddenError(error)) return;
  const message =
    (error as ErrorResponseLike | undefined)?.response?.data?.message ||
    (error instanceof Error ? error.message : "") ||
    fallback;
  toast.error(message);
}
