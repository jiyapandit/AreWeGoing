import axios from "axios";
import { KeyRound, Users } from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import Navbar from "../components/Navbar";

function getAccessToken() {
  return (
    window.localStorage.getItem("arewegoing_access_token") || window.sessionStorage.getItem("arewegoing_access_token")
  );
}

export default function JoinGroup() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [joinCode, setJoinCode] = useState(searchParams.get("code")?.toUpperCase() || "");
  const [publicGroups, setPublicGroups] = useState([]);
  const [loadingPublic, setLoadingPublic] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");
  const [successMessage, setSuccessMessage] = useState("");

  const authToken = getAccessToken();
  const rawApiBaseUrl = (import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000").replace(/\/$/, "");
  const groupsApiBaseUrl = useMemo(
    () => (rawApiBaseUrl.endsWith("/api/v1") ? `${rawApiBaseUrl}/groups` : `${rawApiBaseUrl}/api/v1/groups`),
    [rawApiBaseUrl]
  );

  useEffect(() => {
    let isMounted = true;
    async function loadPublicGroups() {
      setLoadingPublic(true);
      try {
        const { data } = await axios.get(`${groupsApiBaseUrl}/public`, { timeout: 10000 });
        if (isMounted) setPublicGroups(Array.isArray(data) ? data : []);
      } catch {
        if (isMounted) setPublicGroups([]);
      } finally {
        if (isMounted) setLoadingPublic(false);
      }
    }
    loadPublicGroups();
    return () => {
      isMounted = false;
    };
  }, [groupsApiBaseUrl]);

  async function handleSubmit(e) {
    e.preventDefault();
    setErrorMessage("");
    setSuccessMessage("");

    if (!authToken) {
      setErrorMessage("Please sign in first to join a group.");
      return;
    }

    setIsSubmitting(true);
    try {
      const { data } = await axios.post(
        `${groupsApiBaseUrl}/join`,
        { join_code: joinCode.trim() },
        { headers: { Authorization: `Bearer ${authToken}` }, timeout: 10000 }
      );
      setSuccessMessage(`Joined "${data?.name || "group"}" successfully.`);
      navigate(`/groups/${data?.id}`);
    } catch (error) {
      if (error?.response?.status === 404) {
        setErrorMessage("Group not found. Check your code.");
      } else if (error?.response?.status === 409) {
        setErrorMessage("You are already a member of this group.");
      } else if (error?.response?.status === 401) {
        setErrorMessage("Session expired. Please sign in again.");
      } else {
        setErrorMessage("Could not join group right now.");
      }
    } finally {
      setIsSubmitting(false);
    }
  }

  async function requestToJoin(groupId, groupName) {
    setErrorMessage("");
    setSuccessMessage("");
    if (!authToken) {
      setErrorMessage("Please sign in first to send a join request.");
      return;
    }
    try {
      await axios.post(`${groupsApiBaseUrl}/${groupId}/join-request`, {}, { headers: { Authorization: `Bearer ${authToken}` } });
      setSuccessMessage(`Join request sent for "${groupName}". Waiting for host approval.`);
    } catch (error) {
      if (error?.response?.status === 409) {
        setErrorMessage("You have already requested or joined this group.");
      } else if (error?.response?.status === 400) {
        setErrorMessage("This group is not open for public requests.");
      } else if (error?.response?.status === 401) {
        setErrorMessage("Session expired. Please sign in again.");
      } else {
        setErrorMessage("Could not send join request.");
      }
    }
  }

  return (
    <div className="group-scene relative min-h-screen overflow-hidden text-[#f7f1e6]">
      <div className="group-bg-gradient-join absolute inset-0" />
      <div className="scene-photo-wash-join absolute inset-0 opacity-43" />
      <div className="group-cinematic-vignette absolute inset-0" />
      <div className="group-orb-a absolute -left-24 top-16 h-[24rem] w-[24rem] rounded-full login-float-fast" />
      <div className="group-orb-b absolute -right-24 bottom-10 h-[25rem] w-[25rem] rounded-full login-float-slow" />
      <div className="absolute inset-0 grain" />

      <Navbar />

      <main className="relative z-10 mx-auto max-w-5xl px-6 pb-16 pt-6 md:pt-10">
        <section className="group-panel group-panel-join relative mx-auto w-full max-w-3xl overflow-hidden rounded-[2rem] border border-white/30 p-6 shadow-[0_20px_70px_rgba(15,23,42,0.28)] md:p-9">
          <div className="pointer-events-none absolute -left-16 -top-16 h-44 w-44 rounded-full bg-white/20 blur-3xl" />
          <div className="pointer-events-none absolute -bottom-20 -right-10 h-52 w-52 rounded-full bg-sky-200/15 blur-3xl" />
          <div className="pointer-events-none absolute inset-0 bg-gradient-to-br from-white/16 via-white/6 to-transparent" />
          <div className="relative z-10">
          <div className="inline-flex items-center gap-2 rounded-full border border-[#efe4d0]/35 bg-black/20 px-3 py-1 text-xs uppercase tracking-[0.16em] text-[#f4ebda]/90">
            <Users className="h-3.5 w-3.5" />
            Join your crew
          </div>
          <h1 className="mt-5 font-serif text-4xl leading-tight md:text-5xl">Join an existing group</h1>
          <p className="mt-3 max-w-xl text-sm text-[#f1e7d7] md:text-base">
            Enter a code or pick a public group to join instantly.
          </p>

          <form onSubmit={handleSubmit} className="mt-8 space-y-5">
            <label className="block">
              <span className="text-xs uppercase tracking-[0.18em] text-[#f1e7d7]/90">Invite code</span>
              <div className="mt-2 flex items-center gap-2 rounded-2xl border border-white/30 bg-white/10 px-3 py-1">
                <KeyRound className="h-4 w-4 shrink-0 text-[#ecdfcc]/85" />
                <input
                  value={joinCode}
                  onChange={(e) => setJoinCode(e.target.value.toUpperCase())}
                  placeholder="e.g., NF4QVX0A"
                  className="w-full bg-transparent px-1 py-2 text-[#f8f2e7] uppercase tracking-[0.2em] outline-none placeholder:tracking-normal"
                  required
                />
              </div>
            </label>

            <div className="flex flex-wrap gap-3 pt-2">
              <button
                type="submit"
                disabled={isSubmitting}
                className="liquid-chip rounded-2xl border border-[#f3e7d4]/30 px-5 py-3 text-sm text-[#fff8eb] disabled:cursor-not-allowed disabled:opacity-70 md:text-base"
              >
                {isSubmitting ? "Joining..." : "Join Group"}
              </button>
              <button
                type="button"
                onClick={() => navigate("/landing")}
                className="rounded-2xl border border-white/30 bg-white/10 px-5 py-3 text-sm text-[#efe3d1] transition hover:bg-white/20 md:text-base"
              >
                Back to Landing
              </button>
            </div>
          </form>

          {errorMessage ? <p className="mt-5 text-sm text-[#ffcfc5]">{errorMessage}</p> : null}
          {successMessage ? <p className="mt-2 text-sm text-[#d9ffdf]">{successMessage}</p> : null}

          <div className="mt-8">
            <p className="text-xs uppercase tracking-[0.18em] text-[#f1e7d7]/90">Public groups</p>
            <div className="mt-3 space-y-2">
              {loadingPublic ? <p className="text-sm text-[#f1e7d7]/90">Loading public groups...</p> : null}
              {!loadingPublic && publicGroups.length === 0 ? (
                <p className="text-sm text-[#f1e7d7]/90">No public groups available right now.</p>
              ) : null}
              {publicGroups.map((publicGroup) => (
                <div
                  key={publicGroup.id}
                  className="flex flex-wrap items-center justify-between gap-3 rounded-xl border border-white/25 bg-white/8 px-3 py-2 backdrop-blur-xl"
                >
                  <div>
                    <p className="text-[#f7efdf]">{publicGroup.name}</p>
                    <p className="text-xs uppercase tracking-[0.16em] text-[#f1e7d7]/85">{publicGroup.join_code}</p>
                  </div>
                  <button
                    type="button"
                    onClick={() => setJoinCode(publicGroup.join_code)}
                    className="liquid-chip rounded-lg border border-[#f3e7d4]/30 px-3 py-1.5 text-xs text-[#fff8eb]"
                  >
                    Use this code
                  </button>
                  <button
                    type="button"
                    onClick={() => requestToJoin(publicGroup.id, publicGroup.name)}
                    className="rounded-lg border border-white/30 bg-white/10 px-3 py-1.5 text-xs text-[#efe3d1] transition hover:bg-white/20"
                  >
                    Request join
                  </button>
                </div>
              ))}
            </div>
          </div>
          </div>
        </section>

        <div className="mx-auto mt-7 flex max-w-3xl flex-wrap items-center gap-3 text-sm text-[#f1e7d7]">
          <span>Want to start your own plan?</span>
          <button
            type="button"
            onClick={() => navigate("/create-group")}
            className="liquid-chip rounded-xl border border-[#f3e7d4]/30 px-3 py-1.5 text-[#fff8eb]"
          >
            Go to Create Group
          </button>
        </div>
      </main>
    </div>
  );
}
