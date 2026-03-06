import axios from "axios";
import { CheckCircle2, Compass, Home, Mail, Users } from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import Navbar from "../components/Navbar";
import AppToast from "@/components/ui/app-toast";

function getAccessToken() {
  return (
    window.localStorage.getItem("arewegoing_access_token") || window.sessionStorage.getItem("arewegoing_access_token")
  );
}

export default function DashboardHome() {
  const navigate = useNavigate();
  const token = getAccessToken();
  const [myGroups, setMyGroups] = useState([]);
  const [myInvites, setMyInvites] = useState([]);
  const [loading, setLoading] = useState(false);
  const [acceptingInviteId, setAcceptingInviteId] = useState(null);
  const [toast, setToast] = useState({ message: "", type: "info" });

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
      setToast({ message: "", type: "info" });
      try {
        const [groupsRes, invitesRes] = await Promise.all([
          axios.get(`${groupsApiBaseUrl}/my`, {
            headers: { Authorization: `Bearer ${token}` },
            timeout: 10000,
          }),
          axios.get(`${groupsApiBaseUrl}/invites/me`, {
            headers: { Authorization: `Bearer ${token}` },
            timeout: 10000,
          }),
        ]);
        if (isMounted) {
          setMyGroups(Array.isArray(groupsRes.data) ? groupsRes.data : []);
          setMyInvites(Array.isArray(invitesRes.data) ? invitesRes.data : []);
        }
      } catch {
        if (isMounted) setToast({ message: "Could not load your dashboard data. Please sign in again.", type: "error" });
      } finally {
        if (isMounted) setLoading(false);
      }
    }
    loadGroups();
    return () => {
      isMounted = false;
    };
  }, [groupsApiBaseUrl, token]);

  async function acceptInvite(inviteId) {
    setToast({ message: "", type: "info" });
    setAcceptingInviteId(inviteId);
    try {
      const { data } = await axios.post(
        `${groupsApiBaseUrl}/invites/${inviteId}/accept`,
        {},
        { headers: { Authorization: `Bearer ${token}` }, timeout: 10000 }
      );
      setMyInvites((prev) => prev.filter((invite) => invite.id !== inviteId));
      setToast({ message: "Invite accepted. Opening group dashboard...", type: "success" });
      navigate(`/groups/${data.group_id}`);
    } catch (error) {
      if (error?.response?.status === 403) {
        setToast({ message: "This invite does not belong to your account.", type: "error" });
      } else if (error?.response?.status === 404) {
        setToast({ message: "Invite was not found.", type: "error" });
      } else if (error?.response?.status === 409) {
        setToast({ message: "Invite is no longer active.", type: "error" });
      } else {
        setToast({ message: "Could not accept invite right now.", type: "error" });
      }
    } finally {
      setAcceptingInviteId(null);
    }
  }

  return (
    <div className="group-scene relative min-h-screen overflow-hidden text-[#f7f1e6]">
      <AppToast
        message={toast.message}
        type={toast.type}
        onClose={() => setToast({ message: "", type: "info" })}
      />
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
            <nav aria-label="Dashboard quick actions" className="flex flex-wrap gap-2">
              <Link
                to="/landing"
                className="rounded-2xl border border-white/30 bg-white/10 px-4 py-2 text-sm text-[#efe3d1] transition hover:bg-white/20"
              >
                <span className="inline-flex items-center gap-2">
                  <Home className="h-4 w-4" />
                  Landing
                </span>
              </Link>
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
            </nav>
          </div>

          <div className="mt-6">
            <div className="mb-3 flex items-center gap-2 text-[#f0e4d0]">
              <Mail className="h-4 w-4" />
              <p className="text-xs uppercase tracking-[0.16em]">Pending invites</p>
            </div>
            <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-3">
              {loading
                ? Array.from({ length: 2 }).map((_, index) => (
                    <div key={`invite-skeleton-${index}`} className="skeleton-card">
                      <div className="skeleton-block h-5 w-2/3" />
                      <div className="mt-2 skeleton-block h-4 w-1/2" />
                      <div className="mt-4 skeleton-block h-4 w-1/3" />
                    </div>
                  ))
                : null}
              {!loading && myInvites.length === 0 ? (
                <div className="trip-card p-4">
                  <p className="text-sm text-[#e8dcc8]/90">No pending invites.</p>
                </div>
              ) : null}
              {myInvites.slice(0, 6).map((invite) => (
                <div key={invite.id} className="trip-card p-4">
                  <p className="text-lg text-[#fff7ea]">{invite.group_name}</p>
                  <p className="mt-1 text-xs uppercase tracking-[0.15em] text-[#e8dbc7]/80">{invite.join_code}</p>
                  <p className="mt-2 text-sm text-[#e8dcc8]/85">Invited as {invite.email}</p>
                  <button
                    type="button"
                    disabled={acceptingInviteId === invite.id}
                    onClick={() => acceptInvite(invite.id)}
                    className="mt-3 liquid-chip rounded-xl border border-[#f3e7d4]/30 px-3 py-2 text-sm text-[#fff8eb] disabled:cursor-not-allowed disabled:opacity-70"
                  >
                    <span className="inline-flex items-center gap-2">
                      <CheckCircle2 className="h-4 w-4" />
                      {acceptingInviteId === invite.id ? "Accepting..." : "Accept invite"}
                    </span>
                  </button>
                </div>
              ))}
            </div>
          </div>

          <div className="mt-6 grid gap-3 md:grid-cols-2 xl:grid-cols-3">
            {loading && myGroups.length === 0
              ? Array.from({ length: 3 }).map((_, index) => (
                  <div key={`trip-skeleton-${index}`} className="skeleton-card">
                    <div className="skeleton-block h-6 w-2/3" />
                    <div className="mt-2 skeleton-block h-4 w-1/3" />
                    <div className="mt-4 skeleton-block h-4 w-1/2" />
                    <div className="mt-6 skeleton-block h-4 w-2/3" />
                  </div>
                ))
              : null}
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
