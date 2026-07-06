import Link from "next/link";

export default function RootNotFound() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center gap-4 p-8 text-center">
      <h1 className="text-4xl font-bold">404</h1>
      <p className="text-lg text-muted-foreground">Page not found</p>
      <Link
        href="/login"
        className="text-sm text-primary underline underline-offset-4 hover:text-primary/80"
      >
        Go to login
      </Link>
    </div>
  );
}
