import { Badge } from "@/components/ui/badge";

const VARIANTS: Record<string, { label: string; style: React.CSSProperties }> = {
  pending: { label: "Pending", style: { backgroundColor: "var(--status-pending-bg)", color: "var(--status-pending-fg)" } },
  processing: { label: "Processing", style: { backgroundColor: "var(--status-progress-bg)", color: "var(--status-progress-fg)" } },
  completed: { label: "Completed", style: { backgroundColor: "var(--status-done-bg)", color: "var(--status-done-fg)" } },
  failed: { label: "Failed", style: { backgroundColor: "var(--status-error-bg)", color: "var(--status-error-fg)" } },
};

export function TranscriptStatusBadge({
  status,
}: {
  status: string | null | undefined;
}) {
  if (!status) return null;
  const v = VARIANTS[status] || {
    label: status,
    style: { backgroundColor: "var(--status-default-bg)", color: "var(--status-default-fg)" },
  };
  return (
    <Badge style={v.style} variant="outline">
      {v.label}
    </Badge>
  );
}
