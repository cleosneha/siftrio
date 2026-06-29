"use client";

import { useState, useMemo, type ReactNode } from "react";
import { Search, Check, X, Pencil, ExternalLink } from "lucide-react";
import Link from "next/link";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Textarea } from "@/components/ui/textarea";

interface FieldConfig {
  key: string;
  label: string;
  type?: "text" | "textarea" | "select" | "date";
  options?: { label: string; value: string }[];
}

interface StatusOption {
  label: string;
  value: string;
}

interface BaseItem {
  id: string;
  title: string;
  description?: string | null;
  status: string;
  meeting_id?: string;
  meeting_title?: string | null;
  [key: string]: any;
}

interface TabConfig {
  fields: FieldConfig[];
  statusOptions: StatusOption[];
  extraBadge?: (item: BaseItem) => { label: string; variant: string } | null;
  approvalActions?: boolean;
  emptyLabel: string;
}

const STATUS_VARIANTS: Record<string, string> = {
  pending: "outline",
  approved: "default",
  rejected: "destructive",
  implemented: "secondary",
  in_progress: "default",
  completed: "secondary",
  cancelled: "outline",
  active: "default",
  superseded: "outline",
  open: "outline",
  mitigated: "secondary",
  closed: "default",
  answered: "default",
};

export function KnowledgeTabBase({
  items,
  config,
  label,
  onUpdate,
}: {
  items: BaseItem[];
  config: TabConfig;
  label: string;
  onUpdate: (id: string, data: any) => Promise<any>;
}) {
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState<string>("");
  const [editingItem, setEditingItem] = useState<BaseItem | null>(null);
  const [editForm, setEditForm] = useState<Record<string, string>>({});

  const filtered = useMemo(() => {
    return items.filter((item) => {
      const matchesSearch =
        !search ||
        item.title?.toLowerCase().includes(search.toLowerCase()) ||
        item.description?.toLowerCase().includes(search.toLowerCase());
      const matchesStatus = !statusFilter || item.status === statusFilter;
      return matchesSearch && matchesStatus;
    });
  }, [items, search, statusFilter]);

  const handleEdit = (item: BaseItem) => {
    setEditingItem(item);
    const form: Record<string, string> = {};
    for (const field of config.fields) {
      form[field.key] = item[field.key] ?? "";
    }
    form.status = item.status ?? "";
    setEditForm(form);
  };

  const handleSave = async () => {
    if (!editingItem) return;
    await onUpdate(editingItem.id, editForm);
    setEditingItem(null);
  };

  const handleApproval = async (item: BaseItem, status: string) => {
    await onUpdate(item.id, { status });
  };

  return (
    <div>
      <div className="mb-4 flex flex-wrap items-center gap-2">
        <div className="relative flex-1">
          <Search className="absolute left-2.5 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            placeholder="Search..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="pl-8"
          />
        </div>
        <select
          className="h-8 rounded-lg border border-input bg-transparent px-2.5 text-sm"
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
        >
          <option value="">All Status</option>
          {config.statusOptions.map((opt) => (
            <option key={opt.value} value={opt.value}>
              {opt.label}
            </option>
          ))}
        </select>
      </div>

      {filtered.length === 0 ? (
        <div className="flex flex-col items-center justify-center rounded-lg border-2 border-dashed p-8 text-center">
          <p className="text-sm text-muted-foreground">
            {items.length === 0 ? config.emptyLabel : "No matches found"}
          </p>
        </div>
      ) : (
        <div className="space-y-3">
          {filtered.map((item) => (
            <Card key={item.id} size="sm">
              <CardHeader>
                <div className="flex items-start justify-between gap-2">
                  <div>
                    <CardTitle className="text-sm font-medium">
                      {item.title}
                    </CardTitle>
                    {item.description && (
                      <CardDescription className="mt-1">
                        {item.description}
                      </CardDescription>
                    )}
                  </div>
                  <div className="flex shrink-0 items-center gap-1.5">
                    <Badge
                      variant={(STATUS_VARIANTS[item.status] ?? "outline") as any}
                    >
                      {item.status?.replace("_", " ")}
                    </Badge>
                    {config.extraBadge && config.extraBadge(item) && (
                      <Badge
                        variant={(config.extraBadge(item)?.variant ?? "outline") as any}
                      >
                        {config.extraBadge(item)?.label}
                      </Badge>
                    )}
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <div className="flex flex-wrap items-center gap-2 text-xs text-muted-foreground">
                  {item.meeting_title && (
                    <Link
                      href={`/meetings/${item.meeting_id}`}
                      className="flex items-center gap-1 hover:text-foreground"
                    >
                      <ExternalLink className="h-3 w-3" />
                      {item.meeting_title}
                    </Link>
                  )}
                  <Button
                    variant="ghost"
                    size="xs"
                    onClick={() => handleEdit(item)}
                  >
                    <Pencil className="h-3 w-3" />
                    Edit
                  </Button>
                  {config.approvalActions && item.status === "pending" && (
                    <>
                      <Button
                        variant="ghost"
                        size="xs"
                        onClick={() => handleApproval(item, "approved")}
                      >
                        <Check className="h-3 w-3 text-green-600" />
                        Approve
                      </Button>
                      <Button
                        variant="ghost"
                        size="xs"
                        onClick={() => handleApproval(item, "rejected")}
                      >
                        <X className="h-3 w-3 text-red-600" />
                        Reject
                      </Button>
                    </>
                  )}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      <Dialog open={!!editingItem} onOpenChange={(open) => !open && setEditingItem(null)}>
        <DialogContent className="sm:max-w-lg">
          <DialogHeader>
            <DialogTitle>Edit {label}</DialogTitle>
            <DialogDescription>Update the fields below.</DialogDescription>
          </DialogHeader>
          <div className="grid gap-3">
            {config.fields.map((field) => (
              <div key={field.key}>
                <label className="mb-1 block text-sm font-medium">
                  {field.label}
                </label>
                {field.type === "textarea" ? (
                  <Textarea
                    value={editForm[field.key] ?? ""}
                    onChange={(e) =>
                      setEditForm((f) => ({ ...f, [field.key]: e.target.value }))
                    }
                  />
                ) : field.type === "select" ? (
                  <select
                    className="h-8 w-full rounded-lg border border-input bg-transparent px-2.5 text-sm"
                    value={editForm[field.key] ?? ""}
                    onChange={(e) =>
                      setEditForm((f) => ({ ...f, [field.key]: e.target.value }))
                    }
                  >
                    <option value="">None</option>
                    {field.options?.map((opt) => (
                      <option key={opt.value} value={opt.value}>
                        {opt.label}
                      </option>
                    ))}
                  </select>
                ) : field.type === "date" ? (
                  <Input
                    type="date"
                    value={editForm[field.key] ?? ""}
                    onChange={(e) =>
                      setEditForm((f) => ({ ...f, [field.key]: e.target.value }))
                    }
                  />
                ) : (
                  <Input
                    value={editForm[field.key] ?? ""}
                    onChange={(e) =>
                      setEditForm((f) => ({ ...f, [field.key]: e.target.value }))
                    }
                  />
                )}
              </div>
            ))}
            <div>
              <label className="mb-1 block text-sm font-medium">Status</label>
              <select
                className="h-8 w-full rounded-lg border border-input bg-transparent px-2.5 text-sm"
                value={editForm.status ?? ""}
                onChange={(e) =>
                  setEditForm((f) => ({ ...f, status: e.target.value }))
                }
              >
                {config.statusOptions.map((opt) => (
                  <option key={opt.value} value={opt.value}>
                    {opt.label}
                  </option>
                ))}
              </select>
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setEditingItem(null)}>
              Cancel
            </Button>
            <Button onClick={handleSave}>Save</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
