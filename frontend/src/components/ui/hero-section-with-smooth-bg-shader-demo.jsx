import { HeroSection } from "@/components/ui/hero-section-with-smooth-bg-shader";

export default function HeroShaderDemo() {
  return <HeroSection distortion={1.2} speed={0.8} className="min-h-[70vh]" />;
}
