// src/components/Footer.jsx
import logo from "../assets/Logo_extracted.png";

export default function Footer() {
  return (
    <footer className="pb-10">
      <div className="mx-auto max-w-6xl px-6">
        <div className="liquid-panel flex flex-col items-start justify-between gap-4 rounded-[2rem] border border-white/20 px-7 py-6 md:flex-row md:items-center">
          <div className="flex items-center gap-3 text-sm text-[#eadcc7]">
            <img src={logo} alt="AreWeGoing logo" className="h-8 w-8 rounded-xl bg-white/65 p-1 object-contain" />
            <span>© {new Date().getFullYear()} AreWeGoing</span>
          </div>
          <div className="flex gap-6 text-sm text-[#e2d3bc]">
            <a className="hover:text-[#fff7ea]" href="#privacy">
              Privacy
            </a>
            <a className="hover:text-[#fff7ea]" href="#terms">
              Terms
            </a>
            <a className="hover:text-[#fff7ea]" href="#contact">
              Contact
            </a>
          </div>
        </div>
      </div>
    </footer>
  );
}

