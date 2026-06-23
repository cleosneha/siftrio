"use client";

import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { useQuery } from "@tanstack/react-query";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from "@/components/ui/dialog";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { useCreateMeeting } from "@/hooks/useMeetings";
import { projectService } from "@/services/project.service";
import { cn } from "@/lib/utils";

const formSchema = z.object({
  title: z.string().min(1, "Title is required").max(255),
  meeting_type: z.enum(["project", "miscellaneous"]),
  project_id: z.string().optional(),
  tags: z.string().optional(),
  meeting_date: z.string().optional(),
});

type FormValues = z.infer<typeof formSchema>;

interface CreateMeetingModalProps {
  open: boolean;
  onClose: () => void;
  clientId: string;
  defaultProjectId?: string;
}

export function CreateMeetingModal({
  open,
  onClose,
  clientId,
  defaultProjectId,
}: CreateMeetingModalProps) {
  const createMeeting = useCreateMeeting();

  const { data: projectsData } = useQuery({
    queryKey: ["projects", clientId],
    queryFn: () => projectService.list(clientId),
    enabled: open && !!clientId,
  });
  const projects = projectsData?.data ?? [];

  const form = useForm<FormValues>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      title: "",
      meeting_type: defaultProjectId ? "project" : "miscellaneous",
      project_id: defaultProjectId ?? "",
      tags: "",
      meeting_date: "",
    },
  });

  const showTypeSelector = !defaultProjectId;
  const meetingType = form.watch("meeting_type");

  const onSubmit = async (values: FormValues) => {
    const tags = values.tags
      ? values.tags.split(",").map((t) => t.trim()).filter(Boolean)
      : [];

    const result = await createMeeting.mutateAsync({
      client_id: clientId,
      project_id: values.meeting_type === "project" ? values.project_id || null : null,
      title: values.title,
      meeting_type: values.meeting_type,
      tags: values.meeting_type === "project" ? [] : tags,
      meeting_date: values.meeting_date || null,
    });

    form.reset();
    onClose();
  };

  return (
    <Dialog
      open={open}
      onOpenChange={(o) => {
        if (!o) {
          form.reset();
          onClose();
        }
      }}
    >
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Create Meeting</DialogTitle>
          <DialogDescription>
            Create a new meeting and optionally upload a transcript.
          </DialogDescription>
        </DialogHeader>

        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
            <FormField
              control={form.control}
              name="title"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Title</FormLabel>
                  <FormControl>
                    <Input placeholder="Meeting title" autoFocus {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            {showTypeSelector && (
              <FormField
                control={form.control}
                name="meeting_type"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Meeting Type</FormLabel>
                    <FormControl>
                      <div className="flex gap-2">
                        <button
                          type="button"
                          onClick={() => field.onChange("project")}
                          className={cn(
                            "flex-1 rounded-md border px-3 py-2 text-sm font-medium transition-colors",
                            field.value === "project"
                              ? "border-primary bg-primary/10 text-primary"
                              : "border-input hover:bg-accent hover:text-accent-foreground",
                          )}
                        >
                          Project
                        </button>
                        <button
                          type="button"
                          onClick={() => field.onChange("miscellaneous")}
                          className={cn(
                            "flex-1 rounded-md border px-3 py-2 text-sm font-medium transition-colors",
                            field.value === "miscellaneous"
                              ? "border-primary bg-primary/10 text-primary"
                              : "border-input hover:bg-accent hover:text-accent-foreground",
                          )}
                        >
                          Miscellaneous
                        </button>
                      </div>
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
            )}

            {meetingType === "project" && (
              <FormField
                control={form.control}
                name="project_id"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Project</FormLabel>
                    <FormControl>
                      <select
                        value={field.value}
                        onChange={(e) => field.onChange(e.target.value)}
                        className="flex h-10 w-full rounded-md border border-input bg-transparent px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                      >
                        <option value="">Select a project</option>
                        {projects.map((p: { id: string; name: string }) => (
                          <option key={p.id} value={p.id}>
                            {p.name}
                          </option>
                        ))}
                      </select>
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
            )}

            {meetingType === "miscellaneous" && (
              <FormField
                control={form.control}
                name="tags"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Tags (comma separated)</FormLabel>
                    <FormControl>
                      <Input
                        placeholder="design, review, feedback"
                        {...field}
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
            )}

            <FormField
              control={form.control}
              name="meeting_date"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Meeting Date</FormLabel>
                  <FormControl>
                    <Input type="date" {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <DialogFooter>
              <Button
                type="button"
                variant="outline"
                onClick={() => {
                  form.reset();
                  onClose();
                }}
              >
                Cancel
              </Button>
              <Button type="submit" disabled={createMeeting.isPending}>
                {createMeeting.isPending ? "Creating..." : "Create"}
              </Button>
            </DialogFooter>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  );
}
