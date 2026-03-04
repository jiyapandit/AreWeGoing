// src/components/Hero.jsx
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

function clamp(n, min, max) {
  return Math.max(min, Math.min(max, n));
}

function GlassButton({ children, to, variant = "primary" }) {
  const base =
    "group inline-flex items-center justify-center rounded-2xl px-5 py-3 text-sm md:text-base transition will-change-transform";
  const glass = "liquid-chip border border-white/20";
  const primary = "text-[#fff8ed] hover:bg-white/16 active:scale-[0.99]";
  const secondary = "text-[#efe4d3] hover:text-[#fff8ed] hover:bg-white/14 active:scale-[0.99]";

  return (
    <Link to={to} className={[base, glass, variant === "primary" ? primary : secondary].join(" ")}>
      <span className="mr-3 h-[1px] w-5 bg-[#f7ebdb]/45 transition group-hover:w-7" />
      {children}
    </Link>
  );
}

export default function Hero() {
  const [scrollY, setScrollY] = useState(0);

  useEffect(() => {
    const onScroll = () => setScrollY(window.scrollY || 0);
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  const bgY = clamp(scrollY * 0.11, 0, 95);
  const fgY = clamp(scrollY * -0.06, -54, 0);
  const cardRotate = clamp(scrollY * -0.015, -8, 0);

  return (
    <section id="create" className="relative min-h-[92vh] overflow-hidden pt-8">
      <div className="absolute inset-0" style={{ transform: `translateY(${bgY}px)` }}>
        <img
          src="https://images.unsplash.com/photo-1469474968028-56623f02e42e?auto=format&fit=crop&w=2600&q=80"
          alt="Travel landscape"
          className="h-full w-full object-cover"
        />
      </div>
      <div className="absolute inset-0 landing-hero-overlay" />
      <div className="absolute inset-0 grain" />

      <div className="relative z-10 mx-auto max-w-6xl px-6 pb-16 pt-20" style={{ transform: `translateY(${fgY}px)` }}>
        <div className="max-w-3xl">
          <div className="liquid-chip inline-flex items-center gap-3 rounded-full border border-white/25 px-4 py-2 text-sm text-[#f8ecdc]/90">
            <span className="h-1.5 w-1.5 rounded-full bg-[#f4e4ca]" />
            AreWeGoing - travel planning with cinematic depth
          </div>

          <h1 className="mt-6 font-serif text-5xl leading-[0.94] tracking-tight text-[#fff8eb] md:text-7xl">
            One question.
            <br />
            One unforgettable route.
          </h1>

          <p className="mt-5 max-w-2xl text-base leading-relaxed text-[#f2e6d7]/88 md:text-lg">
            Align your group on vibe, budget, and pace. AreWeGoing turns scattered opinions into a travel
            plan that feels handcrafted.
          </p>

          <div className="mt-9 flex flex-wrap gap-3">
            <GlassButton to="/signup">
              Create an account
            </GlassButton>
            <GlassButton to="/login" variant="secondary">
              Sign in
            </GlassButton>
          </div>
        </div>

        <div className="mt-12 max-w-xl" style={{ transform: `perspective(1200px) rotateX(${cardRotate}deg)` }}>
          <div className="liquid-panel rounded-[2rem] border border-white/20 p-5 text-[#f7ecdd]/90 md:p-6">
            <div className="text-xs uppercase tracking-[0.18em] text-[#f2e1c8]/80">Tonight&apos;s frame</div>
            <div className="mt-2 font-serif text-2xl text-[#fff7e9] md:text-3xl">
              "Sunset coastlines, late espresso, and no planning chaos."
            </div>
            <div className="mt-3 text-sm text-[#eedecc]/86">
              3D scroll depth now matches your login page motion language.
            </div>
          </div>
        </div>
      </div>

      <div className="absolute bottom-6 left-0 right-0 z-10 flex justify-center">
        <div className="flex items-center gap-3 text-sm text-[#f3e4cf]/78">
          <span className="h-8 w-[1px] bg-[#f4e4ca]/35" />
          Scroll
          <span className="h-8 w-[1px] bg-[#f4e4ca]/35" />
        </div>
      </div>
    </section>
  );
}

