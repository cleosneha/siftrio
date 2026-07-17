"use client"

import Image from "next/image"

const EXAMPLE_QUESTIONS = [
  "Why did we choose OAuth?",
  "What changed after Sprint 18?",
  "Show pending action items.",
  "Summarize yesterday's meeting.",
]

export function AiAssistantSection() {
  return (
    <section
      className="relative flex items-center"
      style={{ background: "#08090A" }}
    >
      <div className="mx-auto flex w-full max-w-7xl flex-col items-center gap-16 px-6 py-32 md:flex-row md:items-center md:px-12 lg:px-20">
        {/* ── LEFT ── */}
        <div className="flex-1 space-y-8 md:max-w-[40%]">
          <div className="space-y-6">
            <p
              className="text-[11px] font-medium uppercase tracking-[0.2em]"
              style={{ color: "#4A4E54" }}
            >
              AI Assistant
            </p>

            <h2
              className="text-3xl font-semibold leading-[1.15] tracking-tight sm:text-4xl lg:text-5xl"
              style={{ color: "#FFFFFF" }}
            >
              Ask your project
              <br />
              anything.
            </h2>

            <p
              className="max-w-md text-[15px] leading-relaxed sm:text-base"
              style={{ color: "#6D737C" }}
            >
              Ask questions about meetings, decisions, action items,
              requirements, risks, project history, Jira, or documentation.
              Siftrio understands your entire workspace and answers with
              complete context.
            </p>
          </div>

          <div className="flex flex-wrap gap-2">
            {EXAMPLE_QUESTIONS.map((q) => (
              <span
                key={q}
                className="rounded-full px-4 py-2 text-[13px] transition-colors hover:bg-[#17191C]"
                style={{
                  color: "#6D737C",
                  border: "1px solid #1C1E22",
                }}
              >
                {q}
              </span>
            ))}
          </div>
        </div>

        {/* ── RIGHT ── */}
        <div className="flex flex-1 justify-center md:max-w-[60%]">
          <div
            className="relative w-full overflow-hidden"
            style={{ aspectRatio: "16 / 9", borderRadius: 10, border: "1px solid #1C1E22" }}
          >
            <Image
              src="/AI-assistant.png"
              alt="Siftrio AI Assistant preview"
              fill
              className="pointer-events-none object-cover"
              priority
              draggable={false}
            />
            <div
              className="pointer-events-none absolute inset-0"
              style={{
                background: "linear-gradient(to bottom, transparent 60%, #08090A)",
              }}
            />
          </div>
        </div>
      </div>
    </section>
  )
}
