import { Badge } from "@/components/ui/badge";

const VARIANTS: Record<string, { label: string; className: string }> = {
  pending: { label: "Pending", className: "bg-yellow-100 text-yellow-800" },
  processing: { label: "Processing", className: "bg-blue-100 text-blue-800" },
  completed: { label: "Completed", className: "bg-green-100 text-green-800" },
  failed: { label: "Failed", className: "bg-red-100 text-red-800" },
};

export function TranscriptStatusBadge({
  status,
}: {
  status: string | null | undefined;
}) {
  if (!status) return null;
  const v = VARIANTS[status] || {
    label: status,
    className: "bg-gray-100 text-gray-800",
  };
  return (
    <Badge className={v.className} variant="outline">
      {v.label}
    </Badge>
  );
}
