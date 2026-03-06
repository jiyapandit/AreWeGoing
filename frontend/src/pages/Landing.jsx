import axios from "axios";
import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import Navbar from "../components/Navbar";
import DestinationsCarousel from "../components/DestinationsCarousel";
import ValueProps from "../components/ValueProps";
import HowItWorks from "../components/HowItWorks";
import SampleTrip from "../components/SampleTrip";
import Footer from "../components/Footer";
import ScrollExpansionHero from "../components/ui/scroll-expansion-hero";

export default function Landing() {
  const [myGroups, setMyGroups] = useState([]);
  const [myGroupsError, setMyGroupsError] = useState("");

  const token =
    window.localStorage.getItem("arewegoing_access_token") || window.sessionStorage.getItem("arewegoing_access_token");
  const rawApiBaseUrl = (import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000").replace(/\/$/, "");
  const groupsApiBaseUrl = useMemo(
    () => (rawApiBaseUrl.endsWith("/api/v1") ? `${rawApiBaseUrl}/groups` : `${rawApiBaseUrl}/api/v1/groups`),
    [rawApiBaseUrl]
  );

  useEffect(() => {
    let isMounted = true;
    async function loadGroups() {
      if (!token) return;
      try {
        const { data } = await axios.get(`${groupsApiBaseUrl}/my`, {
          headers: { Authorization: `Bearer ${token}` },
          timeout: 10000,
        });
        if (isMounted) setMyGroups(Array.isArray(data) ? data : []);
      } catch {
        if (isMounted) setMyGroupsError("Sign in again to load your dashboard groups.");
      }
    }
    loadGroups();
    return () => {
      isMounted = false;
    };
  }, [groupsApiBaseUrl, token]);

  const latestGroup = myGroups.length > 0 ? myGroups[0] : null;

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
              <p className="mt-4 max-w-2xl text-[#f1e7d7]">
                Build a trip that reflects everyone&apos;s preferences while preserving pace, budget, and mood.
              </p>
              <div className="mt-8 flex flex-wrap gap-3">
                {token ? (
                  <>
                    <Link
                      to="/dashboard"
                      className="liquid-chip rounded-2xl border border-white/20 px-5 py-3 text-[#fff8eb]"
                    >
                      Open dashboard
                    </Link>
                    <Link
                      to="/create-group"
                      className="rounded-2xl border border-white/30 bg-white/10 px-5 py-3 text-[#f1e7d7] transition hover:bg-white/20"
                    >
                      Create group
                    </Link>
                    <Link
                      to="/join-group"
                      className="rounded-2xl border border-white/30 bg-white/10 px-5 py-3 text-[#f1e7d7] transition hover:bg-white/20"
                    >
                      Join group
                    </Link>
                  </>
                ) : (
                  <>
                    <Link to="/signup" className="liquid-chip rounded-2xl border border-white/20 px-5 py-3 text-[#fff8eb]">
                      Create account
                    </Link>
                    <Link
                      to="/login"
                      className="rounded-2xl border border-white/30 bg-white/10 px-5 py-3 text-[#f1e7d7] transition hover:bg-white/20"
                    >
                      Sign in
                    </Link>
                  </>
                )}
              </div>
            </div>
          </div>
        </ScrollExpansionHero>

        <section className="mx-auto max-w-6xl px-6 py-10">
          <div className="kinetic-banner p-6 md:p-8">
            <div className="flex flex-wrap items-center justify-between gap-3">
              <div>
                <h3 className="font-serif text-3xl text-[#fff7ea] md:text-4xl">Dashboard & Planning Features</h3>
                <p className="mt-2 text-sm text-[#f1e7d7] md:text-base">
                  Everything from preferences to locking the final itinerary now lives in one group dashboard.
                </p>
              </div>
              {latestGroup ? (
                <Link
                  to="/dashboard"
                  className="liquid-chip rounded-2xl border border-white/20 px-4 py-2 text-[#fff8eb]"
                >
                  Continue: {latestGroup.name} and others
                </Link>
              ) : token ? (
                <Link to="/create-group" className="liquid-chip rounded-2xl border border-white/20 px-4 py-2 text-[#fff8eb]">
                  Create your first group
                </Link>
              ) : (
                <Link to="/login" className="liquid-chip rounded-2xl border border-white/20 px-4 py-2 text-[#fff8eb]">
                  Sign in to access dashboard
                </Link>
              )}
            </div>

            <div className="mt-6 grid gap-3 md:grid-cols-2 xl:grid-cols-3">
              {[
                ["Preferences Questionnaire", "Submit destination, budget, days, transport, pace, activities."],
                ["Alignment Metrics", "See completion %, budget alignment, activity match, and conflicts."],
                ["Itinerary Engine", "Generate day-by-day plan with rationale and confidence score."],
                ["Voting & Review", "Move itinerary to review and collect member votes."],
              ].map(([title, description]) => (
                <div key={title} className="feature-grid-card">
                  <p className="text-lg text-[#fff7ea]">{title}</p>
                  <p className="mt-1 text-sm text-[#f1e7d7]">{description}</p>
                </div>
              ))}
            </div>

            {myGroupsError ? <p className="mt-4 text-sm text-[#ffcfbf]">{myGroupsError}</p> : null}
          </div>
        </section>

        <DestinationsCarousel />
        <ValueProps />
        <HowItWorks />
        <SampleTrip />
      </main>
      <Footer />
    </div>
  );
}
