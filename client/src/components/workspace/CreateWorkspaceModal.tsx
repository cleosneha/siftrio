"use client";

import { useRouter } from "next/navigation";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
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
import { useCreateWorkspace } from "@/hooks/useWorkspaces";

const formSchema = z.object({
  name: z.string().min(1, "Name is required").max(255),
  description: z.string().max(1000).optional(),
});

type FormValues = z.infer<typeof formSchema>;

interface CreateWorkspaceModalProps {
  open: boolean;
  onClose: () => void;
}

export function CreateWorkspaceModal({ open, onClose }: CreateWorkspaceModalProps) {
  const router = useRouter();
  const createWorkspace = useCreateWorkspace();

  const form = useForm<FormValues>({
    resolver: zodResolver(formSchema),
    defaultValues: { name: "", description: "" },
  });

  const onSubmit = async (values: FormValues) => {
    const result = await createWorkspace.mutateAsync({
      name: values.name,
      description: values.description || null,
    });
    form.reset();
    onClose();
    if (result.data?.id) {
      router.push(`/workspaces/${result.data.id}`);
    }
  };

  return (
    <Dialog open={open} onOpenChange={(o) => { if (!o) { form.reset(); onClose(); } }}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Create Workspace</DialogTitle>
          <DialogDescription>
            Create a new workspace to organize your clients and projects.
          </DialogDescription>
        </DialogHeader>

        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
            <FormField
              control={form.control}
              name="name"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Name</FormLabel>
                  <FormControl>
                    <Input placeholder="My Workspace" autoFocus {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="description"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Description</FormLabel>
                  <FormControl>
                    <Textarea
                      placeholder="Optional description"
                      rows={3}
                      {...field}
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <DialogFooter>
              <Button type="button" variant="outline" onClick={() => { form.reset(); onClose(); }}>
                Cancel
              </Button>
              <Button type="submit" disabled={createWorkspace.isPending}>
                {createWorkspace.isPending ? "Creating..." : "Create"}
              </Button>
            </DialogFooter>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  );
}
