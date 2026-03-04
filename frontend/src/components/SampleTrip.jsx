import InteractiveSelector from "./ui/interactive-selector";

export default function SampleTrip() {
  return (
    <section id="sample" className="mx-auto max-w-6xl px-6 pb-20">
      <div>
        <h2 className="font-serif text-4xl leading-tight text-[#fff6e8] md:text-5xl">Sample trip selector</h2>
        <p className="mt-3 max-w-xl text-[#eadcc8]/90">
          Explore interactive trip styles and pick the experience that matches your group.
        </p>
      </div>

      <div className="liquid-panel mt-10 rounded-[2rem] border border-white/20 p-4 md:p-7">
        <InteractiveSelector />
      </div>
    </section>
  );
}

