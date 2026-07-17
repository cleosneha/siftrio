"use client";

import Link from "next/link";
import Image from "next/image";
import { Button } from "@/components/ui/button";
import { useAuth } from "@/features/auth/AuthProvider";

export function Header() {
  const { user, loading } = useAuth();

  const handleGetStarted = () => {
    const backendUrl =
      process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000/api";
    window.location.href = `${backendUrl}/auth/google/login`;
  };

  return (
    <header className="sticky top-0 z-50 w-full border-b border-border bg-background/80 backdrop-blur-md">
      <div className="mx-auto flex h-14 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
        <Link href="/" className="flex items-center gap-2">
          <Image
            src="/logo.png"
            alt="Siftrio"
            width={40}
            height={40}
            loading="eager"
          />
          <span className="text-lg font-semibold text-foreground">Siftrio</span>
        </Link>
        {!loading && (
          <>
            {user ? (
              <Button
                render={<Link href="/dashboard" />}
                nativeButton={false}
                size="sm"
              >
                Open App
              </Button>
            ) : (
              <Button size="sm" onClick={handleGetStarted}>
                Get Started
              </Button>
            )}
          </>
        )}
      </div>
    </header>
  );
}
