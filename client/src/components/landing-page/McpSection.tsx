"use client"

import { useRef, useState, useMemo, useCallback } from "react"
import { motion, useInView } from "framer-motion"

interface CardDef {
  id: string
  label: string
}

const TOOLS: readonly CardDef[] = [
  { id: "claude", label: "Claude Desktop" },
  { id: "cursor", label: "Cursor" },
  { id: "vscode", label: "VS Code" },
  { id: "windsurf", label: "Windsurf" },
  { id: "agent", label: "Custom Agent" },
]

const RESOURCES_ROW1: readonly CardDef[] = [
  { id: "meetings", label: "Meetings" },
  { id: "knowledge", label: "Knowledge" },
  { id: "projects", label: "Projects" },
  { id: "actions", label: "Action Items" },
  { id: "jira", label: "Jira" },
  { id: "calendar", label: "Google Calendar" },
]

const RESOURCES_ROW2: readonly CardDef[] = [
  { id: "docs", label: "Documents" },
  { id: "requirements", label: "Requirements" },
]

const EASE = [0.25, 0.1, 0.25, 1] as const

const CARD_W = 140
const CARD_H = 52
const CARD_RX = 10
const CIRCLE_R = 110

const VB_W = 1000
const VB_H = 760
const VB_CX = VB_W / 2
const VB_TOP_Y = 50
const VB_GAP1 = 120
const VB_GAP2 = 48
const VB_CIRCLE_CY = VB_TOP_Y + CARD_H + VB_GAP1 + CIRCLE_R
const VB_BOT1_Y = VB_CIRCLE_CY + CIRCLE_R + VB_GAP1
const VB_BOT2_Y = VB_BOT1_Y + CARD_H + VB_GAP2

function rowPositions(
  count: number,
  cardW: number,
  vbW: number,
  cy: number,
): { x: number; y: number }[] {
  const totalW = count * cardW + (count - 1) * 20
  const startX = (vbW - totalW) / 2
  return Array.from({ length: count }, (_, i) => ({
    x: startX + i * (cardW + 20),
    y: cy,
  }))
}

function circleEdgePoint(
  fromX: number,
  fromY: number,
  cx: number,
  cy: number,
  r: number,
): { x: number; y: number } {
  const dx = cx - fromX
  const dy = cy - fromY
  const len = Math.sqrt(dx * dx + dy * dy)
  if (len === 0) return { x: cx, y: cy - r }
  return { x: cx - (dx / len) * r, y: cy - (dy / len) * r }
}

function buildCurve(
  x1: number,
  y1: number,
  x2: number,
  y2: number,
): string {
  const my = (y1 + y2) / 2
  return `M${x1},${y1} C${x1},${my} ${x2},${my} ${x2},${y2}`
}

interface ComputedLayout {
  circleCY: number
  tools: { id: string; label: string; x: number; y: number }[]
  resRow1: { id: string; label: string; x: number; y: number }[]
  resRow2: { id: string; label: string; x: number; y: number }[]
  edges: {
    id: string
    path: string
    fromX: number
    fromY: number
    toX: number
    toY: number
  }[]
}

function computeLayout(): ComputedLayout {
  const circleCY = VB_CIRCLE_CY

  const tools = rowPositions(TOOLS.length, CARD_W, VB_W, VB_TOP_Y).map(
    (p, i) => ({ ...TOOLS[i], ...p }),
  )

  const resRow1 = rowPositions(
    RESOURCES_ROW1.length,
    CARD_W,
    VB_W,
    VB_BOT1_Y,
  ).map((p, i) => ({ ...RESOURCES_ROW1[i], ...p }))

  const resRow2 = rowPositions(
    RESOURCES_ROW2.length,
    CARD_W,
    VB_W,
    VB_BOT2_Y,
  ).map((p, i) => ({ ...RESOURCES_ROW2[i], ...p }))

  const edges: ComputedLayout["edges"] = []

  for (const t of tools) {
    const fx = t.x + CARD_W / 2
    const fy = t.y + CARD_H
    const ep = circleEdgePoint(fx, fy, VB_CX, circleCY, CIRCLE_R)
    edges.push({
      id: `edge-${t.id}`,
      path: buildCurve(fx, fy, ep.x, ep.y),
      fromX: fx,
      fromY: fy,
      toX: ep.x,
      toY: ep.y,
    })
  }

  for (const r of [...resRow1, ...resRow2]) {
    const fx = r.x + CARD_W / 2
    const fy = r.y
    const ep = circleEdgePoint(fx, fy, VB_CX, circleCY, CIRCLE_R)
    edges.push({
      id: `edge-${r.id}`,
      path: buildCurve(fx, fy, ep.x, ep.y),
      fromX: fx,
      fromY: fy,
      toX: ep.x,
      toY: ep.y,
    })
  }

  return { circleCY, tools, resRow1, resRow2, edges }
}

