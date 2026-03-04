// src/components/HowItWorks.jsx
export default function HowItWorks() {
  const steps = [
    { k: "01", title: "Create or join", text: "Start a group trip or jump into one your friends opened." },
    { k: "02", title: "Add preferences", text: "Budget, pace, food, activities, and vibe in one quick flow." },
    { k: "03", title: "Get your route", text: "Receive a practical itinerary and share it instantly." },
  ];

  return (
    <section id="how" className="mx-auto max-w-6xl px-6 pb-16 md:pb-20">
      <div>
        <h2 className="font-serif text-4xl leading-tight text-[#fff6e8] md:text-5xl">How it works</h2>
        <p className="mt-3 max-w-xl text-[#eadcc8]/90">Three steps. Real output. No planning fatigue.</p>
      </div>

      <div className="mt-10 grid gap-5 md:grid-cols-3">
        {steps.map((s) => (
          <article key={s.k} className="liquid-panel rounded-[2rem] border border-white/20 p-7 md:p-8">
            <div className="text-xs uppercase tracking-[0.18em] text-[#e7d9c5]/80">{s.k}</div>
            <div className="mt-3 font-serif text-2xl text-[#fff8ed]">{s.title}</div>
            <div className="mt-2 text-[#ebdecc]/90">{s.text}</div>
          </article>
        ))}
      </div>
    </section>
  );
}

