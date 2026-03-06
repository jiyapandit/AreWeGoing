import axios from "axios";
import { Compass, Users } from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import Navbar from "../components/Navbar";

function getAccessToken() {
  return (
    window.localStorage.getItem("arewegoing_access_token") || window.sessionStorage.getItem("arewegoing_access_token")
  );
}

export default function DashboardHome() {
  const token = getAccessToken();
  const [myGroups, setMyGroups] = useState([]);
  const [loading, setLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");

  const rawApiBaseUrl = (import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000").replace(/\/$/, "");
  const groupsApiBaseUrl = useMemo(
    () => (rawApiBaseUrl.endsWith("/api/v1") ? `${rawApiBaseUrl}/groups` : `${rawApiBaseUrl}/api/v1/groups`),
    [rawApiBaseUrl]
  );

  useEffect(() => {
    let isMounted = true;
    async function loadGroups() {
      if (!token) return;
      setLoading(true);
      setErrorMessage("");
      try {
        const { data } = await axios.get(`${groupsApiBaseUrl}/my`, {
          headers: { Authorization: `Bearer ${token}` },
          timeout: 10000,
        });
        if (isMounted) setMyGroups(Array.isArray(data) ? data : []);
      } catch {
        if (isMounted) setErrorMessage("Could not load your trips. Please sign in again.");
      } finally {
        if (isMounted) setLoading(false);
      }
    }
    loadGroups();
    return () => {
      isMounted = false;
    };
  }, [groupsApiBaseUrl, token]);

  return (
    <div className="group-scene relative min-h-screen overflow-hidden text-[#f7f1e6]">
      <div className="group-bg-gradient-join absolute inset-0" />
      <div className="scene-photo-wash-dashboard absolute inset-0 opacity-36" />
      <div className="group-cinematic-vignette absolute inset-0" />
      <div className="group-orb-a absolute -left-24 top-10 h-[22rem] w-[22rem] rounded-full login-float-fast" />
      <div className="group-orb-b absolute -right-24 bottom-10 h-[24rem] w-[24rem] rounded-full login-float-slow" />
      <div className="absolute inset-0 grain" />

      <Navbar />
      <main className="relative z-10 mx-auto max-w-6xl px-6 pb-16 pt-6 md:pt-10">
        <section className="dashboard-section group-panel group-panel-dashboard rounded-[2rem] border border-[#efe4d0]/35 p-6 md:p-8">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div>
              <p className="text-xs uppercase tracking-[0.16em] text-[#f0e4d0]/85">Dashboard</p>
              <h1 className="mt-2 font-serif text-4xl leading-tight md:text-5xl">Your trips</h1>
              <p className="mt-2 text-sm text-[#e8dcc8]/90 md:text-base">
                Pick a trip to open full planning details, itinerary, votes, and host controls.
              </p>
            </div>
            <div className="flex gap-2">
              <Link
                to="/create-group"
                className="liquid-chip rounded-2xl border border-[#f3e7d4]/30 px-4 py-2 text-sm text-[#fff8eb]"
              >
                Create trip
              </Link>
              <Link
                to="/join-group"
                className="rounded-2xl border border-[#f3e7d4]/30 bg-[#11151c]/45 px-4 py-2 text-sm text-[#efe3d1] transition hover:bg-[#161d27]/60"
              >
                Join trip
              </Link>
            </div>
          </div>

          {errorMessage ? <p className="mt-4 text-sm text-[#ffcfc5]">{errorMessage}</p> : null}

          <div className="mt-6 grid gap-3 md:grid-cols-2 xl:grid-cols-3">
            {myGroups.map((group) => (
              <Link
                key={group.id}
                to={`/groups/${group.id}`}
                className="trip-card block"
              >
                <p className="text-xl text-[#fff7ea]">{group.name}</p>
                <p className="mt-1 text-xs uppercase tracking-[0.16em] text-[#e8dbc7]/75">
                  {group.role} / {group.status}
                </p>
                <p className="mt-2 text-sm text-[#e8dcc8]/85">Join code: {group.join_code}</p>
                <div className="mt-4 flex items-center gap-2 text-xs text-[#daccb6]/90">
                  <Users className="h-3.5 w-3.5" />
                  Open trip dashboard
                </div>
              </Link>
            ))}

            {!loading && myGroups.length === 0 ? (
              <div className="trip-card p-5">
                <div className="inline-flex items-center gap-2 text-[#fff7ea]">
                  <Compass className="h-4 w-4" />
                  <p>No trips yet</p>
                </div>
                <p className="mt-2 text-sm text-[#e8dcc8]/85">Create or join a group to start planning.</p>
              </div>
            ) : null}
          </div>
        </section>
      </main>
    </div>
  );
}
