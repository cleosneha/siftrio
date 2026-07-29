"use client";

interface BouncingDotsProps {
  className?: string;
}

export function BouncingDots({ className = "" }: BouncingDotsProps) {
  return (
    <span className={`inline-flex gap-0.5 ${className}`}>
      <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-muted-foreground" style={{ animationDelay: "0ms" }} />
      <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-muted-foreground" style={{ animationDelay: "150ms" }} />
      <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-muted-foreground" style={{ animationDelay: "300ms" }} />
    </span>
  );
}
