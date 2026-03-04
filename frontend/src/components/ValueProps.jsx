// src/components/ValueProps.jsx
import { Compass, Sparkles, UsersRound } from "lucide-react";

export default function ValueProps() {
  const cards = [
    {
      icon: UsersRound,
      title: "Everyone answers. One trip happens.",
      text: "Collect preferences without group-chat chaos. The app resolves direction fast.",
    },
    {
      icon: Compass,
      title: "Balance budget, pace, and vibe.",
      text: "No one gets steamrolled. Plans align with your group's real constraints.",
    },
    {
      icon: Sparkles,
      title: "It feels curated, not generated.",
      text: "Believable timing, useful sequencing, and moments people actually enjoy.",
    },
  ];

  return (
    <section className="mx-auto max-w-6xl px-6 pb-16 md:pb-20">
      <div className="grid gap-5 md:grid-cols-3">
        {cards.map((c) => {
          const Icon = c.icon;
          return (
            <article key={c.title} className="liquid-panel rounded-[2rem] border border-white/20 p-7 md:p-8">
              <div className="inline-flex h-10 w-10 items-center justify-center rounded-2xl bg-white/14 text-[#f7e9d2]">
                <Icon className="h-5 w-5" />
              </div>
              <div className="mt-4 font-serif text-2xl leading-snug text-[#fff7ea]">{c.title}</div>
              <div className="mt-3 leading-relaxed text-[#ebdecc]/92">{c.text}</div>
              <div className="mt-6 h-[1px] w-full bg-white/12" />
              <div className="mt-5 text-sm text-[#e3d5bf]/86">Cinematic clarity over generic planning.</div>
            </article>
          );
        })}
      </div>
    </section>
  );
}

