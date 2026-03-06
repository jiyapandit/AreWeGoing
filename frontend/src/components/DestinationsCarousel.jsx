// src/components/DestinationsCarousel.jsx
import { ChevronLeft, ChevronRight } from "lucide-react";
import { useMemo, useRef } from "react";

function Slide({ title, mood, image }) {
  return (
    <div className="snap-center shrink-0 w-[86%] md:w-[58%] lg:w-[42%]">
      <div className="relative h-[420px] overflow-hidden rounded-[2rem] md:h-[520px]">
        <img src={image} alt={title} className="absolute inset-0 h-full w-full object-cover" loading="lazy" />
        <div className="absolute inset-0 bg-gradient-to-t from-black/62 via-black/20 to-transparent" />
        <div className="absolute bottom-6 left-6 right-6">
          <div className="liquid-panel rounded-2xl border border-white/20 px-4 py-3">
            <div className="font-serif text-2xl leading-tight text-[#fff7ec]">{title}</div>
            <div className="text-sm text-[#eedfca]/88">{mood}</div>
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
        mood: "salt air • lemon streets • late sun",
        image:
          "https://images.unsplash.com/photo-1612698093158-e07ac200d44e?auto=format&fit=crop&w=2200&q=80",
      },
      {
        title: "Kyoto",
        mood: "mist alleys • tea houses • calm mornings",
        image:
          "https://images.unsplash.com/photo-1545569341-9eb8b30979d9?auto=format&fit=crop&w=2200&q=80",
      },
      {
        title: "Istanbul",
        mood: "bazaars • skyline dusk • ferry breeze",
        image:
          "https://images.unsplash.com/photo-1524231757912-21f4fe3a7200?auto=format&fit=crop&w=2200&q=80",
      },
      {
        title: "Banff",
        mood: "glacial lakes • pine silence • mountain light",
        image:
          "https://images.unsplash.com/photo-1506461883276-594a12b11cf3?auto=format&fit=crop&w=2200&q=80",
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
          <h2 className="font-serif text-4xl leading-tight text-[#fff6e8] md:text-5xl">
            Destinations with a pulse.
          </h2>
          <p className="mt-3 max-w-xl text-[#eadcc8]/90">
            Browse real travel photos and lock in the tone before planning details.
          </p>
        </div>
        <div className="hidden gap-2 md:flex">
          <button
            onClick={() => scrollBySlide(-1)}
            className="liquid-chip rounded-2xl border border-white/20 px-4 py-3 text-[#fff4e4]"
            type="button"
            aria-label="Previous destinations"
          >
            <ChevronLeft className="h-5 w-5" />
          </button>
          <button
            onClick={() => scrollBySlide(1)}
            className="liquid-chip rounded-2xl border border-white/20 px-4 py-3 text-[#fff4e4]"
            type="button"
            aria-label="Next destinations"
          >
            <ChevronRight className="h-5 w-5" />
          </button>
        </div>
      </div>

      <div
        ref={carouselRef}
        className="no-scrollbar mt-10 flex snap-x snap-mandatory gap-5 overflow-x-auto scroll-px-6 pb-2"
      >
        <div className="w-[2px] shrink-0" />
        {slides.map((s) => (
          <Slide key={s.title} title={s.title} mood={s.mood} image={s.image} />
        ))}
        <div className="w-[2px] shrink-0" />
      </div>

      <div className="mt-6 flex justify-center gap-2 md:hidden">
        <button
          onClick={() => scrollBySlide(-1)}
          className="liquid-chip rounded-2xl border border-white/20 px-4 py-3 text-[#fff4e4]"
          type="button"
          aria-label="Previous destinations"
        >
          <ChevronLeft className="h-5 w-5" />
        </button>
        <button
          onClick={() => scrollBySlide(1)}
          className="liquid-chip rounded-2xl border border-white/20 px-4 py-3 text-[#fff4e4]"
          type="button"
          aria-label="Next destinations"
        >
          <ChevronRight className="h-5 w-5" />
        </button>
      </div>
    </section>
  );
}

