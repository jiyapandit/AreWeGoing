// src/components/ValueProps.jsx
import { motion, useReducedMotion } from "framer-motion";

export default function ValueProps() {
  const reduce = useReducedMotion();
  const item = {
    hidden: { opacity: 0, y: 14, filter: "blur(6px)" },
    show: (i) => ({
      opacity: 1,
      y: 0,
      filter: "blur(0px)",
      transition: { duration: 0.95, delay: i * 0.08, ease: [0.16, 1, 0.3, 1] },
    }),
  };

  const cards = [
    {
      title: "Everyone answers. One trip happens.",
      text: "Collect preferences without chaos — the plan resolves into one direction.",
    },
    {
      title: "Balance budget, pace, and vibes.",
      text: "No one gets steamrolled. The itinerary respects the group.",
    },
    {
      title: "A plan that feels curated.",
      text: "Real places, believable timing, and a flow you actually want to follow.",
    },
  ];

  return (
    <section className="mx-auto max-w-6xl px-6 pb-16 md:pb-20">
      <div className="grid md:grid-cols-3 gap-5">
        {cards.map((c, i) => (
          <motion.div
            key={c.title}
            initial={reduce ? false : "hidden"}
            whileInView={reduce ? undefined : "show"}
            viewport={{ once: true, amount: 0.35 }}
            variants={item}
            custom={i}
            className="rounded-[2rem] bg-white/70 border border-black/5 shadow-glass p-7 md:p-8"
          >
            <div className="font-serif text-2xl leading-snug">{c.title}</div>
            <div className="mt-3 text-neutral-700 leading-relaxed">{c.text}</div>
            <div className="mt-6 h-[1px] w-full bg-black/5" />
            <div className="mt-5 text-sm text-neutral-600">Cinematic clarity over generic planning.</div>
          </motion.div>
        ))}
      </div>
    </section>
  );
}