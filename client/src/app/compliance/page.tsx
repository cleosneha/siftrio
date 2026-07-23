"use client";

import { useEffect, useRef, useState } from "react";
import Link from "next/link";
import { motion } from "framer-motion";

const EASE = [0.25, 0.1, 0.25, 1] as const;

const SECTIONS = [
  { id: "limited-use-statement", label: "Limited Use Compliance Statement" },
  { id: "ai-integrations", label: "AI/ML Third-Party Integrations" },
  { id: "data-isolation", label: "Data Isolation" },
  { id: "google-data-usage", label: "Google Data Usage" },
  { id: "contact", label: "Contact" },
];

export default function Compliance() {
  const [activeId, setActiveId] = useState(SECTIONS[0].id);
  const observerRef = useRef<IntersectionObserver | null>(null);

  useEffect(() => {
    const headings = SECTIONS.map((s) => document.getElementById(s.id)).filter(
      Boolean,
    );

    observerRef.current = new IntersectionObserver(
      (entries) => {
        for (const entry of entries) {
          if (entry.isIntersecting) {
            setActiveId(entry.target.id);
          }
        }
      },
      { rootMargin: "-20% 0px -60% 0px" },
    );

    headings.forEach((el) => {
      if (el) observerRef.current?.observe(el);
    });

    return () => observerRef.current?.disconnect();
  }, []);

  const scrollTo = (id: string) => {
    const el = document.getElementById(id);
    if (el) {
      el.scrollIntoView({ behavior: "smooth", block: "start" });
    }
  };

  return (
    <div className="min-h-screen bg-background">
      {/* ── Nav ── */}
      <nav className="sticky top-0 z-50 border-b border-border bg-background/80 backdrop-blur-md">
        <div className="mx-auto flex h-14 max-w-[820px] items-center justify-between px-6">
          <Link
            href="/"
            className="text-sm text-disabled-text transition-colors hover:text-foreground"
          >
            &larr; Back to Home
          </Link>
          <span className="text-lg font-semibold text-foreground">Siftrio</span>
          <span className="w-[120px]" />
        </div>
      </nav>

      {/* ── Content ── */}
      <div className="mx-auto max-w-[820px] px-6">
        {/* ── Hero ── */}
        <motion.div
          className="pt-24 pb-20"
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, ease: EASE }}
        >
          <h1 className="text-[40px] font-semibold leading-tight tracking-tight text-foreground">
            Data Safety &amp; Compliance
          </h1>

          <div className="mt-6 flex gap-10 text-[13px] text-disabled-text">
            <div>
              <span className="block text-subtle-text">Effective Date</span>
              July 23, 2026
            </div>
            <div>
              <span className="block text-subtle-text">Last Updated</span>
              July 23, 2026
            </div>
          </div>

          <p className="mt-10 max-w-[640px] text-[17px] leading-[1.8] text-disabled-text">
            This page describes how Siftrio handles user data received from
            Google Workspace APIs, including our AI/ML integrations and
            compliance with Google&apos;s Limited Use requirements.
          </p>
        </motion.div>

        {/* ── Table of Contents ── */}
        <motion.div
          className="border-t border-border pb-20 pt-10"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.5, ease: EASE, delay: 0.15 }}
        >
          <p className="mb-6 text-[11px] font-medium uppercase tracking-[0.2em] text-subtle-text">
            Contents
          </p>
          <nav className="flex flex-col gap-1">
            {SECTIONS.map((s, i) => (
              <button
                key={s.id}
                onClick={() => scrollTo(s.id)}
                className={`flex items-center gap-3 rounded-md px-3 py-2 text-left text-[14px] transition-colors ${
                  activeId === s.id
                    ? "bg-accent text-foreground"
                    : "text-disabled-text hover:text-soft-text"
                }`}
              >
                <span className="w-5 text-right text-[12px] text-faint-text">
                  {String(i + 1).padStart(2, "0")}
                </span>
                {s.label}
              </button>
            ))}
          </nav>
        </motion.div>

        {/* ── Document ── */}
        <div className="border-t border-border pt-20">
          {/* 01 Limited Use Compliance Statement */}
          <Section
            id="limited-use-statement"
            number="01"
            title="Limited Use Compliance Statement"
          >
            <div className="rounded-lg border border-border bg-accent/50 p-6">
              <p className="text-[17px] leading-[1.8] text-foreground">
                The use of raw or derived user data received from Google
                Workspace APIs will adhere to the{" "}
                <a
                  href="https://developers.google.com/terms/api-services-user-data-policy"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="underline underline-offset-4 transition-colors hover:text-soft-text"
                >
                  Google User Data Policy
                </a>
                , including the{" "}
                <a
                  href="https://developers.google.com/workspace/guides/create-credentials#limited-use"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="underline underline-offset-4 transition-colors hover:text-soft-text"
                >
                  Limited Use requirements
                </a>
                .
              </p>
            </div>
            <p>
              Siftrio&apos;s use and transfer of information received from Google
              APIs adheres to the Google API Services User Data Policy,
              including the Limited Use requirements. Google user data is
              accessed and processed only to provide or improve user-facing
              features that you explicitly request.
            </p>
          </Section>

          {/* 02 AI/ML Third-Party Integrations */}
          <Section
            id="ai-integrations"
            number="02"
            title="AI/ML Third-Party Integrations"
          >
            <p>
              Siftrio integrates with the following third-party AI/ML and
              transcription service providers:
            </p>

            {/* Mistral AI */}
            <div className="mt-6 rounded-lg border border-border p-6">
              <p className="text-[17px] font-medium text-foreground">
                Mistral AI
              </p>
              <div className="mt-4 space-y-2 text-[15px] leading-[1.7] text-disabled-text">
                <div className="flex gap-4">
                  <span className="w-32 shrink-0 text-subtle-text">
                    Provider
                  </span>
                  <span>Mistral AI (api.mistral.ai)</span>
                </div>
                <div className="flex gap-4">
                  <span className="w-32 shrink-0 text-subtle-text">Plan</span>
                  <span>Free Experiment tier</span>
                </div>
                <div className="flex gap-4">
                  <span className="w-32 shrink-0 text-subtle-text">
                    Purpose
                  </span>
                  <span>
                    LLM inference (meeting transcript analysis, RAG chat
                    responses) and embedding generation (vector search)
                  </span>
                </div>
                <div className="flex gap-4">
                  <span className="w-32 shrink-0 text-subtle-text">
                    Training
                  </span>
                  <span>
                    Opted out — training on API inputs and outputs is disabled
                    via the Admin Console Privacy settings. Mistral AI&apos;s
                    paid API tiers are excluded from model training by default;
                    the free tier opt-out provides equivalent protection.
                  </span>
                </div>
                <div className="flex gap-4">
                  <span className="w-32 shrink-0 text-subtle-text">
                    Privacy Policy
                  </span>
                  <a
                    href="https://legal.mistral.ai/terms/privacy-policy"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-foreground underline underline-offset-4 transition-colors hover:text-soft-text"
                  >
                    legal.mistral.ai/terms/privacy-policy
                  </a>
                </div>
              </div>
            </div>

            {/* Fireflies.ai */}
            <div className="mt-4 rounded-lg border border-border p-6">
              <p className="text-[17px] font-medium text-foreground">
                Fireflies.ai
              </p>
              <div className="mt-4 space-y-2 text-[15px] leading-[1.7] text-disabled-text">
                <div className="flex gap-4">
                  <span className="w-32 shrink-0 text-subtle-text">
                    Provider
                  </span>
                  <span>Fireflies.ai (fireflies.ai)</span>
                </div>
                <div className="flex gap-4">
                  <span className="w-32 shrink-0 text-subtle-text">Plan</span>
                  <span>Business tier</span>
                </div>
                <div className="flex gap-4">
                  <span className="w-32 shrink-0 text-subtle-text">
                    Purpose
                  </span>
                  <span>
                    Automated meeting transcription — retrieves meeting
                    transcripts and metadata from Fireflies.ai to populate
                    Siftrio project records
                  </span>
                </div>
                <div className="flex gap-4">
                  <span className="w-32 shrink-0 text-subtle-text">
                    Data Flow
                  </span>
                  <span>
                    Siftrio pulls transcript data from Fireflies.ai via API
                    and webhook. No Google user data is shared with Fireflies.ai
                    through Siftrio.
                  </span>
                </div>
                <div className="flex gap-4">
                  <span className="w-32 shrink-0 text-subtle-text">
                    Privacy Policy
                  </span>
                  <a
                    href="https://fireflies.ai/privacy"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-foreground underline underline-offset-4 transition-colors hover:text-soft-text"
                  >
                    fireflies.ai/privacy
                  </a>
                </div>
              </div>
            </div>

            <p className="mt-6">
              No other AI/ML model providers, services, or third-party AI
              integrations are used. Siftrio does not integrate with OpenAI,
              Anthropic, Google Gemini, or any other AI/ML service.
            </p>
          </Section>

          {/* 03 Data Isolation */}
          <Section id="data-isolation" number="03" title="Data Isolation">
            <p>
              Siftrio maintains strict separation between Google Workspace API
              data and third-party AI/ML services:
            </p>
            <p className="font-medium text-soft-text">
              Data Sent to Mistral AI
            </p>
            <ul>
              <li>
                Meeting transcript text — provided by the user via manual upload
                or received through Fireflies.ai webhooks
              </li>
              <li>
                User queries sent to the RAG chat assistant
              </li>
            </ul>
            <p className="font-medium text-soft-text">
              Data NEVER Sent to Mistral AI or Any AI Service
            </p>
            <ul>
              <li>
                Google OAuth profile data (name, email, profile picture)
              </li>
              <li>
                Google Calendar data (event IDs, Google Meet URLs, attendee
                information)
              </li>
              <li>
                Google account credentials or tokens
              </li>
              <li>
                Any other Google Workspace API user data
              </li>
            </ul>
            <p>
              Meeting transcript text processed by Mistral AI is used solely
              for generating structured analyses (summaries, action items,
              decisions, risks) and embeddings for semantic search within the
              user&apos;s Siftrio workspace. This data is not combined with
              Google OAuth or Calendar data when sent to Mistral AI.
            </p>
          </Section>

          {/* 04 Google Data Usage */}
          <Section id="google-data-usage" number="04" title="Google Data Usage">
            <p className="font-medium text-soft-text">
              Google OAuth Scopes
            </p>
            <p>
              Siftrio requests the following Google OAuth scopes:{" "}
              <code>openid</code>, <code>email</code>, <code>profile</code>,
              and <code>calendar.events</code>.
            </p>
            <p className="font-medium text-soft-text">
              How Google Data Is Used
            </p>
            <ul>
              <li>
                Google account information (name, email, profile picture) is
                used solely for authentication and account identification
              </li>
              <li>
                Google Calendar data is used only to read, create, and
                synchronize calendar events and generate Google Meet conference
                links
              </li>
              <li>
                Google Workspace APIs are not used for advertising, marketing,
                profiling, or any purpose beyond providing the features
                explicitly requested by the user
              </li>
            </ul>
            <p className="font-medium text-soft-text">
              Google Data Is Not Used For
            </p>
            <ul>
              <li>Advertising or marketing purposes</li>
              <li>
                Training, fine-tuning, or improving generalized AI or machine
                learning models
              </li>
              <li>Profiling or building advertising profiles</li>
              <li>
                Sale or transfer to third parties (except strictly necessary
                service providers bound by data protection obligations)
              </li>
            </ul>
          </Section>

          {/* 05 Contact */}
          <Section id="contact" number="05" title="Contact">
            <p>
              If you have questions about this compliance page or our data
              practices, please contact us:
            </p>
            <div className="mt-6 space-y-3">
              <div>
                <span className="text-[13px] text-subtle-text">Email</span>
                <p className="text-foreground">appsbysneha@gmail.com</p>
              </div>
              <div>
                <span className="text-[13px] text-subtle-text">Website</span>
                <p className="text-foreground">siftrio.tech</p>
              </div>
            </div>
          </Section>
        </div>

        {/* ── Footer ── */}
        <footer className="border-t border-border py-10">
          <div className="flex flex-col items-center gap-4 text-[13px] text-disabled-text">
            <div className="flex items-center gap-4">
              <Link
                href="/privacy"
                className="transition-colors hover:text-soft-text"
              >
                Privacy Policy
              </Link>
              <span>·</span>
              <Link
                href="/terms"
                className="transition-colors hover:text-soft-text"
              >
                Terms &amp; Conditions
              </Link>
              <span>·</span>
              <Link
                href="/compliance"
                className="transition-colors hover:text-soft-text"
              >
                Compliance
              </Link>
            </div>
            <p className="text-faint-text">&copy; 2026 Siftrio</p>
          </div>
        </footer>
      </div>
    </div>
  );
}

function Section({
  id,
  number,
  title,
  children,
}: {
  id: string;
  number: string;
  title: string;
  children: React.ReactNode;
}) {
  return (
    <section id={id} className="scroll-mt-24 pb-20">
      <div className="mb-6">
        <span className="block text-[13px] font-medium text-faint-text">
          {number}
        </span>
        <h2 className="mt-1 text-[30px] font-semibold leading-tight tracking-tight text-foreground">
          {title}
        </h2>
      </div>
      <div className="space-y-6 text-[17px] leading-[1.8] text-disabled-text [&_li]:pl-1 [&_li]:marker:text-faint-text [&_ul]:list-disc [&_ul]:space-y-2 [&_ul]:pl-5">
        {children}
      </div>
    </section>
  );
}
