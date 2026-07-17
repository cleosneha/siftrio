"use client"

import { useRef } from "react"
import { motion, useInView } from "framer-motion"

const TOOLS = [
  { id: "claude", label: "Claude Desktop", x: 30, y: 10, w: 140, h: 56 },
  { id: "cursor", label: "Cursor", x: 200, y: 0, w: 110, h: 56 },
  { id: "vscode", label: "VS Code", x: 340, y: 0, w: 110, h: 56 },
  { id: "windsurf", label: "Windsurf", x: 480, y: 0, w: 120, h: 56 },
  { id: "agent", label: "Custom Agent", x: 620, y: 10, w: 130, h: 56 },
] as const

const RESOURCES = [
  { id: "meetings", label: "Meetings", x: 0, y: 310, w: 110, h: 52 },
  { id: "knowledge", label: "Knowledge", x: 118, y: 310, w: 118, h: 52 },
  { id: "projects", label: "Projects", x: 244, y: 310, w: 106, h: 52 },
  { id: "actions", label: "Action Items", x: 358, y: 310, w: 126, h: 52 },
  { id: "jira", label: "Jira", x: 492, y: 310, w: 86, h: 52 },
  { id: "calendar", label: "Google Calendar", x: 586, y: 310, w: 148, h: 52 },
  { id: "documents", label: "Documents", x: 130, y: 376, w: 118, h: 52 },
  { id: "requirements", label: "Requirements", x: 400, y: 376, w: 136, h: 52 },
] as const

const HUB = { x: 290, y: 168, w: 120, h: 120 }

function c(id: string) {
  const n = [...TOOLS, ...RESOURCES].find((n) => n.id === id)!
  return { x: n.x + n.w / 2, y: n.y + n.h / 2 }
}

function hubCenter() {
  return { x: HUB.x + HUB.w / 2, y: HUB.y + HUB.h / 2 }
}

function curve(a: { x: number; y: number }, b: { x: number; y: number }) {
  const mx = (a.x + b.x) / 2
  return `M${a.x},${a.y} C${mx},${a.y} ${mx},${b.y} ${b.x},${b.y}`
}

const EASE = [0.25, 0.1, 0.25, 1] as const
const W = 780
const H = 450

const cardEntrance = {
  hidden: { opacity: 0, y: 10 },
  visible: (d: number) => ({
    opacity: 1,
    y: 0,
    transition: { duration: 0.9, ease: EASE, delay: d },
  }),
}

