// src/components/HowItWorks.jsx
export default function HowItWorks() {
  const steps = [
    { k: "01", title: "Create or join", text: "Host a group trip or join one solo." },
    { k: "02", title: "Add preferences", text: "Budget, vibes, food, pace, activities." },
    { k: "03", title: "Get the itinerary", text: "A plan that feels human — and shareable." },
  ];

  return (
    <section id="how" className="mx-auto max-w-6xl px-6 pb-16 md:pb-20">
      <div className="flex items-end justify-between gap-6">
        <div>
          <h2 className="font-serif text-4xl md:text-5xl leading-tight">How it works</h2>
          <p className="mt-3 text-neutral-700 max-w-xl">
            Three steps. No noise. Just direction.
          </p>
        </div>
      </div>

      <div className="mt-10 grid md:grid-cols-3 gap-5">
        {steps.map((s) => (
          <div key={s.k} className="rounded-[2rem] bg-white/70 border border-black/5 shadow-glass p-7 md:p-8">
            <div className="text-xs uppercase tracking-[0.18em] text-neutral-600">{s.k}</div>
            <div className="mt-3 font-serif text-2xl">{s.title}</div>
            <div className="mt-2 text-neutral-700">{s.text}</div>
          </div>
        ))}
      </div>
    </section>
  );
}