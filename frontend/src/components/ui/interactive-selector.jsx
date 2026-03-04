import { useEffect, useState } from "react";
import { FaCampground, FaFire, FaHiking, FaHotTub, FaTint } from "react-icons/fa";

const OPTIONS = [
  {
    title: "Luxury Tent",
    description: "Cozy glamping under the stars",
    image:
      "https://images.unsplash.com/photo-1506744038136-46273834b3fb?auto=format&fit=crop&w=1200&q=80",
    icon: <FaCampground size={24} className="text-white" />,
  },
  {
    title: "Campfire Feast",
    description: "Gourmet s'mores and stories",
    image:
      "https://images.unsplash.com/photo-1464983953574-0892a716854b?auto=format&fit=crop&w=1200&q=80",
    icon: <FaFire size={24} className="text-white" />,
  },
  {
    title: "Lakeside Retreat",
    description: "Private dock and canoe rides",
    image:
      "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=1200&q=80",
    icon: <FaTint size={24} className="text-white" />,
  },
  {
    title: "Mountain Spa",
    description: "Outdoor sauna and hot tub",
    image:
      "https://images.unsplash.com/photo-1502082553048-f009c37129b9?auto=format&fit=crop&w=1200&q=80",
    icon: <FaHotTub size={24} className="text-white" />,
  },
  {
    title: "Guided Adventure",
    description: "Expert-led nature tours",
    image:
      "https://images.unsplash.com/photo-1470770841072-f978cf4d019e?auto=format&fit=crop&w=1200&q=80",
    icon: <FaHiking size={24} className="text-white" />,
  },
];

export default function InteractiveSelector() {
  const [activeIndex, setActiveIndex] = useState(0);
  const [animatedOptions, setAnimatedOptions] = useState([]);

  useEffect(() => {
    const timers = [];
    OPTIONS.forEach((_, i) => {
      const timer = setTimeout(() => {
        setAnimatedOptions((prev) => [...prev, i]);
      }, 180 * i);
      timers.push(timer);
    });
    return () => timers.forEach((timer) => clearTimeout(timer));
  }, []);

  return (
    <div className="relative flex flex-col items-center justify-center font-sans text-white">
      <div className="mb-8 w-full max-w-2xl px-2 text-center">
        <h3 className="animate-fadeInTop delay-300 mb-2 text-3xl font-extrabold tracking-tight text-white md:text-4xl">
          Escape in Style
        </h3>
        <p className="animate-fadeInTop delay-600 mx-auto max-w-xl text-base font-medium text-gray-300 md:text-lg">
          Discover luxurious travel experiences in nature&apos;s most breathtaking spots.
        </p>
      </div>

      <div className="options relative flex h-[380px] w-full max-w-[980px] min-w-0 items-stretch overflow-hidden rounded-[1.4rem] border border-white/10 bg-[#181a1f]/55">
        {OPTIONS.map((option, index) => (
          <button
            key={option.title}
            className={`option relative flex min-h-[100px] min-w-[52px] flex-1 cursor-pointer flex-col justify-end overflow-hidden border-2 border-[#292929] bg-[#18181b] transition-all duration-700 ease-in-out ${
              activeIndex === index ? "z-10" : "z-[1]"
            }`}
            style={{
              backgroundImage: `url('${option.image}')`,
              backgroundSize: activeIndex === index ? "auto 100%" : "auto 120%",
              backgroundPosition: "center",
              opacity: animatedOptions.includes(index) ? 1 : 0,
              transform: animatedOptions.includes(index) ? "translateX(0)" : "translateX(-60px)",
              borderColor: activeIndex === index ? "#fff" : "#292929",
              boxShadow:
                activeIndex === index
                  ? "0 20px 60px rgba(0,0,0,0.50)"
                  : "0 10px 30px rgba(0,0,0,0.30)",
              flex: activeIndex === index ? "7 1 0%" : "1 1 0%",
              willChange: "flex-grow, box-shadow, background-size",
            }}
            onClick={() => setActiveIndex(index)}
            type="button"
            aria-label={option.title}
          >
            <div
              className="shadow pointer-events-none absolute left-0 right-0 transition-all duration-700 ease-in-out"
              style={{
                bottom: activeIndex === index ? "0" : "-40px",
                height: "120px",
                boxShadow:
                  activeIndex === index
                    ? "inset 0 -120px 120px -120px #000, inset 0 -120px 120px -80px #000"
                    : "inset 0 -120px 0 -120px #000, inset 0 -120px 0 -80px #000",
              }}
            />

            <div className="label pointer-events-none absolute bottom-4 left-0 right-0 z-[2] flex h-12 w-full items-center justify-start gap-3 px-3 md:px-4">
              <div className="icon flex h-[44px] w-[44px] flex-shrink-0 items-center justify-center rounded-full border-2 border-[#444] bg-[rgba(32,32,32,0.85)] shadow-[0_1px_4px_rgba(0,0,0,0.18)] backdrop-blur-[10px]">
                {option.icon}
              </div>
              <div className="info relative whitespace-pre text-white">
                <div
                  className="main text-base font-bold transition-all duration-700 ease-in-out md:text-lg"
                  style={{
                    opacity: activeIndex === index ? 1 : 0,
                    transform: activeIndex === index ? "translateX(0)" : "translateX(25px)",
                  }}
                >
                  {option.title}
                </div>
                <div
                  className="sub text-sm text-gray-300 transition-all duration-700 ease-in-out md:text-base"
                  style={{
                    opacity: activeIndex === index ? 1 : 0,
                    transform: activeIndex === index ? "translateX(0)" : "translateX(25px)",
                  }}
                >
                  {option.description}
                </div>
              </div>
            </div>
          </button>
        ))}
      </div>

      <style>{`
        @keyframes fadeInFromTop {
          0% {
            opacity: 0;
            transform: translateY(-20px);
          }
          100% {
            opacity: 1;
            transform: translateY(0);
          }
        }
        .animate-fadeInTop {
          opacity: 0;
          transform: translateY(-20px);
          animation: fadeInFromTop 0.8s ease-in-out forwards;
        }
        .delay-300 {
          animation-delay: 0.3s;
        }
        .delay-600 {
          animation-delay: 0.6s;
        }
      `}</style>
    </div>
  );
}

