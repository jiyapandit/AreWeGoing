import { MeshGradient } from "@paper-design/shaders-react";
import { useEffect, useState } from "react";

export function HeroSection({
  title = "Discover destinations with",
  highlightText = "your people",
  description = "",
  buttonText = "Start planning",
  onButtonClick,
  colors = ["#1a2f38", "#274a58", "#486f7a", "#8e7b67", "#b69472", "#564c5b"],
  distortion = 0.34,
  swirl = 0.22,
  speed = 0.18,
  offsetX = 0.08,
  photoSrc = "https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?auto=format&fit=crop&w=2400&q=80",
  photoPosition = "center 38%",
  photoScale = 1.1,
  className = "",
  titleClassName = "",
  descriptionClassName = "",
  buttonClassName = "",
  maxWidth = "max-w-6xl",
  veilOpacity = "bg-black/16",
  fontFamily = "Satoshi, sans-serif",
  fontWeight = 500,
}) {
  const [dimensions, setDimensions] = useState(() => {
    if (typeof window !== "undefined") {
      return { width: window.innerWidth, height: window.innerHeight };
    }
    return { width: 1920, height: 1080 };
  });
  const [scrollY, setScrollY] = useState(0);
  const [prefersReducedMotion, setPrefersReducedMotion] = useState(false);

  useEffect(() => {
    const update = () =>
      setDimensions({
        width: window.innerWidth,
        height: window.innerHeight,
      });
    const media = window.matchMedia("(prefers-reduced-motion: reduce)");
    setPrefersReducedMotion(media.matches);

    const onMediaChange = (event) => setPrefersReducedMotion(event.matches);
    const onScroll = () => {
      setScrollY(window.scrollY || 0);
    };

    window.addEventListener("resize", update);
    window.addEventListener("scroll", onScroll, { passive: true });
    media.addEventListener("change", onMediaChange);
    return () => {
      window.removeEventListener("resize", update);
      window.removeEventListener("scroll", onScroll);
      media.removeEventListener("change", onMediaChange);
    };
  }, []);

  const handleButtonClick = () => {
    if (onButtonClick) {
      onButtonClick();
    }
  };

  const photoTranslateY = prefersReducedMotion ? 0 : Math.min(scrollY * 0.05, 30);
  const meshTranslateY = prefersReducedMotion ? 0 : Math.min(scrollY * 0.02, 14);

  return (
    <section
      className={`relative flex min-h-screen w-full items-center justify-center overflow-hidden bg-background ${className}`}
    >
      <div className="fixed inset-0 h-screen w-screen">
        {typeof window !== "undefined" && (
          <>
            <div
              className="absolute inset-0"
              style={{ transform: `translate3d(0, ${meshTranslateY}px, 0)` }}
            >
              <MeshGradient
                width={dimensions.width}
                height={dimensions.height}
                colors={colors}
                distortion={distortion}
                swirl={swirl}
                grainMixer={0}
                grainOverlay={0}
                speed={speed}
                offsetX={offsetX}
              />
            </div>
            <img
              src={photoSrc}
              alt="Travel destination landscape"
              className="absolute inset-0 h-full w-full object-cover opacity-64 mix-blend-soft-light"
              style={{
                objectPosition: photoPosition,
                transform: `translate3d(0, ${photoTranslateY}px, 0) scale(${photoScale})`,
                filter: "saturate(108%) contrast(104%)",
              }}
            />
            <div className="pointer-events-none absolute inset-0 bg-gradient-to-b from-slate-950/20 via-slate-900/8 to-black/30" />
            <div className={`pointer-events-none absolute inset-0 ${veilOpacity}`} />
          </>
        )}
      </div>

      <div className={`relative z-10 mx-auto w-full px-6 ${maxWidth}`}>
        <div className="relative mx-auto max-w-4xl overflow-hidden rounded-[2rem] border border-white/30 bg-white/12 p-8 text-center shadow-[0_20px_80px_rgba(15,23,42,0.25)] backdrop-blur-2xl sm:p-10 md:p-12">
          <div className="pointer-events-none absolute -left-16 -top-16 h-48 w-48 rounded-full bg-white/25 blur-3xl" />
          <div className="pointer-events-none absolute -bottom-20 -right-10 h-56 w-56 rounded-full bg-sky-200/20 blur-3xl" />
          <div className="pointer-events-none absolute inset-0 rounded-[2rem] bg-gradient-to-br from-white/22 via-white/8 to-transparent" />
          <div className="pointer-events-none absolute inset-[1px] rounded-[calc(2rem-1px)] border border-white/22" />
          <div className="relative z-10">
          <h1
            className={`mb-6 text-balance text-4xl font-bold leading-tight text-white drop-shadow-[0_8px_24px_rgba(0,0,0,0.35)] sm:text-5xl sm:leading-tight md:text-6xl md:leading-tight lg:text-7xl lg:leading-tight xl:text-[80px] xl:leading-[1.1] ${titleClassName}`}
            style={{ fontFamily, fontWeight }}
          >
            {title} <span className="text-[#f3c98b] drop-shadow-[0_4px_14px_rgba(33,18,8,0.45)]">{highlightText}</span>
          </h1>
          {description ? (
            <p
              className={`mx-auto mb-10 max-w-2xl px-4 text-pretty text-lg leading-relaxed text-white sm:text-xl ${descriptionClassName}`}
            >
              {description}
            </p>
          ) : null}
          <button
            onClick={handleButtonClick}
            className={`rounded-full border border-white/45 bg-white/22 px-6 py-4 text-sm text-slate-900 shadow-[0_8px_30px_rgba(15,23,42,0.18)] backdrop-blur-lg transition-all hover:bg-white/30 hover:shadow-[0_12px_36px_rgba(15,23,42,0.2)] sm:px-8 sm:py-6 sm:text-base ${buttonClassName}`}
          >
            {buttonText}
          </button>
          </div>
        </div>
      </div>
    </section>
  );
}
