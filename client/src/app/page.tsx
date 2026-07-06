"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";

export default function Home() {
  const router = useRouter();

  useEffect(() => {
    if (typeof window === "undefined") return;
    const pendingToken = sessionStorage.getItem("pendingAcceptToken");
    if (pendingToken) {
      sessionStorage.removeItem("pendingAcceptToken");
      router.replace(`/invitations/accept?token=${pendingToken}`);
    } else {
      router.replace("/dashboard");
    }
  }, [router]);

  return null;
}
