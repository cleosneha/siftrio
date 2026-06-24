"use client";

import { useForm, useWatch } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { useQuery } from "@tanstack/react-query";
import { ExternalLink } from "lucide-react";
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
  meeting_provider: z.enum(["none", "google_meet", "existing"]),
  start_time: z.string().optional(),
  end_time: z.string().optional(),
  meeting_url: z.string().optional(),
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
      meeting_provider: "none",
      start_time: "",
      end_time: "",
      meeting_url: "",
    },
  });

  const showTypeSelector = !defaultProjectId;
  const meetingType = useWatch({ control: form.control, name: "meeting_type" });
  const meetingProvider = useWatch({
    control: form.control,
    name: "meeting_provider",
  });

  const onSubmit = async (values: FormValues) => {
    const tags = values.tags
      ? values.tags
          .split(",")
          .map((t) => t.trim())
          .filter(Boolean)
      : [];

    let provider: string;
    let meetingUrl: string | null = null;

    if (values.meeting_provider === "google_meet") {
      provider = "google_meet";
    } else if (values.meeting_provider === "existing") {
      provider = "manual";
      meetingUrl = values.meeting_url || null;
    } else {
      provider = "manual";
    }

    await createMeeting.mutateAsync({
      client_id: clientId,
      project_id:
        values.meeting_type === "project" ? values.project_id || null : null,
      title: values.title,
      meeting_type: values.meeting_type,
      tags: values.meeting_type === "project" ? [] : tags,
      meeting_date: values.meeting_date || null,
      meeting_provider: provider,
      meeting_url: meetingUrl,
      start_time: values.start_time ? new Date(values.start_time).toISOString() : null,
      end_time: values.end_time ? new Date(values.end_time).toISOString() : null,
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
      <DialogContent className="sm:max-w-2xl">
        <DialogHeader>
          <DialogTitle>Create Meeting</DialogTitle>
          <DialogDescription>
            Create a new meeting and optionally add a meeting link.
          </DialogDescription>
        </DialogHeader>

        <Form {...form}>
          <form
            onSubmit={form.handleSubmit(onSubmit)}
            className="grid grid-cols-2 gap-x-6 gap-y-3"
          >
            <div className="col-span-2">
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
            </div>

            {showTypeSelector && (
              <>
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

                {meetingType === "project" ? (
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
                ) : (
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
              </>
            )}

            {!showTypeSelector && meetingType === "project" && (
              <div className="col-span-2">
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
              </div>
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

            <FormField
              control={form.control}
              name="meeting_provider"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Meeting Provider</FormLabel>
                  <FormControl>
                    <div className="flex flex-wrap gap-2">
                      <button
                        type="button"
                        onClick={() => {
                          field.onChange("none");
                        }}
                        className={cn(
                          "flex-1 rounded-md border px-3 py-2 text-sm font-medium transition-colors",
                          field.value === "none"
                            ? "border-primary bg-primary/10 text-primary"
                            : "border-input hover:bg-accent hover:text-accent-foreground",
                        )}
                      >
                        No Meeting Link
                      </button>
                      <button
                        type="button"
                        onClick={() => {
                          field.onChange("google_meet");
                        }}
                        className={cn(
                          "flex-1 rounded-md border px-3 py-2 text-sm font-medium transition-colors",
                          field.value === "google_meet"
                            ? "border-primary bg-primary/10 text-primary"
                            : "border-input hover:bg-accent hover:text-accent-foreground",
                        )}
                      >
                        Google Meet
                      </button>
                      <button
                        type="button"
                        onClick={() => {
                          field.onChange("existing");
                        }}
                        className={cn(
                          "flex-1 rounded-md border px-3 py-2 text-sm font-medium transition-colors",
                          field.value === "existing"
                            ? "border-primary bg-primary/10 text-primary"
                            : "border-input hover:bg-accent hover:text-accent-foreground",
                        )}
                      >
                        Existing Meeting Link
                      </button>
                    </div>
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            {meetingProvider === "google_meet" && (
              <div className="col-span-2 rounded-md border p-3 space-y-3">
                <p className="text-sm font-medium text-foreground">
                  Google Meet Schedule
                </p>
                <div className="grid grid-cols-2 gap-3">
                  <FormField
                    control={form.control}
                    name="start_time"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Start Time</FormLabel>
                        <FormControl>
                          <Input type="datetime-local" {...field} />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                  <FormField
                    control={form.control}
                    name="end_time"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>End Time</FormLabel>
                        <FormControl>
                          <Input type="datetime-local" {...field} />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                </div>
              </div>
            )}

            {meetingProvider === "existing" && (
              <div className="col-span-2">
                <FormField
                  control={form.control}
                  name="meeting_url"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Meeting URL</FormLabel>
                      <FormControl>
                        <div className="relative">
                          <Input
                            placeholder="https://meet.google.com/xxx-xxxx-xxx"
                            className="pl-9"
                            {...field}
                          />
                          <ExternalLink className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
                        </div>
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
              </div>
            )}

            <div className="col-span-2">
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
            </div>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  );
}
