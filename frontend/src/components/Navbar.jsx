// src/components/Navbar.jsx
import { Link } from "react-router-dom";
import logo from "../assets/Logo_extracted.png";

export default function Navbar() {
  return (
    <header className="sticky top-0 z-50">
      <div className="mx-auto max-w-6xl px-6 py-4">
        <div className="liquid-nav rounded-3xl px-1">
          <div className="flex items-center justify-between px-5 py-3">
            <div className="flex items-center gap-3">
              <div className="h-10 w-10 overflow-hidden rounded-2xl bg-white/75 p-1.5">
                <img src={logo} alt="AreWeGoing logo" className="h-full w-full object-contain" />
              </div>
              <div className="leading-tight">
                <div className="font-serif text-lg text-[#fff7ea]">AreWeGoing</div>
                <div className="text-xs text-[#e8dcca]/85">cinematic group travel</div>
              </div>
            </div>

            <nav className="hidden md:flex items-center gap-7 text-sm text-[#e8ddcc]/85">
              <a href="#how" className="hover:text-[#fff7ea]">
                How it works
              </a>
              <a href="#destinations" className="hover:text-[#fff7ea]">
                Destinations
              </a>
              <a href="#sample" className="hover:text-[#fff7ea]">
                Sample trip
              </a>
              <Link to="/login" className="login-text-link hover:text-[#fff7ea]">
                Sign in
              </Link>
            </nav>

            <div className="flex items-center gap-2">
              <Link
                to="/signup"
                className="liquid-chip hidden md:inline-flex rounded-2xl px-4 py-2 text-sm text-[#fff7ea]"
              >
                Create account
              </Link>
              <button className="liquid-chip md:hidden rounded-2xl px-3 py-2 text-[#fff7ea]" type="button">
                Menu
              </button>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
}

