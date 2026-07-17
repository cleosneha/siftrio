"use client"

import { motion } from "framer-motion"

const CARDS = [
  { id: "meeting", label: "Meeting", delay: 0 },
  { id: "decision", label: "Decision", delay: 0.8 },
  { id: "action", label: "Action Item", delay: 1.6 },
  { id: "jira", label: "Jira", delay: 2.4 },
  { id: "assistant", label: "AI Assistant", delay: 3.2 },
] as const

const CONNECTIONS = [
  { from: "meeting", to: "decision" },
  { from: "decision", to: "action" },
  { from: "action", to: "jira" },
  { from: "jira", to: "assistant" },
] as const

const NODES: Record<string, { x: number; y: number; w: number; h: number }> = {
  meeting:   { x: 16,  y: 30,  w: 120, h: 64 },
  decision:  { x: 260, y: 90,  w: 120, h: 64 },
  action:    { x: 16,  y: 170, w: 140, h: 64 },
  jira:      { x: 220, y: 250, w: 100, h: 64 },
  assistant: { x: 100, y: 340, w: 140, h: 64 },
}

function getCenter(id: string) {
  const n = NODES[id]
  return { x: n.x + n.w / 2, y: n.y + n.h / 2 }
}

function buildPath(from: string, to: string) {
  const a = getCenter(from)
  const b = getCenter(to)
  const mx = (a.x + b.x) / 2
  return `M${a.x},${a.y} C${mx},${a.y} ${mx},${b.y} ${b.x},${b.y}`
}

const EASE = [0.25, 0.1, 0.25, 1] as const

export function HeroSection() {
  return (
    <section
      className="relative flex min-h-screen items-center overflow-hidden"
      style={{ background: "#08090A" }}
    >
      <div className="mx-auto flex w-full max-w-7xl flex-col items-center gap-16 px-6 py-24 md:flex-row md:items-center md:gap-20 md:px-12 lg:px-20">
        {/* ── LEFT ── */}
        <div className="flex-1 space-y-8 md:max-w-[55%]">
          <motion.p
            className="text-[11px] font-medium uppercase tracking-[0.2em]"
            style={{ color: "#4A4E54" }}
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.7, ease: EASE, delay: 0.1 }}
          >
            Siftrio
          </motion.p>

          <h1 className="text-4xl font-semibold leading-[1.15] tracking-tight sm:text-5xl lg:text-6xl">
            <motion.span
              className="block"
              style={{ color: "#FFFFFF" }}
              initial={{ opacity: 0, y: 16 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.7, ease: EASE, delay: 0.25 }}
            >
              Every project
            </motion.span>
            <motion.span
              className="block"
              style={{ color: "#FFFFFF" }}
              initial={{ opacity: 0, y: 16 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.7, ease: EASE, delay: 0.35 }}
            >
              has a memory.
            </motion.span>
            <motion.span
              className="block"
              style={{ color: "#6D737C" }}
              initial={{ opacity: 0, y: 16 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.7, ease: EASE, delay: 0.45 }}
            >
              Siftrio gives it one.
            </motion.span>
          </h1>

          <motion.p
            className="max-w-md text-[15px] leading-relaxed sm:text-base"
            style={{ color: "#6D737C" }}
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.7, ease: EASE, delay: 0.6 }}
          >
            Turn conversations into knowledge that both your team and AI can
            understand.
          </motion.p>
        </div>

        {/* ── RIGHT ── */}
        <div className="flex flex-1 items-center justify-center md:max-w-[45%]">
          <div className="relative" style={{ width: 420, height: 410 }}>
            {/* Connection lines */}
            <svg
              className="absolute inset-0"
              viewBox="0 0 420 410"
              fill="none"
              style={{ width: 420, height: 410 }}
            >
              {CONNECTIONS.map((c, i) => {
                const d = buildPath(c.from, c.to)
                const lineDelay = 4.0 + i * 0.8
                const dotDelay = 6.0 + i * 0.8
                return (
                  <g key={`${c.from}-${c.to}`}>
                    <path d={d} stroke="#1A1C1F" strokeWidth={1} fill="none" />
                    <motion.path
                      d={d}
                      stroke="#2A2E34"
                      strokeWidth={1}
                      fill="none"
                      initial={{ pathLength: 0 }}
                      animate={{ pathLength: 1 }}
                      transition={{ duration: 0.8, ease: "easeOut", delay: lineDelay }}
                    />
                    <motion.circle
                      r={2.5}
                      fill="#3A3E44"
                      style={{ offsetPath: `path('${d}')` }}
                      initial={{ offsetDistance: "0%", opacity: 0 }}
                      animate={{
                        offsetDistance: ["0%", "100%"],
                        opacity: [0, 0.8, 0.8, 0],
                      }}
                      transition={{
                        offsetDistance: { duration: 3.5, ease: "linear", repeat: Infinity, delay: dotDelay },
                        opacity: { duration: 3.5, times: [0, 0.08, 0.85, 1], repeat: Infinity, delay: dotDelay },
                      }}
                    />
                  </g>
                )
              })}
            </svg>

            {/* Cards */}
            {CARDS.map((card) => {
              const n = NODES[card.id]
              const floatY = card.delay % 2 === 0 ? -2 : 2
              const floatDuration = 5 + card.delay * 0.4
              return (
                <motion.div
                  key={card.id}
                  className="absolute"
                  style={{ left: n.x, top: n.y, width: n.w, height: n.h }}
                  initial={{ opacity: 0, y: 12 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.8, ease: EASE, delay: card.delay }}
                >
                  <motion.div
                    className="flex h-full w-full flex-col items-center justify-center gap-1.5"
                    style={{
                      background: "#111213",
                      border: "1px solid #1C1E22",
                      borderRadius: 8,
                      boxShadow:
                        "0 1px 0 rgba(255,255,255,0.015), 0 4px 16px rgba(0,0,0,0.3)",
                    }}
                    animate={{ y: [0, floatY, 0] }}
                    transition={{
                      duration: floatDuration,
                      ease: "easeInOut",
                      repeat: Infinity,
                      delay: card.delay + 1,
                    }}
                    whileHover={{ scale: 1.02, transition: { duration: 0.2 } }}
                  >
                    <span
                      className="text-[13px] font-medium tracking-wide"
                      style={{ color: "#BCC0C6" }}
                    >
                      {card.label}
                    </span>
                    <span
                      className="text-[10px]"
                      style={{ color: "#3A3E44" }}
                    >
                      ● ● ●
                    </span>
                  </motion.div>
                </motion.div>
              )
            })}
          </div>
        </div>
      </div>
    </section>
  )
}
