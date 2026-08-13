"use client";

import Link from "next/link";
import Image from "next/image";
import { usePathname } from "next/navigation";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Button } from "@/components/ui/button";
import { useAuth } from "@/features/auth/AuthProvider";

export function Header() {
  const { user } = useAuth();
  const pathname = usePathname();
  const isLanding = pathname === "/";
  console.log(user);

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
        {user ? (
          isLanding ? (
            <Button
              render={<Link href="/dashboard" />}
              nativeButton={false}
              size="sm"
            >
              Open App
            </Button>
          ) : (
            <Link href="/dashboard">
              <Avatar>
                {user.profile_picture ? (
                  <AvatarImage
                    src={user.profile_picture}
                    alt={user.full_name ?? user.email}
                    referrerPolicy="no-referrer"
                  />
                ) : (
                  <AvatarFallback>
                    {(user.full_name ?? user.email).slice(0, 2).toUpperCase()}
                  </AvatarFallback>
                )}
              </Avatar>
            </Link>
          )
        ) : (
          <Button size="sm" onClick={handleGetStarted}>
            Get Started
          </Button>
        )}
      </div>
    </header>
  );
}