export function McpSection() {
  const ref = useRef<HTMLDivElement>(null)
  const inView = useInView(ref, { once: true, margin: "-80px" })
  const hc = hubCenter()

  return (
    <section className="relative bg-background">
      <div className="mx-auto flex w-full max-w-7xl flex-col items-center gap-16 px-6 py-32 md:flex-row md:items-center md:px-12 lg:px-20">
        {/* ── LEFT ── */}
        <div className="flex-1 space-y-8 md:max-w-[40%]">
          <div className="space-y-6">
            <p
              className="text-[11px] font-medium uppercase tracking-[0.2em] text-subtle-text"
            >
              MCP Server
            </p>

            <h2
              className="text-3xl font-semibold leading-[1.15] tracking-tight text-foreground sm:text-4xl lg:text-5xl"
            >
              Connect your favorite
              <br />
              AI tools.
            </h2>

            <p
              className="max-w-md text-[15px] leading-relaxed sm:text-base text-disabled-text"
            >
              Use Claude Desktop, Cursor, VS Code, Windsurf, or your own AI
              agents with secure access to your Siftrio workspace through the
              Model Context Protocol.
            </p>
          </div>

          <p
            className="text-sm font-medium tracking-wide text-faint-text"
          >
            One protocol. Every project. Unlimited context.
          </p>
        </div>

        {/* ── RIGHT ── */}
        <div
          ref={ref}
          className="flex flex-1 justify-center md:max-w-[60%]"
        >
          <div className="relative" style={{ width: W, height: H }}>
            <svg
              className="absolute inset-0"
              viewBox={`0 0 ${W} ${H}`}
              fill="none"
              style={{ width: W, height: H }}
            >
              {/* Background lines */}
              {TOOLS.map((t) => (
                <path
                  key={`bg-t-${t.id}`}
                  d={curve(c(t.id), hc)}
                  style={{ stroke: "var(--svg-bg-track)" }}
                  strokeWidth={1}
                  fill="none"
                />
              ))}
              {RESOURCES.map((r) => (
                <path
                  key={`bg-r-${r.id}`}
                  d={curve(hc, c(r.id))}
                  style={{ stroke: "var(--svg-bg-track)" }}
                  strokeWidth={1}
                  fill="none"
                />
              ))}

              {/* Animated lines — tools → hub */}
              {inView &&
                TOOLS.map((t, i) => (
                  <motion.path
                    key={`line-t-${t.id}`}
                    d={curve(c(t.id), hc)}
                    style={{ stroke: "var(--svg-line)" }}
                    strokeWidth={1}
                    fill="none"
                    initial={{ pathLength: 0 }}
                    animate={{ pathLength: 1 }}
                    transition={{
                      duration: 0.6,
                      ease: "easeOut",
                      delay: 0.5 + i * 0.15,
                    }}
                  />
                ))}

              {/* Animated lines — hub → resources */}
              {inView &&
                RESOURCES.map((r, i) => (
                  <motion.path
                    key={`line-r-${r.id}`}
                    d={curve(hc, c(r.id))}
                    style={{ stroke: "var(--svg-line)" }}
                    strokeWidth={1}
                    fill="none"
                    initial={{ pathLength: 0 }}
                    animate={{ pathLength: 1 }}
                    transition={{
                      duration: 0.6,
                      ease: "easeOut",
                      delay: 2.5 + i * 0.12,
                    }}
                  />
                ))}

              {/* Traveling dots — tools → hub */}
              {inView &&
                TOOLS.map((t, i) => {
                  const d = curve(c(t.id), hc)
                  const delay = 1.5 + i * 0.15
                  return (
                    <motion.circle
                      key={`dot-t-${t.id}`}
                      r={2}
                      style={{ fill: "var(--subtle-text)", offsetPath: `path('${d}')` }}
                      initial={{ offsetDistance: "0%", opacity: 0 }}
                      animate={{
                        offsetDistance: ["0%", "100%"],
                        opacity: [0, 0.7, 0.7, 0],
                      }}
                      transition={{
                        offsetDistance: {
                          duration: 2.5,
                          ease: "linear",
                          repeat: Infinity,
                          delay,
                        },
                        opacity: {
                          duration: 2.5,
                          times: [0, 0.1, 0.85, 1],
                          repeat: Infinity,
                          delay,
                        },
                      }}
                    />
                  )
                })}

              {/* Traveling dots — hub → resources */}
              {inView &&
                RESOURCES.map((r, i) => {
                  const d = curve(hc, c(r.id))
                  const delay = 3.5 + i * 0.12
                  return (
                    <motion.circle
                      key={`dot-r-${r.id}`}
                      r={2}
                      style={{ fill: "var(--subtle-text)", offsetPath: `path('${d}')` }}
                      initial={{ offsetDistance: "0%", opacity: 0 }}
                      animate={{
                        offsetDistance: ["0%", "100%"],
                        opacity: [0, 0.7, 0.7, 0],
                      }}
                      transition={{
                        offsetDistance: {
                          duration: 2.5,
                          ease: "linear",
                          repeat: Infinity,
                          delay,
                        },
                        opacity: {
                          duration: 2.5,
                          times: [0, 0.1, 0.85, 1],
                          repeat: Infinity,
                          delay,
                        },
                      }}
                    />
                  )
                })}
            </svg>

            {/* Hub */}
            <motion.div
              className="absolute flex items-center justify-center"
              style={{
                left: HUB.x,
                top: HUB.y,
                width: HUB.w,
                height: HUB.h,
                borderRadius: "50%",
                background: "var(--muted)",
                border: "1px solid var(--subtle-border)",
                boxShadow:
                  "0 1px 0 rgba(255,255,255,0.015), 0 4px 20px rgba(0,0,0,0.3)",
              }}
              initial={{ opacity: 0, scale: 0.9 }}
              animate={
                inView
                  ? {
                      opacity: 1,
                      scale: [1, 1.03, 1],
                    }
                  : { opacity: 0, scale: 0.9 }
              }
              transition={{
                opacity: { duration: 0.9, ease: EASE, delay: 0.3 },
                scale: {
                  duration: 4,
                  ease: "easeInOut",
                  repeat: Infinity,
                  delay: 2,
                },
              }}
            >
              <div className="text-center leading-tight">
                <span
                  className="block text-[13px] font-semibold text-soft-text"
                >
                  Siftrio
                </span>
                <span
                  className="block text-[11px] text-subtle-text"
                >
                  MCP
                </span>
              </div>
            </motion.div>

            {/* Tool cards */}
            {TOOLS.map((t, i) => {
              const floatDir = i % 2 === 0 ? -1.5 : 1.5
              return (
                <motion.div
                  key={t.id}
                  className="absolute flex items-center justify-center"
                  style={{
                    left: t.x,
                    top: t.y,
                    width: t.w,
                    height: t.h,
                    background: "var(--muted)",
                    border: "1px solid var(--subtle-border)",
                    borderRadius: 8,
                    boxShadow:
                      "0 1px 0 rgba(255,255,255,0.015), 0 4px 16px rgba(0,0,0,0.3)",
                  }}
                  variants={cardEntrance}
                  initial="hidden"
                  animate={inView ? "visible" : "hidden"}
                  custom={0.8 + i * 0.12}
                >
                  <motion.span
                    className="text-[12px] font-medium text-soft-text"
                    animate={{ y: [0, floatDir, 0] }}
                    transition={{
                      duration: 5.5 + i * 0.3,
                      ease: "easeInOut",
                      repeat: Infinity,
                      delay: 2 + i * 0.2,
                    }}
                  >
                    {t.label}
                  </motion.span>
                </motion.div>
              )
            })}

            {/* Resource cards */}
            {RESOURCES.map((r, i) => {
              const floatDir = i % 2 === 0 ? 1.5 : -1.5
              return (
                <motion.div
                  key={r.id}
                  className="absolute flex items-center justify-center"
                  style={{
                    left: r.x,
                    top: r.y,
                    width: r.w,
                    height: r.h,
                    background: "var(--muted)",
                    border: "1px solid var(--subtle-border)",
                    borderRadius: 8,
                    boxShadow:
                      "0 1px 0 rgba(255,255,255,0.015), 0 4px 16px rgba(0,0,0,0.3)",
                  }}
                  variants={cardEntrance}
                  initial="hidden"
                  animate={inView ? "visible" : "hidden"}
                  custom={3.0 + i * 0.1}
                >
                  <motion.span
                    className="text-[11px] font-medium text-soft-text"
                    animate={{ y: [0, floatDir, 0] }}
                    transition={{
                      duration: 6 + i * 0.4,
                      ease: "easeInOut",
                      repeat: Infinity,
                      delay: 4 + i * 0.15,
                    }}
                  >
                    {r.label}
                  </motion.span>
                </motion.div>
              )
            })}
          </div>
        </div>
      </div>
    </section>
  )
}
