// src/components/Navbar.jsx
import { motion, useReducedMotion } from "framer-motion";

export default function Navbar() {
  const reduce = useReducedMotion();
  return (
    <motion.header
      initial={reduce ? false : { opacity: 0, y: -10, filter: "blur(6px)" }}
      animate={reduce ? false : { opacity: 1, y: 0, filter: "blur(0px)" }}
      transition={{ duration: 0.9, ease: [0.16, 1, 0.3, 1] }}
      className="sticky top-0 z-50"
    >
      <div className="mx-auto max-w-6xl px-6 py-4">
        <div className="rounded-3xl bg-white/25 backdrop-blur-2xl border border-white/35 shadow-glass">
          <div className="flex items-center justify-between px-5 py-3">
            <div className="flex items-center gap-3">
              <div className="h-9 w-9 rounded-2xl bg-black/80" />
              <div className="leading-tight">
                <div className="font-serif text-lg">AreWeGoing</div>
                <div className="text-xs text-neutral-600">cinematic group travel</div>
              </div>
            </div>

            <nav className="hidden md:flex items-center gap-7 text-sm text-neutral-700">
              <a href="#how" className="hover:text-neutral-900">How it works</a>
              <a href="#destinations" className="hover:text-neutral-900">Destinations</a>
              <a href="#sample" className="hover:text-neutral-900">Sample trip</a>
              <a href="#signin" className="hover:text-neutral-900">Sign in</a>
            </nav>

            <div className="flex items-center gap-2">
              <a
                href="#create"
                className="hidden md:inline-flex rounded-2xl px-4 py-2 bg-white/40 border border-black/5 shadow-glass hover:bg-white/60 transition text-sm"
              >
                Create group
              </a>
              <button className="md:hidden rounded-2xl px-3 py-2 bg-white/40 border border-black/5 shadow-glass">
                ☰
              </button>
            </div>
          </div>
        </div>
      </div>
    </motion.header>
  );
}