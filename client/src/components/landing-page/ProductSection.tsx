"use client";

import Image from "next/image";

export function ProductSection() {
  return (
    <section
      className="relative flex items-center"
      style={{ background: "#08090A" }}
    >
      <div className="mx-auto flex w-full max-w-7xl flex-col items-center px-6 py-32 md:px-12 lg:px-20">
        <div className="max-w-2xl space-y-6 text-center">
          <p
            className="text-[11px] font-medium uppercase tracking-[0.2em]"
            style={{ color: "#4A4E54" }}
          >
            Product
          </p>

          <h2
            className="text-3xl font-semibold leading-[1.15] tracking-tight sm:text-4xl lg:text-5xl"
            style={{ color: "#FFFFFF" }}
          >
            Built for projects
            <br />
            that never lose context.
          </h2>

          <p
            className="mx-auto max-w-xl text-[15px] leading-relaxed sm:text-base"
            style={{ color: "#6D737C" }}
          >
            Every meeting, decision, and action lives in one intelligent
            workspace, giving your team and AI a shared understanding of the
            entire project.
          </p>
        </div>

        <div
          className="relative mt-16 w-full max-w-[90%] select-none overflow-hidden"
          style={{ aspectRatio: "16 / 9", borderRadius: 10 }}
          onContextMenu={(e) => e.preventDefault()}
          onDragStart={(e) => e.preventDefault()}
        >
          <Image
            src="/product-ss.png"
            alt="Siftrio product screenshot"
            fill
            className="pointer-events-none object-cover"
            priority
            draggable={false}
          />
          <div
            className="pointer-events-none absolute inset-0"
            style={{
              background:
                "linear-gradient(to bottom, transparent 60%, #08090A)",
            }}
          />
        </div>
      </div>
    </section>
  );
}
