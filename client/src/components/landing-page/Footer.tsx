"use client";

import { useRef } from "react";
import Link from "next/link";
import { motion, useInView } from "framer-motion";
import { FaGithub, FaLinkedinIn, FaXTwitter } from "react-icons/fa6";
import { HiOutlineGlobeAlt } from "react-icons/hi2";

const EASE = [0.25, 0.1, 0.25, 1] as const;

const SOCIALS = [
  { icon: FaGithub, label: "GitHub", href: "https://github.com/cleosneha" },
  {
    icon: FaLinkedinIn,
    label: "LinkedIn",
    href: "https://linkedin.com/in/cleosneha",
  },
  { icon: FaXTwitter, label: "X", href: "https://x.com/cleosneha" },
  {
    icon: HiOutlineGlobeAlt,
    label: "Portfolio",
    href: "https://snehasharma.in",
  },
];

export function Footer() {
  const ref = useRef<HTMLDivElement>(null);
  const inView = useInView(ref, { once: true, margin: "-40px" });

  return (
    <>
      {/* Gradient fade before footer */}
      <div
        style={{
          height: 80,
          background:
            "linear-gradient(to bottom, var(--background), var(--muted))",
        }}
      />

      <footer
        ref={ref}
        className="footer-curve relative overflow-hidden bg-muted"
        style={{ height: 340 }}
      >
        {/* Content */}
        <div className="relative z-10 flex h-full flex-col items-center justify-center px-6 text-center">
          <motion.h2
            className="text-xl font-semibold tracking-tight text-foreground"
            initial={{ opacity: 0, y: 10 }}
            animate={inView ? { opacity: 1, y: 0 } : { opacity: 0, y: 10 }}
            transition={{ duration: 0.45, ease: EASE }}
          >
            Siftrio
          </motion.h2>

          <motion.p
            className="mt-2 max-w-xs text-[14px] leading-relaxed text-disabled-text"
            initial={{ opacity: 0, y: 8 }}
            animate={inView ? { opacity: 1, y: 0 } : { opacity: 0, y: 8 }}
            transition={{ duration: 0.45, ease: EASE, delay: 0.05 }}
          >
            AI-native project memory for modern software teams.
          </motion.p>

          <motion.div
            className="mt-8 flex items-center gap-2 text-[13px] text-subtle-text"
            initial={{ opacity: 0 }}
            animate={inView ? { opacity: 1 } : { opacity: 0 }}
            transition={{ duration: 0.45, ease: EASE, delay: 0.1 }}
          >
            <Link
              href="/privacy"
              className="transition-colors duration-200 hover:text-soft-text"
            >
              Privacy Policy
            </Link>
            <span>•</span>
            <Link
              href="/terms"
              className="transition-colors duration-200 hover:text-soft-text"
            >
              Terms &amp; Conditions
            </Link>
            <span>•</span>
            <Link
              href="/compliance"
              className="transition-colors duration-200 hover:text-soft-text"
            >
              Compliance
            </Link>
          </motion.div>

          <motion.div
            className="mt-10"
            initial={{ opacity: 0 }}
            animate={inView ? { opacity: 1 } : { opacity: 0 }}
            transition={{ duration: 0.45, ease: EASE, delay: 0.15 }}
          >
            <p className="mb-4 text-[10px] font-medium uppercase tracking-[0.2em] text-faint-text">
              Connect with the developer
            </p>

            <div className="flex items-center justify-center gap-5">
              {SOCIALS.map((s, i) => (
                <motion.a
                  key={s.label}
                  href={s.href}
                  aria-label={s.label}
                  className="flex items-center justify-center transition-all duration-200 text-subtle-text"
                  whileHover={{ y: -2, color: "var(--soft-text)" }}
                  initial={{ opacity: 0, y: 6 }}
                  animate={inView ? { opacity: 1, y: 0 } : { opacity: 0, y: 6 }}
                  transition={{
                    opacity: {
                      duration: 0.35,
                      ease: EASE,
                      delay: 0.2 + i * 0.06,
                    },
                    y: { duration: 0.35, ease: EASE, delay: 0.2 + i * 0.06 },
                  }}
                >
                  <s.icon size={18} />
                </motion.a>
              ))}
            </div>
          </motion.div>
        </div>
      </footer>
    </>
  );
}
