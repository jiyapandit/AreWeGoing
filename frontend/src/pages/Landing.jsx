import Navbar from "../components/Navbar";
import DestinationsCarousel from "../components/DestinationsCarousel";
import ValueProps from "../components/ValueProps";
import HowItWorks from "../components/HowItWorks";
import SampleTrip from "../components/SampleTrip";
import Footer from "../components/Footer";
import ScrollExpansionHero from "../components/ui/scroll-expansion-hero";
import { Link } from "react-router-dom";

export default function Landing() {
  return (
    <div className="landing-shell min-h-screen text-[#f7f2e9]">
      <div className="landing-overlay fixed inset-0 -z-10" />
      <Navbar />
      <main>
        <ScrollExpansionHero
          mediaType="image"
          mediaSrc="https://images.unsplash.com/photo-1476514525535-07fb3b4ae5f1?auto=format&fit=crop&w=2200&q=80"
          bgImageSrc="https://images.unsplash.com/photo-1469474968028-56623f02e42e?auto=format&fit=crop&w=2600&q=80"
          title="AreWeGoing Cinematic Travel"
          date="Group planning, elevated"
          scrollToExpand="Scroll to reveal your route"
          textBlend
        >
          <div className="mx-auto max-w-4xl">
            <div className="liquid-panel rounded-[2rem] border border-white/20 p-7 md:p-10">
              <h2 className="font-serif text-3xl text-[#fff7ea] md:text-5xl">Plan once. Travel together.</h2>
              <p className="mt-4 max-w-2xl text-[#eadeca]/92">
                Build a trip that reflects everyoneâ€™s preferences while preserving pace, budget, and mood.
              </p>
              <div className="mt-8 flex flex-wrap gap-3">
                <Link to="/signup" className="liquid-chip rounded-2xl border border-white/20 px-5 py-3 text-[#fff8eb]">
                  Create account
                </Link>
                <Link to="/login" className="liquid-chip rounded-2xl border border-white/20 px-5 py-3 text-[#efe3d1]">
                  Sign in
                </Link>
              </div>
            </div>
          </div>
        </ScrollExpansionHero>
        <DestinationsCarousel />
        <ValueProps />
        <HowItWorks />
        <SampleTrip />
      </main>
      <Footer />
    </div>
  );
}

