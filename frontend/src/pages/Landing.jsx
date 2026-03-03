import Navbar from "../components/Navbar";
import Hero from "../components/Hero";
import DestinationsCarousel from "../components/DestinationsCarousel";
import ValueProps from "../components/ValueProps";
import HowItWorks from "../components/HowItWorks";
import SampleTrip from "../components/Sampletrip";
import Footer from "../components/Footer";

export default function Landing() {
  return (
    <div className="min-h-screen bg-[#F5F2ED] text-[#141414]">
      <Navbar />
      <main>
        <Hero />
        <DestinationsCarousel />
        <ValueProps />
        <HowItWorks />
        <SampleTrip />
      </main>
      <Footer />
    </div>
  );
}