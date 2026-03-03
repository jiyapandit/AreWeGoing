// src/components/DestinationsCarousel.jsx
import { useMemo, useRef } from "react";

function Slide({ title, mood, image }) {
  return (
    <div className="snap-center shrink-0 w-[86%] md:w-[58%] lg:w-[42%]">
      <div className="relative h-[420px] md:h-[520px] rounded-[2rem] overflow-hidden">
        <img src={image} alt={title} className="absolute inset-0 h-full w-full object-cover" loading="lazy" />
        <div className="absolute inset-0 bg-gradient-to-t from-black/55 via-black/10 to-transparent" />
        <div className="absolute left-6 right-6 bottom-6">
          <div className="inline-flex items-center gap-3 rounded-2xl bg-white/16 backdrop-blur-2xl border border-white/20 px-4 py-3 shadow-glass">
            <div className="h-2 w-2 rounded-full bg-white/70" />
            <div>
              <div className="font-serif text-white text-2xl leading-tight">{title}</div>
              <div className="text-white/80 text-sm">{mood}</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default function DestinationsCarousel() {
  const carouselRef = useRef(null);
  const slides = useMemo(
    () => [
      {
        title: "Amalfi Coast",
        mood: "Salt air • late sun • slow mornings",
        image:
          "https://images.unsplash.com/photo-1500375592092-40eb2168fd21?auto=format&fit=crop&w=2000&q=80",
      },
      {
        title: "Kyoto",
        mood: "Mist • bamboo • soft footsteps",
        image:
          "https://images.unsplash.com/photo-1549692520-acc6669e2f0c?auto=format&fit=crop&w=2000&q=80",
      },
      {
        title: "New York",
        mood: "Night lights • elevators • city pulse",
        image:
          "https://images.unsplash.com/photo-1496588152823-86ff7695d109?auto=format&fit=crop&w=2000&q=80",
      },
      {
        title: "Banff",
        mood: "Glacial water • quiet trails • deep blue",
        image:
          "https://images.unsplash.com/photo-1500043357865-c6b8827edf2c?auto=format&fit=crop&w=2000&q=80",
      },
    ],
    []
  );

  const scrollBySlide = (dir) => {
    const el = carouselRef.current;
    if (!el) return;
    el.scrollBy({ left: dir * el.clientWidth * 0.7, behavior: "smooth" });
  };

  return (
    <section id="destinations" className="mx-auto max-w-6xl px-6 py-16 md:py-20">
      <div className="flex items-end justify-between gap-6">
        <div>
          <h2 className="font-serif text-4xl md:text-5xl leading-tight">Destinations with a pulse.</h2>
          <p className="mt-3 text-neutral-700 max-w-xl">
            Real places. Real photos. Slow motion. Pick a mood and build the trip around it.
          </p>
        </div>
        <div className="hidden md:flex gap-2">
          <button
            onClick={() => scrollBySlide(-1)}
            className="rounded-2xl px-4 py-3 bg-white/60 border border-black/5 shadow-glass hover:bg-white/75 transition"
          >
            ←
          </button>
          <button
            onClick={() => scrollBySlide(1)}
            className="rounded-2xl px-4 py-3 bg-white/60 border border-black/5 shadow-glass hover:bg-white/75 transition"
          >
            →
          </button>
        </div>
      </div>

      <div
        ref={carouselRef}
        className="mt-10 flex gap-5 overflow-x-auto no-scrollbar snap-x snap-mandatory scroll-px-6 pb-2"
      >
        <div className="shrink-0 w-[2px]" />
        {slides.map((s) => (
          <Slide key={s.title} title={s.title} mood={s.mood} image={s.image} />
        ))}
        <div className="shrink-0 w-[2px]" />
      </div>

      <div className="mt-6 md:hidden flex justify-center gap-2">
        <button
          onClick={() => scrollBySlide(-1)}
          className="rounded-2xl px-4 py-3 bg-white/60 border border-black/5 shadow-glass"
        >
          ←
        </button>
        <button
          onClick={() => scrollBySlide(1)}
          className="rounded-2xl px-4 py-3 bg-white/60 border border-black/5 shadow-glass"
        >
          →
        </button>
      </div>
    </section>
  );
}