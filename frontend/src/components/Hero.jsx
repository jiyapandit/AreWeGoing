// src/components/Hero.jsx
import { useEffect, useState } from "react";
import { motion, useReducedMotion } from "framer-motion";

function clamp(n, min, max) {
  return Math.max(min, Math.min(max, n));
}
function useScrollY() {
  const [y, setY] = useState(0);
  useEffect(() => {
    const onScroll = () => setY(window.scrollY || 0);
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);
  return y;
}
function GlassButton({ children, onClick, variant = "primary" }) {
  const base =
    "group inline-flex items-center justify-center rounded-2xl px-5 py-3 text-sm md:text-base transition will-change-transform";
  const glass =
    "bg-white/20 backdrop-blur-2xl border border-white/25 shadow-glass";
  const primary = "text-neutral-900 hover:bg-white/28 active:scale-[0.99]";
  const secondary =
    "text-neutral-900/85 hover:text-neutral-900 hover:bg-white/24 active:scale-[0.99]";
  return (
    <button
      onClick={onClick}
      className={[base, glass, variant === "primary" ? primary : secondary].join(" ")}
    >
      <span className="mr-3 h-[1px] w-5 bg-neutral-900/30 transition group-hover:w-7" />
      {children}
    </button>
  );
}

export default function Hero() {
  const y = useScrollY();
  const reduceMotion = useReducedMotion();

  const heroScale = reduceMotion ? 1 : 1 + clamp(y / 1800, 0, 0.06);
  const heroY = reduceMotion ? 0 : clamp(y * 0.08, 0, 52);

  const fadeUp = {
    hidden: { opacity: 0, y: 18, filter: "blur(6px)" },
    show: {
      opacity: 1,
      y: 0,
      filter: "blur(0px)",
      transition: { duration: 1.15, ease: [0.16, 1, 0.3, 1] },
    },
  };

  const floatSlow = reduceMotion
    ? {}
    : { y: [0, -8, 0], transition: { duration: 8.5, repeat: Infinity, ease: "easeInOut" } };

  return (
    <section id="create" className="relative h-[92vh] min-h-[680px] overflow-hidden">
      <div className="absolute inset-0 grain">
        <motion.div
          className="absolute inset-0"
          style={{ y: heroY, scale: heroScale, willChange: "transform" }}
        >
          <img
            src="https://images.unsplash.com/photo-1500530855697-b586d89ba3ee?auto=format&fit=crop&w=2400&q=80"
            alt="Cinematic travel"
            className="h-full w-full object-cover"
          />
          <div className="absolute inset-0 bg-gradient-to-b from-black/50 via-black/10 to-[#F5F2ED]" />
        </motion.div>
      </div>

      <div className="relative z-10 mx-auto max-w-6xl px-6 pt-20">
        <motion.div initial="hidden" animate="show" variants={fadeUp} className="max-w-2xl">
          <div className="inline-flex items-center gap-3 rounded-full bg-white/16 backdrop-blur-2xl border border-white/25 px-4 py-2 shadow-glass text-white/85 text-sm">
            <span className="h-1.5 w-1.5 rounded-full bg-white/70" />
            AreWeGoing • group travel, cinematic clarity
          </div>

          <h1 className="mt-6 font-serif text-white text-5xl md:text-7xl leading-[0.95] tracking-tight">
            Plan like a film.
            <br />
            Travel like it’s real.
          </h1>

          <p className="mt-5 text-white/80 text-base md:text-lg leading-relaxed max-w-xl">
            Create a group, collect preferences, and get an itinerary that feels human — not generic.
          </p>

          <div className="mt-8 flex flex-wrap gap-3">
            <GlassButton onClick={() => alert("Create Group (hook to your flow)")}>
              Create a group
            </GlassButton>
            <GlassButton variant="secondary" onClick={() => alert("Join Group (hook to your flow)")}>
              Join a group
            </GlassButton>
          </div>
        </motion.div>

        <motion.div className="mt-12 max-w-xl" animate={floatSlow}>
          <div className="rounded-[2rem] bg-white/14 backdrop-blur-2xl border border-white/20 shadow-glass p-5 text-white/85">
            <div className="text-xs uppercase tracking-[0.18em] text-white/70">Tonight’s vibe</div>
            <div className="mt-2 font-serif text-2xl text-white">
              “Golden hour cities. Ocean air. No chaos.”
            </div>
            <div className="mt-3 text-sm text-white/75">You’re composing a trip, not filling forms.</div>
          </div>
        </motion.div>
      </div>

      <div className="absolute bottom-6 left-0 right-0 z-10 flex justify-center">
        <div className="flex items-center gap-3 text-white/70 text-sm">
          <span className="h-8 w-[1px] bg-white/30" />
          Scroll
          <span className="h-8 w-[1px] bg-white/30" />
        </div>
      </div>
    </section>
  );
}