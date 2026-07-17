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
          className="mt-16 flex w-full max-w-[90%] items-center justify-center"
          style={{ aspectRatio: "16 / 9" }}
        >
          <div
            className="flex h-full w-full items-center justify-center"
            style={{
              background: "#111213",
              border: "1px dashed #1C1E22",
              borderRadius: 10,
            }}
          >
            <span
              className="text-sm"
              style={{ color: "#3A3E44" }}
            >
              Product Screenshot
            </span>
          </div>
        </div>
      </div>
    </section>
  )
}
