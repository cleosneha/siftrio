"use client";

import { useRef } from "react";
import { motion, useInView } from "framer-motion";
import { ArrowDown, Check, MessageSquare, Shield } from "lucide-react";
import { FaGoogle, FaJira } from "react-icons/fa";
import { SiFirefoxbrowser } from "react-icons/si";

const EASE = [0.25, 0.1, 0.25, 1] as const;

const INTEGRATIONS = [
  {
    icon: FaGoogle,
    title: "Google Calendar",
    caption:
      "Schedule meetings and allow Siftrio to automatically add the Fireflies AI meeting assistant.",
  },
  {
    icon: SiFirefoxbrowser,
    title: "Fireflies AI",
    caption:
      "Joins meetings, records conversations, and generates searchable transcripts.",
  },

  {
    icon: FaJira,
    title: "Jira",
    caption: "Import issues, epics, sprint updates, and project tasks.",
  },
  {
    icon: null,
    title: "Documents",
    caption:
      "Upload PDFs, specifications, meeting notes, and technical documentation.",
  },
];

const KNOWLEDGE_ITEMS = [
  "Organizes project knowledge",
  "Links related information",
  "Builds searchable project memory",
  "Understands project context",
];

const SOURCES = [
  "GitHub PR #214",
  "Jira DEV-102",
  "Sprint Planning Meeting",
  "Authentication Design Document",
];

const cardStyle = {
  background: "var(--muted)",
  border: "1px solid var(--subtle-border)",
  borderRadius: 18,
  boxShadow: "0 1px 0 rgba(255,255,255,0.02), 0 8px 24px rgba(0,0,0,0.2)",
};

const fadeUp = {
  hidden: { opacity: 0, y: 20 },
  visible: (d: number) => ({
    opacity: 1,
    y: 0,
    transition: { duration: 0.8, ease: EASE, delay: d },
  }),
};

const cardHover = { y: -3, transition: { duration: 0.25, ease: EASE } };

function Connector() {
  const ref = useRef<HTMLDivElement>(null);
  const inView = useInView(ref, { once: true, margin: "-40px" });

  return (
    <div ref={ref} className="flex justify-center py-10 sm:py-12">
      <div className="relative flex flex-col items-center">
        <motion.div
          className="w-px bg-subtle-border origin-top"
          initial={{ scaleY: 0 }}
          animate={inView ? { scaleY: 1 } : { scaleY: 0 }}
          transition={{ duration: 0.6, ease: "easeOut" }}
          style={{ height: 56 }}
        />
        <motion.div
          initial={{ opacity: 0, y: -6 }}
          animate={inView ? { opacity: 1, y: 0 } : { opacity: 0, y: -6 }}
          transition={{ duration: 0.5, delay: 0.5, ease: "easeOut" }}
        >
          <ArrowDown className="h-5 w-5 text-subtle-text" strokeWidth={1.5} />
        </motion.div>
      </div>
    </div>
  );
}

function NetworkSvg() {
  const nodes = [
    { cx: 180, cy: 100 },
    { cx: 280, cy: 80 },
    { cx: 120, cy: 160 },
    { cx: 240, cy: 180 },
    { cx: 160, cy: 230 },
    { cx: 300, cy: 160 },
    { cx: 100, cy: 110 },
    { cx: 340, cy: 130 },
    { cx: 200, cy: 60 },
    { cx: 260, cy: 240 },
  ];

  return (
    <svg
      className="pointer-events-none absolute inset-0 h-full w-full"
      viewBox="0 0 400 300"
      fill="none"
      preserveAspectRatio="xMidYMid slice"
    >
      {nodes.map((n, i) =>
        nodes.slice(i + 1).map((m, j) => {
          const dist = Math.hypot(n.cx - m.cx, n.cy - m.cy);
          if (dist > 180) return null;
          return (
            <line
              key={`${i}-${j}`}
              x1={n.cx}
              y1={n.cy}
              x2={m.cx}
              y2={m.cy}
              stroke="var(--subtle-border)"
              strokeWidth={0.5}
              opacity={0.4}
            />
          );
        }),
      )}
      {nodes.map((n, i) => (
        <circle
          key={i}
          cx={n.cx}
          cy={n.cy}
          r={1.5}
          fill="var(--faint-text)"
          opacity={0.3}
        />
      ))}
    </svg>
  );
}

