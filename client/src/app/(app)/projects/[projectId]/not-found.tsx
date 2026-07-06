import Link from "next/link";

export default function ProjectNotFound() {
  return (
    <div className="flex flex-1 flex-col items-center justify-center gap-4 p-8 text-center">
      <h1 className="text-4xl font-bold">404</h1>
      <p className="text-lg text-muted-foreground">Project not found</p>
      <p className="text-sm text-muted-foreground">
        The project you are looking for does not exist or you may not have access to it.
      </p>
      <Link
        href="/dashboard"
        className="text-sm text-primary underline underline-offset-4 hover:text-primary/80"
      >
        Go to dashboard
      </Link>
    </div>
  );
}