export function McpSection() {
  const ref = useRef<HTMLDivElement>(null)
  const inView = useInView(ref, { once: true, margin: "-80px" })
  const [hovered, setHovered] = useState<string | null>(null)
  const layout = useMemo(() => computeLayout(), [])

  const nodeOpacity = useCallback(
    (nodeId: string) => {
      if (!hovered) return 1
      if (nodeId === "center" || nodeId === hovered) return 1
      return layout.edges.some(
        (e) =>
          e.id === `edge-${hovered}` &&
          (e.id === `edge-${nodeId}` || nodeId === "center"),
      )
        ? 1
        : 0.2
    },
    [hovered, layout.edges],
  )

  const edgeOpacity = useCallback(
    (edgeId: string) => {
      if (!hovered) return 0.12
      return edgeId === `edge-${hovered}` ? 0.45 : 0.06
    },
    [hovered],
  )

  const isRelated = useCallback(
    (nodeId: string) => {
      if (!hovered) return false
      if (nodeId === hovered || nodeId === "center") return true
      return layout.edges.some(
        (e) =>
          e.id === `edge-${hovered}` &&
          (e.id === `edge-${nodeId}` || nodeId === "center"),
      )
    },
    [hovered, layout.edges],
  )

  const nodeScale = useCallback(
    (nodeId: string) => {
      if (!hovered) return 1
      return nodeId === hovered ? 1.03 : 0.98
    },
    [hovered],
  )

  const SvgCard = ({
    id,
    label,
    x,
    y,
    delay,
  }: {
    id: string
    label: string
    x: number
    y: number
    delay: number
  }) => (
    <motion.g
      initial={{ opacity: 0, y: 10 }}
      animate={
        inView
          ? { opacity: nodeOpacity(id), y: 0, scale: nodeScale(id) }
          : { opacity: 0, y: 10, scale: 1 }
      }
      transition={{
        opacity: { duration: 0.3 },
        y: { duration: 0.8, ease: EASE, delay },
        scale: { duration: 0.2, ease: "easeOut" },
      }}
      style={{ transformOrigin: `${x + CARD_W / 2}px ${y + CARD_H / 2}px` }}
      onMouseEnter={() => setHovered(id)}
      onMouseLeave={() => setHovered(null)}
      className="cursor-pointer"
    >
      <rect
        x={x}
        y={y}
        width={CARD_W}
        height={CARD_H}
        rx={CARD_RX}
        fill="var(--muted)"
        stroke="var(--subtle-border)"
        strokeWidth={1}
        style={{
          filter: isRelated(id)
            ? "drop-shadow(0 1px 0 rgba(255,255,255,0.02)) drop-shadow(0 6px 20px rgba(0,0,0,0.35))"
            : "drop-shadow(0 1px 0 rgba(255,255,255,0.015)) drop-shadow(0 4px 16px rgba(0,0,0,0.3))",
          transition: "filter 0.2s ease-out, stroke 0.2s ease-out",
          stroke: isRelated(id) ? "var(--subtle-text)" : "var(--subtle-border)",
        }}
      />
      <text
        x={x + CARD_W / 2}
        y={y + CARD_H / 2 + 1}
        textAnchor="middle"
        dominantBaseline="middle"
        fill="var(--soft-text)"
        fontSize={12}
        fontWeight={500}
        fontFamily="var(--font-sans)"
        pointerEvents="none"
      >
        {label}
      </text>
    </motion.g>
  )

  return (
    <section className="relative overflow-x-hidden bg-background">
      {/* Mobile */}
      <div className="block md:hidden">
        <div className="mx-auto max-w-3xl px-6 py-24">
          <div className="mb-12 space-y-6 text-center">
            <p className="text-[11px] font-medium uppercase tracking-[0.2em] text-subtle-text">
              MCP Server
            </p>
            <h2 className="text-3xl font-semibold leading-[1.15] tracking-tight text-foreground">
              Connect your favorite
              <br />
              AI tools.
            </h2>
            <p className="mx-auto max-w-md text-[15px] leading-relaxed text-disabled-text">
              Use Claude Desktop, Cursor, VS Code, Windsurf, or your own AI
              agents with secure access to your Siftrio workspace through the
              Model Context Protocol.
            </p>
          </div>

          <div className="space-y-6">
            <div className="space-y-3 text-center">
              <span className="text-[11px] font-medium uppercase tracking-[0.15em] text-faint-text">
                AI Clients
              </span>
              <div className="flex flex-wrap justify-center gap-2">
                {[...TOOLS].map((t) => (
                  <span
                    key={t.id}
                    className="rounded-lg border border-subtle-border bg-muted px-3 py-2 text-[12px] font-medium text-soft-text"
                  >
                    {t.label}
                  </span>
                ))}
              </div>
            </div>

            <div className="flex justify-center">
              <div
                className="flex h-24 w-24 items-center justify-center rounded-full border border-subtle-border bg-muted"
                style={{
                  boxShadow:
                    "0 1px 0 rgba(255,255,255,0.015), 0 4px 20px rgba(0,0,0,0.3)",
                }}
              >
                <div className="text-center leading-tight">
                  <span className="block text-[11px] font-semibold text-soft-text">
                    Siftrio
                  </span>
                  <span className="block text-[9px] text-subtle-text">
                    MCP
                  </span>
                </div>
              </div>
            </div>

            <div className="space-y-3 text-center">
              <span className="text-[11px] font-medium uppercase tracking-[0.15em] text-faint-text">
                Knowledge Sources
              </span>
              <div className="flex flex-wrap justify-center gap-2">
                {[...RESOURCES_ROW1, ...RESOURCES_ROW2].map((r) => (
                  <span
                    key={r.id}
                    className="rounded-lg border border-subtle-border bg-muted px-3 py-2 text-[11px] font-medium text-soft-text"
                  >
                    {r.label}
                  </span>
                ))}
              </div>
            </div>
          </div>

          <div className="mt-10 rounded-lg border border-subtle-border bg-muted/50 p-4 text-center">
            <p className="text-[13px] text-subtle-text">
              One protocol. Every project. Unlimited context.
            </p>
          </div>
        </div>
      </div>

      {/* Desktop / Tablet */}
      <div className="hidden md:block">
        <div className="mx-auto flex w-full max-w-7xl flex-col items-center gap-16 px-6 py-32 md:flex-row md:items-center md:px-12 lg:px-20">
          {/* Left — Text */}
          <div className="flex-1 space-y-8 md:max-w-[40%]">
            <div className="space-y-6">
              <p className="text-[11px] font-medium uppercase tracking-[0.2em] text-subtle-text">
                MCP Server
              </p>
              <h2 className="text-3xl font-semibold leading-[1.15] tracking-tight text-foreground sm:text-4xl lg:text-5xl">
                Connect your favorite
                <br />
                AI tools.
              </h2>
              <p className="max-w-md text-[15px] leading-relaxed text-disabled-text sm:text-base">
                Use Claude Desktop, Cursor, VS Code, Windsurf, or your own AI
                agents with secure access to your Siftrio workspace through the
                Model Context Protocol.
              </p>
            </div>
            <p className="text-sm font-medium tracking-wide text-faint-text">
              One protocol. Every project. Unlimited context.
            </p>
          </div>

          {/* Right — Diagram */}
          <div
            ref={ref}
            className="flex flex-1 justify-center overflow-hidden md:max-w-[60%]"
          >
            <svg
              className="h-auto w-full"
              viewBox={`0 0 ${VB_W} ${VB_H}`}
              fill="none"
              preserveAspectRatio="xMidYMid meet"
            >
              <defs>
                <radialGradient id="centerGlow" cx="50%" cy="50%" r="50%">
                  <stop offset="0%" stopColor="var(--svg-line)" stopOpacity={0.15} />
                  <stop offset="100%" stopColor="var(--svg-line)" stopOpacity={0} />
                </radialGradient>
              </defs>

              {/* Background track lines */}
              {layout.edges.map((edge) => (
                <path
                  key={`bg-${edge.id}`}
                  d={edge.path}
                  stroke="var(--svg-bg-track)"
                  strokeWidth={1.5}
                  fill="none"
                />
              ))}

              {/* Animated edge lines */}
              {inView &&
                layout.edges.map((edge, i) => (
                  <motion.path
                    key={edge.id}
                    d={edge.path}
                    stroke="var(--svg-line)"
                    strokeWidth={1.5}
                    fill="none"
                    initial={{ pathLength: 0 }}
                    animate={{
                      pathLength: 1,
                      strokeOpacity: edgeOpacity(edge.id),
                    }}
                    transition={{
                      pathLength: {
                        duration: 0.8,
                        ease: "easeOut",
                        delay: 0.4 + i * 0.06,
                      },
                      strokeOpacity: { duration: 0.25 },
                    }}
                  />
                ))}

              {/* Data-flow dots: top → center (tools) */}
              {inView &&
                layout.edges.slice(0, TOOLS.length).map((edge, i) => (
                    <circle
                      key={`dot-${edge.id}`}
                      r={2.5}
                      fill="var(--subtle-text)"
                      opacity={0}
                      className="dataflow-dot"
                      style={{
                        offsetPath: `path('${edge.path}')`,
                        ["--df-duration" as string]: "5s",
                        ["--df-delay" as string]: `${1.0 + i * 0.5}s`,
                      }}
                    />
                  ),
                )}

              {/* Data-flow dots: center → bottom (resources) */}
              {inView &&
                layout.edges.slice(TOOLS.length).map((edge, i) => (
                    <circle
                      key={`dot-${edge.id}`}
                      r={2.5}
                      fill="var(--subtle-text)"
                      opacity={0}
                      className="dataflow-dot"
                      style={{
                        offsetPath: `path('${edge.path}')`,
                        ["--df-duration" as string]: "6s",
                        ["--df-delay" as string]: `${2.0 + i * 0.4}s`,
                      }}
                    />
                  ),
                )}

              {/* Center circle */}
              <motion.g
                initial={{ opacity: 0, scale: 0.92 }}
                animate={
                  inView
                    ? {
                        opacity: nodeOpacity("center"),
                        scale: nodeScale("center"),
                      }
                    : { opacity: 0, scale: 0.92 }
                }
                transition={{
                  opacity: { duration: 0.9, ease: EASE, delay: 0.2 },
                  scale: { duration: 0.25, ease: "easeOut" },
                }}
                style={{
                  transformOrigin: `${VB_CX}px ${layout.circleCY}px`,
                }}
                onMouseEnter={() => setHovered("center")}
                onMouseLeave={() => setHovered(null)}
                className="cursor-pointer"
              >
                <circle
                  cx={VB_CX}
                  cy={layout.circleCY}
                  r={CIRCLE_R + 40}
                  fill="url(#centerGlow)"
                  pointerEvents="none"
                />
                <circle
                  cx={VB_CX}
                  cy={layout.circleCY}
                  r={CIRCLE_R}
                  fill="var(--muted)"
                  stroke="var(--subtle-border)"
                  strokeWidth={1}
                  style={{
                    filter:
                      "drop-shadow(0 1px 0 rgba(255,255,255,0.015)) drop-shadow(0 4px 20px rgba(0,0,0,0.3))",
                    transition: "stroke 0.2s ease-out",
                    stroke: isRelated("center")
                      ? "var(--subtle-text)"
                      : "var(--subtle-border)",
                  }}
                />
                <text
                  x={VB_CX}
                  y={layout.circleCY - 8}
                  textAnchor="middle"
                  fill="var(--soft-text)"
                  fontSize={18}
                  fontWeight={600}
                  fontFamily="var(--font-sans)"
                  pointerEvents="none"
                >
                  Siftrio
                </text>
                <text
                  x={VB_CX}
                  y={layout.circleCY + 14}
                  textAnchor="middle"
                  fill="var(--subtle-text)"
                  fontSize={12}
                  fontFamily="var(--font-sans)"
                  pointerEvents="none"
                >
                  MCP
                </text>
              </motion.g>

              {/* Top row — AI Clients */}
              {layout.tools.map((t, i) => (
                <SvgCard
                  key={t.id}
                  id={t.id}
                  label={t.label}
                  x={t.x}
                  y={t.y}
                  delay={0.7 + i * 0.1}
                />
              ))}

              {/* Bottom row 1 */}
              {layout.resRow1.map((r, i) => (
                <SvgCard
                  key={r.id}
                  id={r.id}
                  label={r.label}
                  x={r.x}
                  y={r.y}
                  delay={1.8 + i * 0.08}
                />
              ))}

              {/* Bottom row 2 */}
              {layout.resRow2.map((r, i) => (
                <SvgCard
                  key={r.id}
                  id={r.id}
                  label={r.label}
                  x={r.x}
                  y={r.y}
                  delay={2.4 + i * 0.08}
                />
              ))}
            </svg>
          </div>
        </div>
      </div>
    </section>
  )
}