export function HowSiftrioWorks() {
  const sectionRef = useRef<HTMLDivElement>(null);
  const inView = useInView(sectionRef, { once: true, margin: "-100px" });

  return (
    <section className="relative bg-background">
      <div className="mx-auto max-w-7xl px-6 py-32 md:px-12 lg:px-20">
        {/* ── Header ── */}
        <motion.div
          className="mx-auto max-w-2xl space-y-6 text-center"
          initial="hidden"
          animate={inView ? "visible" : "hidden"}
          variants={fadeUp}
          custom={0}
        >
          <p className="text-[11px] font-medium uppercase tracking-[0.2em] text-subtle-text">
            How Siftrio Works
          </p>
          <h2 className="text-3xl font-semibold leading-[1.15] tracking-tight text-foreground sm:text-4xl lg:text-5xl">
            Connect the tools your team
            <br />
            already uses.
          </h2>
          <p className="mx-auto max-w-xl text-[15px] leading-relaxed sm:text-base text-disabled-text">
            Siftrio automatically organizes meetings, code, tasks, and documents
            into one searchable AI project memory.
          </p>
        </motion.div>

        {/* ── Workflow ── */}
        <div ref={sectionRef} className="mx-auto mt-20 max-w-3xl">
          {/* ── Step 1: Connect Your Workspace ── */}
          <motion.div
            initial="hidden"
            animate={inView ? "visible" : "hidden"}
            variants={fadeUp}
            custom={0.2}
          >
            <p className="mb-3 text-[11px] font-medium uppercase tracking-[0.2em] text-faint-text">
              Step 1
            </p>
            <h3 className="mb-3 text-xl font-semibold tracking-tight text-foreground sm:text-2xl">
              Connect Your Workspace
            </h3>
            <p className="mb-8 max-w-lg text-[14px] leading-relaxed text-disabled-text">
              Siftrio connects directly to the tools your team already uses.
              Each integration is optional and only accesses the data needed for
              its specific feature.
            </p>

            <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 sm:gap-4">
              {INTEGRATIONS.map((item, i) => (
                <motion.div
                  key={item.title}
                  className="flex items-start gap-4 p-5"
                  style={cardStyle}
                  variants={fadeUp}
                  initial="hidden"
                  animate={inView ? "visible" : "hidden"}
                  custom={0.3 + i * 0.08}
                  whileHover={cardHover}
                >
                  <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-background">
                    {item.icon ? (
                      <item.icon className="h-4 w-4 text-soft-text" />
                    ) : (
                      <svg
                        className="h-4 w-4 text-soft-text"
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                        strokeWidth={1.5}
                        strokeLinecap="round"
                        strokeLinejoin="round"
                      >
                        <path d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z" />
                        <path d="M14 2v4a2 2 0 0 0 2 2h4" />
                      </svg>
                    )}
                  </div>
                  <div className="min-w-0">
                    <p className="text-[13px] font-medium text-foreground">
                      {item.title}
                    </p>
                    <p className="mt-1 text-[12px] leading-relaxed text-disabled-text">
                      {item.caption}
                    </p>
                  </div>
                </motion.div>
              ))}
            </div>
          </motion.div>

          {/* ── Connector 1 ── */}
          <Connector />

          {/* ── Step 2: AI Engine ── */}
          <motion.div
            initial="hidden"
            animate={inView ? "visible" : "hidden"}
            variants={fadeUp}
            custom={0.5}
          >
            <p className="mb-3 text-[11px] font-medium uppercase tracking-[0.2em] text-faint-text">
              Step 2
            </p>
            <h3 className="mb-3 text-xl font-semibold tracking-tight text-foreground sm:text-2xl">
              Siftrio AI Project Memory
            </h3>
            <p className="mb-8 max-w-lg text-[14px] leading-relaxed text-disabled-text">
              Your connected data feeds into Siftrio&apos;s AI Engine, which
              automatically organizes, links, and indexes everything into a
              unified project memory.
            </p>

            <div
              className="relative mx-auto max-w-2xl overflow-hidden p-8 sm:p-10"
              style={cardStyle}
            >
              <NetworkSvg />

              <div
                className="pointer-events-none absolute inset-0"
                style={{
                  background:
                    "radial-gradient(ellipse at center, rgba(255,255,255,0.02) 0%, transparent 70%)",
                }}
              />

              <div className="relative z-10">
                <p className="text-[15px] font-semibold tracking-tight text-foreground">
                  Siftrio AI Engine
                </p>
                <p className="mt-2 max-w-md text-[13px] leading-relaxed text-disabled-text">
                  Processes everything you connect and builds a searchable,
                  contextual memory of your entire project.
                </p>
                <div className="mt-6 flex flex-wrap gap-2.5">
                  {KNOWLEDGE_ITEMS.map((item) => (
                    <span
                      key={item}
                      className="inline-flex items-center gap-1.5 rounded-full border border-subtle-border bg-background px-3 py-1.5 text-[12px] text-soft-text"
                    >
                      <Check
                        className="h-3 w-3 text-entity-project"
                        strokeWidth={2.5}
                      />
                      {item}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          </motion.div>

          {/* ── Connector 2 ── */}
          <Connector />

          {/* ── Step 3: Ask AI ── */}
          <motion.div
            initial="hidden"
            animate={inView ? "visible" : "hidden"}
            variants={fadeUp}
            custom={0.7}
          >
            <p className="mb-3 text-[11px] font-medium uppercase tracking-[0.2em] text-faint-text">
              Step 3
            </p>
            <h3 className="mb-3 text-xl font-semibold tracking-tight text-foreground sm:text-2xl">
              Ask AI
            </h3>
            <p className="mb-8 max-w-lg text-[14px] leading-relaxed text-disabled-text">
              Ask questions about your project in natural language. Siftrio
              understands your meetings, code, tasks, and documentation — and
              answers with source-backed context.
            </p>

            <div className="mx-auto max-w-2xl p-6 sm:p-8" style={cardStyle}>
              <div className="space-y-5">
                {/* User message */}
                <div className="flex justify-end">
                  <div className="max-w-[85%] rounded-2xl rounded-br-md bg-background border border-subtle-border px-4 py-2.5 text-[13px] text-foreground">
                    Why was the authentication system changed?
                  </div>
                </div>

                {/* Assistant message */}
                <div className="flex gap-3">
                  <div className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-accent">
                    <MessageSquare className="h-3.5 w-3.5 text-soft-text" />
                  </div>
                  <div className="min-w-0 flex-1 space-y-3">
                    <p className="text-[13px] leading-relaxed text-disabled-text">
                      The authentication flow was updated after discussion
                      during Sprint Planning.
                    </p>

                    <div className="space-y-1.5">
                      <p className="text-[11px] font-medium uppercase tracking-wider text-faint-text">
                        Relevant sources
                      </p>
                      <div className="flex flex-wrap gap-1.5">
                        {SOURCES.map((src) => (
                          <span
                            key={src}
                            className="inline-flex items-center gap-1 rounded-full border border-subtle-border bg-background px-2.5 py-1 text-[11px] text-soft-text transition-colors hover:bg-accent cursor-pointer"
                          >
                            <Check
                              className="h-2.5 w-2.5 text-entity-project"
                              strokeWidth={2.5}
                            />
                            {src}
                          </span>
                        ))}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </motion.div>
        </div>

        {/* ── Privacy Notice ── */}
        <motion.div
          className="mx-auto mt-20 max-w-2xl"
          initial="hidden"
          animate={inView ? "visible" : "hidden"}
          variants={fadeUp}
          custom={0.9}
        >
          <div
            className="flex items-start gap-4 p-5 sm:p-6"
            style={{
              ...cardStyle,
              borderRadius: 14,
            }}
          >
            <div className="mt-0.5 flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-background">
              <Shield className="h-4 w-4 text-soft-text" strokeWidth={1.5} />
            </div>
            <p className="text-[13px] leading-relaxed text-disabled-text">
              <span className="font-medium text-soft-text">
                Your connected data stays under your control.
              </span>{" "}
              Siftrio only accesses the services you explicitly connect to
              organize project knowledge and answer your questions with
              source-backed context. Data is never accessed beyond the
              permissions you grant.
            </p>
          </div>
        </motion.div>
      </div>
    </section>
  );
}
