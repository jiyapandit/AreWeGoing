export default function SampleTrip() {
  return (
    <section id="sample" className="mx-auto max-w-6xl px-6 pb-20">
      <div className="flex items-end justify-between gap-6">
        <div>
          <h2 className="font-serif text-4xl md:text-5xl leading-tight">Sample trip preview</h2>
          <p className="mt-3 text-neutral-700 max-w-xl">
            Bottom placement. Clean. Believable. A real preview of what users get.
          </p>
        </div>
      </div>

      <div className="mt-10 rounded-[2rem] bg-white/70 border border-black/5 shadow-glass overflow-hidden">
        <div className="p-7 md:p-10 flex flex-col md:flex-row md:items-center md:justify-between gap-6">
          <div>
            <div className="text-xs uppercase tracking-[0.18em] text-neutral-600">
              4 days • NYC • mid budget • night views
            </div>
            <div className="mt-2 font-serif text-3xl md:text-4xl">City lights & skyline air</div>
            <div className="mt-2 text-neutral-700">
              Pace: balanced • Food: mixed • Transit: subway + walking
            </div>
          </div>

          <div className="flex gap-3">
            <button className="rounded-2xl px-5 py-3 bg-black text-white shadow-glass hover:opacity-90 transition">
              View itinerary
            </button>
            <button className="rounded-2xl px-5 py-3 bg-white/60 border border-black/5 shadow-glass hover:bg-white/80 transition">
              Edit preferences
            </button>
          </div>
        </div>

        <div className="border-t border-black/5 grid md:grid-cols-4">
          {[
            { day: "Day 1", line: "Arrival • sunset walk • skyline view" },
            { day: "Day 2", line: "Neighborhoods • coffee • night tour" },
            { day: "Day 3", line: "Iconic spots • chill lunch • show" },
            { day: "Day 4", line: "Brunch • last photos • checkout" },
          ].map((d) => (
            <div
              key={d.day}
              className="p-6 md:p-7 border-black/5 md:border-r last:border-r-0"
            >
              <div className="text-xs uppercase tracking-[0.18em] text-neutral-600">{d.day}</div>
              <div className="mt-2 text-neutral-800">{d.line}</div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}