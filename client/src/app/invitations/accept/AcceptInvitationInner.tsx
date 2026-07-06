"use client";

import { useEffect, useState } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import { CheckCircle, XCircle, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useAuth } from "@/features/auth/AuthProvider";
import { invitationService } from "@/features/invitations/services/invitation.service";

type AcceptState =
  | { status: "idle" }
  | { status: "loading" }
  | { status: "success"; message: string }
  | { status: "error"; message: string };

export function AcceptInvitationInner() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const token = searchParams.get("token");
  const { user, loading: authLoading } = useAuth();
  const [state, setState] = useState<AcceptState>({ status: "idle" });

  useEffect(() => {
    if (authLoading) return;
    if (!token) {
      setState({ status: "error", message: "Invalid invitation link. No token provided." });
      return;
    }
    if (!user) {
      sessionStorage.setItem("pendingAcceptToken", token);
      setState({ status: "idle" });
      return;
    }

    const actualToken = token || sessionStorage.getItem("pendingAcceptToken");
    if (!actualToken) {
      setState({ status: "error", message: "No invitation token found." });
      return;
    }

    setState({ status: "loading" });

    invitationService
      .accept(actualToken)
      .then((res) => {
        sessionStorage.removeItem("pendingAcceptToken");
        setState({ status: "success", message: res.message || "You have successfully joined!" });
      })
      .catch((err) => {
        const msg = err?.response?.data?.message || "Failed to accept invitation.";
        setState({ status: "error", message: msg });
      });
  }, [authLoading, user, token]);

  const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000/api";

  if (authLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
      </div>
    );
  }

  return (
    <div className="flex min-h-screen flex-col items-center justify-center gap-6 p-8 text-center">
      {!user && token ? (
        <>
          <h1 className="text-2xl font-semibold">You're Invited!</h1>
          <p className="text-muted-foreground">
            Log in to accept this invitation.
          </p>
          <Button
            onClick={() => {
              window.location.href = `${backendUrl}/auth/google/login`;
            }}
          >
            Continue with Google
          </Button>
        </>
      ) : state.status === "loading" ? (
        <>
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
          <p className="text-muted-foreground">Accepting invitation...</p>
        </>
      ) : state.status === "success" ? (
        <>
          <CheckCircle className="h-12 w-12 text-green-500" />
          <h1 className="text-2xl font-semibold">Invitation Accepted!</h1>
          <p className="text-muted-foreground">{state.message}</p>
          <Button onClick={() => router.push("/dashboard")}>
            Go to Dashboard
          </Button>
        </>
      ) : state.status === "error" ? (
        <>
          <XCircle className="h-12 w-12 text-destructive" />
          <h1 className="text-2xl font-semibold">Unable to Accept</h1>
          <p className="text-muted-foreground">{state.message}</p>
          <Button onClick={() => router.push("/dashboard")}>
            Go to Dashboard
          </Button>
        </>
      ) : null}
    </div>
  );
}
