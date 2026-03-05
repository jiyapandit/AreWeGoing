import axios from "axios";
import { Copy, Mail, Sparkles, Users } from "lucide-react";
import { useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import Navbar from "../components/Navbar";

function getAccessToken() {
  return (
    window.localStorage.getItem("arewegoing_access_token") || window.sessionStorage.getItem("arewegoing_access_token")
  );
}

export default function CreateGroup() {
  const navigate = useNavigate();
  const [name, setName] = useState("");
  const [isPublic, setIsPublic] = useState(false);
  const [inviteEmail, setInviteEmail] = useState("");
  const [group, setGroup] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");
  const [successMessage, setSuccessMessage] = useState("");

  const authToken = getAccessToken();
  const rawApiBaseUrl = (import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000").replace(/\/$/, "");
  const groupsApiBaseUrl = rawApiBaseUrl.endsWith("/api/v1") ? `${rawApiBaseUrl}/groups` : `${rawApiBaseUrl}/api/v1/groups`;

  const inviteUrl = useMemo(() => {
    if (!group?.join_code) return "";
    return `${window.location.origin}/join-group?code=${encodeURIComponent(group.join_code)}`;
  }, [group?.join_code]);

  async function handleSubmit(e) {
    e.preventDefault();
    setErrorMessage("");
    setSuccessMessage("");

    if (!authToken) {
      setErrorMessage("Please sign in first to create a group.");
      return;
    }

    setIsSubmitting(true);
    try {
      const { data } = await axios.post(
        groupsApiBaseUrl,
        { name: name.trim(), is_public: isPublic },
        { headers: { Authorization: `Bearer ${authToken}` }, timeout: 10000 }
      );
      setGroup(data);
      setSuccessMessage("Group created. Invite your friends using the code below.");
      navigate(`/groups/${data.id}`);
    } catch (error) {
      if (error?.response?.status === 401) {
        setErrorMessage("Session expired. Please sign in again.");
      } else if (error?.response?.status === 422) {
        setErrorMessage("Group name must be between 2 and 120 characters.");
      } else if (error?.response?.status === 400) {
        setErrorMessage(error?.response?.data?.message || "Invalid request.");
      } else {
        setErrorMessage("Could not create group right now. Please try again.");
      }
    } finally {
      setIsSubmitting(false);
    }
  }

  async function copyCode() {
    if (!group?.join_code) return;
    try {
      await navigator.clipboard.writeText(group.join_code);
      setSuccessMessage("Join code copied.");
    } catch {
      setErrorMessage("Copy failed. Please copy the code manually.");
    }
  }

  async function copyInviteLink() {
    if (!inviteUrl) return;
    try {
      await navigator.clipboard.writeText(inviteUrl);
      setSuccessMessage("Invite link copied.");
    } catch {
      setErrorMessage("Copy failed. Please copy the invite link manually.");
    }
  }

  async function sendInvite() {
    if (!group?.join_code) return;
    if (inviteEmail.trim() && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(inviteEmail.trim())) {
      setErrorMessage("Please enter a valid friend email.");
      return;
    }
    if (!inviteEmail.trim()) {
      setErrorMessage("Enter an email to send invite.");
      return;
    }

    try {
      await axios.post(
        `${groupsApiBaseUrl}/${group.id}/invites`,
        { email: inviteEmail.trim().toLowerCase() },
        { headers: { Authorization: `Bearer ${authToken}` }, timeout: 10000 }
      );
      setSuccessMessage("Invite sent.");
      setInviteEmail("");
    } catch (error) {
      if (error?.response?.status === 403) {
        setErrorMessage("Only host can send invites.");
      } else if (error?.response?.status === 404) {
        setErrorMessage("Group not found.");
      } else {
        setErrorMessage("Could not send invite.");
      }
    }
  }

  return (
    <div className="group-scene relative min-h-screen overflow-hidden text-[#f7f1e6]">
      <div className="group-bg-gradient-create absolute inset-0" />
      <div className="group-orb-a absolute -left-28 top-10 h-[24rem] w-[24rem] rounded-full login-float-slow" />
      <div className="group-orb-b absolute -right-24 bottom-12 h-[26rem] w-[26rem] rounded-full login-float-fast" />
      <div className="absolute inset-0 grain" />

      <Navbar />

      <main className="relative z-10 mx-auto max-w-5xl px-6 pb-16 pt-6 md:pt-10">
        <section className="group-panel mx-auto w-full max-w-3xl rounded-[2rem] border border-[#efe4d0]/35 p-6 md:p-9">
          <div className="inline-flex items-center gap-2 rounded-full border border-[#efe4d0]/35 bg-black/20 px-3 py-1 text-xs uppercase tracking-[0.16em] text-[#f4ebda]/90">
            <Sparkles className="h-3.5 w-3.5" />
            Start a trip room
          </div>
          <h1 className="mt-5 font-serif text-4xl leading-tight md:text-5xl">Create your group</h1>
          <p className="mt-3 max-w-xl text-sm text-[#e8dcc8]/90 md:text-base">
            Create once, then invite friends by sending the generated code or link.
          </p>

          <form onSubmit={handleSubmit} className="mt-8 space-y-5">
            <label className="block">
              <span className="text-xs uppercase tracking-[0.18em] text-[#eadfcf]/80">Group name</span>
              <input
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="e.g., Summer Escape 2026"
                className="mt-2 w-full rounded-2xl border border-[#f1e6d6]/35 bg-[#14171d]/55 px-4 py-3 text-[#f8f2e7] outline-none transition focus:border-[#f4ebda]/70 focus:ring-2 focus:ring-[#f4ebda]/20"
                required
                minLength={2}
                maxLength={120}
              />
            </label>

            <label className="inline-flex items-center gap-3 text-sm text-[#ecdfcc]/95">
              <input
                id="isPublic"
                type="checkbox"
                checked={isPublic}
                onChange={(e) => setIsPublic(e.target.checked)}
                className="h-4 w-4 rounded border-[#e8dcc8]/45 bg-transparent"
              />
              Make this group public (it appears in the public groups list)
            </label>

            <div className="flex flex-wrap gap-3 pt-2">
              <button
                type="submit"
                disabled={isSubmitting}
                className="liquid-chip rounded-2xl border border-[#f3e7d4]/30 px-5 py-3 text-sm text-[#fff8eb] disabled:cursor-not-allowed disabled:opacity-70 md:text-base"
              >
                <span className="inline-flex items-center gap-2">
                  <Users className="h-4 w-4" />
                  {isSubmitting ? "Creating..." : "Create Group"}
                </span>
              </button>
              <button
                type="button"
                onClick={() => navigate("/landing")}
                className="rounded-2xl border border-[#f3e7d4]/30 bg-[#11151c]/45 px-5 py-3 text-sm text-[#efe3d1] transition hover:bg-[#161d27]/60 md:text-base"
              >
                Back to Landing
              </button>
            </div>
          </form>

          {group ? (
            <div className="mt-8 space-y-4 rounded-2xl border border-[#f1e6d6]/30 bg-[#0f1319]/55 p-4">
              <div className="flex flex-wrap items-center justify-between gap-3">
                <div>
                  <p className="text-xs uppercase tracking-[0.18em] text-[#e8dbc7]/75">Join code</p>
                  <p className="text-2xl tracking-[0.2em] text-[#fff7ea]">{group.join_code}</p>
                </div>
                <div className="flex gap-2">
                  <button
                    type="button"
                    onClick={copyCode}
                    className="liquid-chip rounded-xl border border-[#f3e7d4]/30 px-3 py-2 text-sm text-[#fff8eb]"
                  >
                    <span className="inline-flex items-center gap-2">
                      <Copy className="h-4 w-4" />
                      Copy code
                    </span>
                  </button>
                  <button
                    type="button"
                    onClick={copyInviteLink}
                    className="liquid-chip rounded-xl border border-[#f3e7d4]/30 px-3 py-2 text-sm text-[#fff8eb]"
                  >
                    Copy invite link
                  </button>
                </div>
              </div>

              <div className="space-y-2">
                <label className="text-xs uppercase tracking-[0.18em] text-[#eadfcf]/80">Invite friend by email</label>
                <div className="flex flex-wrap gap-2">
                  <input
                    type="email"
                    placeholder="friend@example.com"
                    value={inviteEmail}
                    onChange={(e) => setInviteEmail(e.target.value)}
                    className="min-w-[14rem] flex-1 rounded-xl border border-[#f1e6d6]/35 bg-[#14171d]/55 px-3 py-2 text-[#f8f2e7] outline-none"
                  />
                  <button
                    type="button"
                    onClick={sendInvite}
                    className="liquid-chip rounded-xl border border-[#f3e7d4]/30 px-3 py-2 text-sm text-[#fff8eb]"
                  >
                    <span className="inline-flex items-center gap-2">
                      <Mail className="h-4 w-4" />
                      Send invite
                    </span>
                  </button>
                </div>
              </div>
            </div>
          ) : null}

          {errorMessage ? <p className="mt-5 text-sm text-[#ffcfc5]">{errorMessage}</p> : null}
          {successMessage ? <p className="mt-2 text-sm text-[#d9ffdf]">{successMessage}</p> : null}
        </section>

        <div className="mx-auto mt-7 flex max-w-3xl flex-wrap items-center gap-3 text-sm text-[#e8dcc8]/85">
          <span>Already have a code?</span>
          <button
            type="button"
            onClick={() => navigate("/join-group")}
            className="liquid-chip rounded-xl border border-[#f3e7d4]/30 px-3 py-1.5 text-[#fff8eb]"
          >
            Go to Join Group
          </button>
        </div>
      </main>
    </div>
  );
}
