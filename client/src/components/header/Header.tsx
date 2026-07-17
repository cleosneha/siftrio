"use client"

import Link from "next/link"
import { Button } from "@/components/ui/button"
import { useAuth } from "@/features/auth/AuthProvider"

export function Header() {
  const { user, loading } = useAuth()

  const handleGetStarted = () => {
    const backendUrl =
      process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000/api"
    window.location.href = `${backendUrl}/auth/google/login`
  }

  return (
    <header className="sticky top-0 z-50 w-full border-b border-border bg-background/80 backdrop-blur-md">
      <div className="mx-auto flex h-14 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
        <Link href="/" className="text-lg font-semibold text-foreground">
          Siftrio
        </Link>
        {!loading && (
          <>
            {user ? (
              <Button render={<Link href="/dashboard" />} nativeButton={false} size="sm">
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
  )
}
