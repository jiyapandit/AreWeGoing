import axios from "axios";
import { AlertTriangle, Bell, CheckCircle2, Home, Mail, RefreshCcw, Users } from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import Navbar from "../components/Navbar";
import AppToast from "@/components/ui/app-toast";
import { FluidDropdown } from "@/components/ui/fluid-dropdown";

function getAccessToken() {
  return (
    window.localStorage.getItem("arewegoing_access_token") || window.sessionStorage.getItem("arewegoing_access_token")
  );
}

const DEFAULT_FORM = {
  destination_type: "",
  budget_min: "",
  budget_max: "",
  days: "",
  activities: "",
  transport_mode: "",
  dietary_preferences: "",
  travel_pace: "",
};

export default function GroupDashboard() {
  const { groupId } = useParams();
  const navigate = useNavigate();
  const authToken = getAccessToken();
  const [group, setGroup] = useState(null);
  const [members, setMembers] = useState([]);
  const [status, setStatus] = useState(null);
  const [metrics, setMetrics] = useState(null);
  const [metricHistory, setMetricHistory] = useState([]);
  const [form, setForm] = useState(DEFAULT_FORM);
  const [itinerary, setItinerary] = useState(null);
  const [voteValue, setVoteValue] = useState("APPROVE");
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [inviteEmail, setInviteEmail] = useState("");
  const [invites, setInvites] = useState([]);
  const [notifications, setNotifications] = useState([]);
  const [currentUserId, setCurrentUserId] = useState(null);
  const [memberStatusFilter, setMemberStatusFilter] = useState("ALL");
  const [membershipActionId, setMembershipActionId] = useState(null);
  const [inviteStatusFilter, setInviteStatusFilter] = useState("ALL");
  const [inviteActionId, setInviteActionId] = useState(null);
  const [readingNotificationId, setReadingNotificationId] = useState(null);
  const [toast, setToast] = useState({ message: "", type: "info" });

  const rawApiBaseUrl = (import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000").replace(/\/$/, "");
  const groupsApiBaseUrl = useMemo(
    () => (rawApiBaseUrl.endsWith("/api/v1") ? `${rawApiBaseUrl}/groups` : `${rawApiBaseUrl}/api/v1/groups`),
    [rawApiBaseUrl]
  );

  const authHeaders = useMemo(() => ({ Authorization: `Bearer ${authToken}` }), [authToken]);
  const authApiBaseUrl = useMemo(
    () => (rawApiBaseUrl.endsWith("/api/v1") ? `${rawApiBaseUrl}/auth` : `${rawApiBaseUrl}/api/v1/auth`),
    [rawApiBaseUrl]
  );
  const isHost = useMemo(
    () => members.some((member) => member.id === currentUserId && member.role === "HOST" && member.status === "ACTIVE"),
    [members, currentUserId]
  );
  const pendingMembers = useMemo(() => members.filter((member) => member.status === "PENDING"), [members]);
  const sortedPendingMembers = useMemo(
    () => [...pendingMembers].sort((a, b) => String(a.email || "").localeCompare(String(b.email || ""))),
    [pendingMembers]
  );
  const activeMembers = useMemo(() => members.filter((member) => member.status === "ACTIVE"), [members]);
  const rejectedMembers = useMemo(() => members.filter((member) => member.status === "REJECTED"), [members]);
  const visibleMembers = useMemo(() => {
    if (memberStatusFilter === "ALL") return members;
    return members.filter((member) => member.status === memberStatusFilter);
  }, [members, memberStatusFilter]);
  const filteredNotifications = useMemo(
    () => notifications.filter((n) => !groupId || String(n.group_id) === String(groupId)).slice(0, 4),
    [notifications, groupId]
  );
  const unreadNotifications = useMemo(
    () => filteredNotifications.filter((notification) => !notification.is_read).length,
    [filteredNotifications]
  );
  const visibleInvites = useMemo(() => {
    if (inviteStatusFilter === "ALL") return invites;
    return invites.filter((invite) => invite.status === inviteStatusFilter);
  }, [invites, inviteStatusFilter]);
  const itineraryState = itinerary?.state || "NOT_CREATED";
  const canGenerateItinerary = itineraryState === "NOT_CREATED" || itineraryState === "DRAFT";
  const canMoveToReview = itineraryState === "DRAFT";
  const canVote = itineraryState === "REVIEW";
  const canLock = isHost && itineraryState === "REVIEW";
  const voteOptions = useMemo(
    () => [
      { id: "APPROVE", label: "Approve", icon: CheckCircle2, color: "#34D399" },
      { id: "CHANGES", label: "Request Changes", icon: AlertTriangle, color: "#F59E0B" },
    ],
    []
  );

  useEffect(() => {
    if (!authToken) {
      navigate("/login", { replace: true });
      return;
    }

    let isMounted = true;
    async function loadGroupData() {
      setLoading(true);
      setToast({ message: "", type: "info" });
      try {
        const [groupRes, membersRes, statusRes, metricsRes, metricHistoryRes, invitesRes, notificationsRes, meRes] = await Promise.all([
          axios.get(`${groupsApiBaseUrl}/${groupId}`, { headers: authHeaders }),
          axios.get(`${groupsApiBaseUrl}/${groupId}/members`, { headers: authHeaders }),
          axios.get(`${groupsApiBaseUrl}/${groupId}/preferences/status`, { headers: authHeaders }),
          axios.get(`${groupsApiBaseUrl}/${groupId}/metrics`, { headers: authHeaders }),
          axios.get(`${groupsApiBaseUrl}/${groupId}/metrics/history`, { headers: authHeaders }),
          axios.get(`${groupsApiBaseUrl}/${groupId}/invites`, { headers: authHeaders }),
          axios.get(`${rawApiBaseUrl.endsWith("/api/v1") ? rawApiBaseUrl : `${rawApiBaseUrl}/api/v1`}/notifications`, {
            headers: authHeaders,
          }),
          axios.get(`${authApiBaseUrl}/me`, { headers: authHeaders }),
        ]);
        if (!isMounted) return;
        setGroup(groupRes.data);
        setMembers(membersRes.data?.members || []);
        setStatus(statusRes.data);
        setMetrics(metricsRes.data);
        setMetricHistory(metricHistoryRes.data || []);
        setInvites(invitesRes.data || []);
        setNotifications(notificationsRes.data || []);
        setCurrentUserId(meRes.data?.id || null);
        try {
          const itineraryRes = await axios.get(`${groupsApiBaseUrl}/${groupId}/itinerary`, { headers: authHeaders });
          setItinerary(itineraryRes.data);
        } catch {
          setItinerary(null);
        }
      } catch (error) {
        if (!isMounted) return;
        if (error?.response?.status === 403) {
          setToast({ message: "You do not have access to this group.", type: "error" });
        } else if (error?.response?.status === 404) {
          setToast({ message: "Group not found.", type: "error" });
        } else {
          setToast({ message: "Could not load group dashboard.", type: "error" });
        }
      } finally {
        if (isMounted) setLoading(false);
      }
    }

    async function loadMyPreferences() {
      try {
        const { data } = await axios.get(`${groupsApiBaseUrl}/${groupId}/preferences/me`, { headers: authHeaders });
        if (!isMounted || !data) return;
        setForm({
          destination_type: data.destination_type || "",
          budget_min: data.budget_min ?? "",
          budget_max: data.budget_max ?? "",
          days: data.days ?? "",
          activities: (data.activities || []).join(", "),
          transport_mode: data.transport_mode || "",
          dietary_preferences: (data.dietary_preferences || []).join(", "),
          travel_pace: data.travel_pace || "",
        });
      } catch {
        // no existing preferences yet
      }
    }

    loadGroupData();
    loadMyPreferences();
    return () => {
      isMounted = false;
    };
  }, [authApiBaseUrl, authHeaders, authToken, groupId, groupsApiBaseUrl, navigate, rawApiBaseUrl]);

  async function refreshDashboard() {
    setToast({ message: "", type: "info" });
    setLoading(true);
    try {
      const [membersRes, statusRes, metricsRes, metricHistoryRes, invitesRes, notificationsRes, meRes] = await Promise.all([
        axios.get(`${groupsApiBaseUrl}/${groupId}/members`, { headers: authHeaders }),
        axios.get(`${groupsApiBaseUrl}/${groupId}/preferences/status`, { headers: authHeaders }),
        axios.get(`${groupsApiBaseUrl}/${groupId}/metrics`, { headers: authHeaders }),
        axios.get(`${groupsApiBaseUrl}/${groupId}/metrics/history`, { headers: authHeaders }),
        axios.get(`${groupsApiBaseUrl}/${groupId}/invites`, { headers: authHeaders }),
        axios.get(`${rawApiBaseUrl.endsWith("/api/v1") ? rawApiBaseUrl : `${rawApiBaseUrl}/api/v1`}/notifications`, {
          headers: authHeaders,
        }),
        axios.get(`${authApiBaseUrl}/me`, { headers: authHeaders }),
      ]);
      setMembers(membersRes.data?.members || []);
      setStatus(statusRes.data);
      setMetrics(metricsRes.data);
      setMetricHistory(metricHistoryRes.data || []);
      setInvites(invitesRes.data || []);
      setNotifications(notificationsRes.data || []);
      setCurrentUserId(meRes.data?.id || null);
      try {
        const itineraryRes = await axios.get(`${groupsApiBaseUrl}/${groupId}/itinerary`, { headers: authHeaders });
        setItinerary(itineraryRes.data);
      } catch {
        setItinerary(null);
      }
    } catch {
      setToast({ message: "Could not refresh dashboard data.", type: "error" });
    } finally {
      setLoading(false);
    }
  }

  async function generateItinerary() {
    setToast({ message: "", type: "info" });
    try {
      const { data } = await axios.post(`${groupsApiBaseUrl}/${groupId}/itinerary/generate`, {}, { headers: authHeaders });
      setItinerary(data);
      setToast({ message: "Itinerary draft generated.", type: "success" });
      await refreshDashboard();
    } catch (error) {
      if (error?.response?.status === 409) {
        setToast({ message: error?.response?.data?.message || "Cannot generate itinerary.", type: "error" });
      } else {
        setToast({ message: "Could not generate itinerary.", type: "error" });
      }
    }
  }

  async function moveToReview() {
    setToast({ message: "", type: "info" });
    try {
      const { data } = await axios.post(`${groupsApiBaseUrl}/${groupId}/itinerary/review`, {}, { headers: authHeaders });
      setItinerary(data);
      setToast({ message: "Itinerary moved to review.", type: "success" });
      await refreshDashboard();
    } catch (error) {
      setToast({ message: error?.response?.data?.message || "Could not move itinerary to review.", type: "error" });
    }
  }

  async function voteItinerary() {
    setToast({ message: "", type: "info" });
    try {
      await axios.post(`${groupsApiBaseUrl}/${groupId}/vote`, { value: voteValue }, { headers: authHeaders });
      setToast({ message: "Vote submitted.", type: "success" });
      await refreshDashboard();
    } catch (error) {
      setToast({ message: error?.response?.data?.message || "Could not submit vote.", type: "error" });
    }
  }

  async function lockItineraryNow() {
    setToast({ message: "", type: "info" });
    if (!isHost) {
      setToast({ message: "Only host can lock itinerary.", type: "error" });
      return;
    }
    try {
      const { data } = await axios.post(`${groupsApiBaseUrl}/${groupId}/itinerary/lock`, {}, { headers: authHeaders });
      setItinerary(data);
      setToast({ message: "Itinerary locked.", type: "success" });
      await refreshDashboard();
    } catch (error) {
      setToast({ message: error?.response?.data?.message || "Could not lock itinerary.", type: "error" });
    }
  }

  async function sendInvite(event) {
    event.preventDefault();
    setToast({ message: "", type: "info" });
    if (!inviteEmail.trim()) {
      setToast({ message: "Enter email to invite.", type: "error" });
      return;
    }
    try {
      await axios.post(
        `${groupsApiBaseUrl}/${groupId}/invites`,
        { email: inviteEmail.trim().toLowerCase() },
        { headers: authHeaders }
      );
      setInviteEmail("");
      setToast({ message: "Invite sent.", type: "success" });
      await refreshDashboard();
    } catch (error) {
      if (error?.response?.status === 403) {
        setToast({ message: "Only host can send invites.", type: "error" });
      } else {
        setToast({ message: "Could not send invite.", type: "error" });
      }
    }
  }

  async function resendInvite(invite) {
    setToast({ message: "", type: "info" });
    if (!isHost) {
      setToast({ message: "Only host can resend invites.", type: "error" });
      return;
    }
    setInviteActionId(invite.id);
    try {
      await axios.post(
        `${groupsApiBaseUrl}/${groupId}/invites`,
        { email: invite.email },
        { headers: authHeaders }
      );
      setToast({ message: `Invite resent to ${invite.email}.`, type: "success" });
      await refreshDashboard();
    } catch (error) {
      if (error?.response?.status === 403) {
        setToast({ message: "Only host can resend invites.", type: "error" });
      } else if (error?.response?.status === 404) {
        setToast({ message: "Group not found.", type: "error" });
      } else {
        setToast({ message: "Could not resend invite.", type: "error" });
      }
    } finally {
      setInviteActionId(null);
    }
  }

  async function revokeInvite(invite) {
    setToast({ message: "", type: "info" });
    if (!isHost) {
      setToast({ message: "Only host can cancel invites.", type: "error" });
      return;
    }
    setInviteActionId(invite.id);
    try {
      await axios.patch(
        `${groupsApiBaseUrl}/${groupId}/invites/${invite.id}`,
        { status: "REVOKED" },
        { headers: authHeaders }
      );
      setToast({ message: `Invite canceled for ${invite.email}.`, type: "success" });
      await refreshDashboard();
    } catch (error) {
      if (error?.response?.status === 403) {
        setToast({ message: "Only host can cancel invites.", type: "error" });
      } else if (error?.response?.status === 404) {
        setToast({ message: "Invite not found.", type: "error" });
      } else if (error?.response?.status === 409) {
        setToast({ message: "Invite cannot be canceled in its current status.", type: "error" });
      } else {
        setToast({ message: "Could not cancel invite.", type: "error" });
      }
    } finally {
      setInviteActionId(null);
    }
  }

  async function updatePendingMembership(membershipId, nextStatus) {
    setToast({ message: "", type: "info" });
    if (!isHost) {
      setToast({ message: "Only host can update join requests.", type: "error" });
      return;
    }
    setMembershipActionId(membershipId);
    try {
      await axios.patch(
        `${groupsApiBaseUrl}/${groupId}/members/${membershipId}/status`,
        { status: nextStatus },
        { headers: authHeaders }
      );
      setToast({ message: `Request ${nextStatus === "ACTIVE" ? "approved" : "rejected"}.`, type: "success" });
      await refreshDashboard();
    } catch (error) {
      if (error?.response?.status === 403) {
        setToast({ message: "Only host can update membership status.", type: "error" });
      } else if (error?.response?.status === 404) {
        setToast({ message: "Membership request not found.", type: "error" });
      } else {
        setToast({ message: "Could not update request.", type: "error" });
      }
    } finally {
      setMembershipActionId(null);
    }
  }

  async function submitPreferences(event) {
    event.preventDefault();
    setSaving(true);
    setToast({ message: "", type: "info" });
    try {
      await axios.put(
        `${groupsApiBaseUrl}/${groupId}/preferences`,
        {
          destination_type: form.destination_type || null,
          budget_min: form.budget_min === "" ? null : Number(form.budget_min),
          budget_max: form.budget_max === "" ? null : Number(form.budget_max),
          days: form.days === "" ? null : Number(form.days),
          activities: form.activities
            .split(",")
            .map((item) => item.trim())
            .filter(Boolean),
          transport_mode: form.transport_mode || null,
          dietary_preferences: form.dietary_preferences
            .split(",")
            .map((item) => item.trim())
            .filter(Boolean),
          travel_pace: form.travel_pace || null,
        },
        { headers: authHeaders }
      );
      setToast({ message: "Preferences saved.", type: "success" });
      await refreshDashboard();
    } catch (error) {
      if (error?.response?.status === 422) {
        setToast({ message: "Invalid preferences. Check values and try again.", type: "error" });
      } else if (error?.response?.status === 403) {
        setToast({ message: "You are not an active member of this group.", type: "error" });
      } else {
        setToast({ message: "Could not save preferences.", type: "error" });
      }
    } finally {
      setSaving(false);
    }
  }

  async function markNotificationAsRead(notificationId) {
    setToast({ message: "", type: "info" });
    setReadingNotificationId(notificationId);
    try {
      await axios.patch(
        `${rawApiBaseUrl.endsWith("/api/v1") ? rawApiBaseUrl : `${rawApiBaseUrl}/api/v1`}/notifications/${notificationId}/read`,
        {},
        { headers: authHeaders }
      );
      setNotifications((prev) =>
        prev.map((notification) =>
          notification.id === notificationId ? { ...notification, is_read: true } : notification
        )
      );
    } catch {
      setToast({ message: "Could not mark notification as read.", type: "error" });
    } finally {
      setReadingNotificationId(null);
    }
  }

  async function captureMetricsSnapshot() {
    setToast({ message: "", type: "info" });
    try {
      await axios.post(`${groupsApiBaseUrl}/${groupId}/metrics/snapshot`, {}, { headers: authHeaders });
      setToast({ message: "Metrics snapshot captured.", type: "success" });
      await refreshDashboard();
    } catch {
      setToast({ message: "Could not capture metrics snapshot.", type: "error" });
    }
  }

  return (
    <div className="group-scene relative min-h-screen overflow-hidden text-[#f7f1e6]">
      <AppToast
        message={toast.message}
        type={toast.type}
        onClose={() => setToast({ message: "", type: "info" })}
      />
      <div className="group-bg-gradient-create absolute inset-0" />
      <div className="scene-photo-wash-dashboard absolute inset-0 opacity-32" />
      <div className="group-cinematic-vignette absolute inset-0" />
      <div className="group-orb-a absolute -left-24 top-8 h-[22rem] w-[22rem] rounded-full login-float-fast" />
      <div className="group-orb-b absolute -right-24 bottom-10 h-[25rem] w-[25rem] rounded-full login-float-slow" />
      <div className="absolute inset-0 grain" />

      <Navbar />
      <main className="relative z-10 mx-auto max-w-6xl space-y-6 px-6 pb-16 pt-6 md:pt-10">
        <section className="dashboard-section group-panel group-panel-dashboard rounded-[2rem] border border-[#efe4d0]/35 p-6">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div>
              <p className="text-xs uppercase tracking-[0.16em] text-[#f0e4d0]/85">Group dashboard</p>
              <h1 className="mt-2 font-serif text-4xl leading-tight">{group?.name || `Group #${groupId}`}</h1>
              <p className="mt-2 text-sm text-[#f1e7d7]">
                Join code: <span className="tracking-[0.15em] text-[#fff7ea]">{group?.join_code || "-"}</span>
              </p>
            </div>
            <nav aria-label="Group dashboard actions" className="flex flex-wrap gap-2">
              <button
                type="button"
                onClick={refreshDashboard}
                className="liquid-chip rounded-xl border border-[#f3e7d4]/30 px-3 py-2 text-sm text-[#fff8eb]"
              >
                <span className="inline-flex items-center gap-2">
                  <RefreshCcw className="h-4 w-4" />
                  Refresh
                </span>
              </button>
              <Link
                to="/dashboard"
                className="rounded-xl border border-[#f3e7d4]/30 bg-[#11151c]/45 px-3 py-2 text-sm text-[#efe3d1] transition hover:bg-[#161d27]/60"
              >
                All trips
              </Link>
              <Link
                to="/landing"
                className="rounded-xl border border-white/30 bg-white/10 px-3 py-2 text-sm text-[#efe3d1] transition hover:bg-white/20"
              >
                <span className="inline-flex items-center gap-2">
                  <Home className="h-4 w-4" />
                  Landing
                </span>
              </Link>
            </nav>
          </div>
          <nav aria-label="Dashboard sections" className="mt-4 flex flex-wrap gap-2 text-xs uppercase tracking-[0.14em] text-[#e8dbc7]/90">
            <a href="#itinerary-section" className="rounded-lg border border-white/25 bg-white/5 px-2.5 py-1 transition hover:bg-white/15">Itinerary</a>
            <a href="#preferences-section" className="rounded-lg border border-white/25 bg-white/5 px-2.5 py-1 transition hover:bg-white/15">Preferences</a>
            <a href="#team-section" className="rounded-lg border border-white/25 bg-white/5 px-2.5 py-1 transition hover:bg-white/15">Team</a>
            <a href="#updates-section" className="rounded-lg border border-white/25 bg-white/5 px-2.5 py-1 transition hover:bg-white/15">Updates</a>
          </nav>
        </section>

        <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
          {loading && !metrics
            ? Array.from({ length: 6 }).map((_, index) => (
                <div key={`metric-skeleton-${index}`} className="skeleton-card">
                  <div className="skeleton-block h-4 w-2/3" />
                  <div className="mt-3 skeleton-block h-8 w-1/2" />
                </div>
              ))
            : [
                ["Group size", metrics?.groupSize],
                ["Preferences completion", `${metrics?.preferenceCompletionPercent ?? 0}%`],
                ["Conflict count", metrics?.conflictCount ?? 0],
                ["Itinerary state", itinerary?.state || "NOT_CREATED"],
                ["Itinerary confidence", `${metrics?.itineraryConfidenceScore ?? 0}%`],
                ["Approval status", metrics?.approvalStatus || "NOT_STARTED"],
              ].map(([label, value]) => (
                <div key={label} className="metric-tile p-4 transition">
                  <p className="text-xs uppercase tracking-[0.16em] text-[#f1e7d7]/90">{label}</p>
                  <p className="mt-2 text-2xl text-[#fff7ea]">{value}</p>
                </div>
              ))}
        </section>
        <section className="rounded-2xl border border-[#f1e6d6]/25 bg-[#0f1319]/45 p-4">
          <div className="flex flex-wrap items-center justify-between gap-2">
            <p className="text-xs uppercase tracking-[0.14em] text-[#e8dbc7]/85">Metrics trend history</p>
            <button
              type="button"
              onClick={captureMetricsSnapshot}
              className="rounded-md border border-[#f3e7d4]/25 bg-white/8 px-2 py-1 text-[11px] uppercase tracking-[0.12em] text-[#efe3d1]"
            >
              Capture snapshot
            </button>
          </div>
          <div className="mt-3 grid gap-2 md:grid-cols-3">
            <div className="rounded-lg border border-white/15 bg-white/5 p-3">
              <p className="text-[11px] uppercase tracking-[0.12em] text-[#e8dbc7]/80">Preference completion</p>
              <div className="mt-2 flex items-end gap-1">
                {metricHistory.slice(0, 8).reverse().map((point) => (
                  <div
                    key={`pref-${point.id}`}
                    className="w-3 rounded-sm bg-emerald-300/60"
                    style={{ height: `${Math.max(8, Number(point.preferenceCompletionPercent || 0)) / 2}px` }}
                  />
                ))}
              </div>
            </div>
            <div className="rounded-lg border border-white/15 bg-white/5 p-3">
              <p className="text-[11px] uppercase tracking-[0.12em] text-[#e8dbc7]/80">Confidence score</p>
              <div className="mt-2 flex items-end gap-1">
                {metricHistory.slice(0, 8).reverse().map((point) => (
                  <div
                    key={`conf-${point.id}`}
                    className="w-3 rounded-sm bg-sky-300/60"
                    style={{ height: `${Math.max(8, Number(point.itineraryConfidenceScore || 0)) / 2}px` }}
                  />
                ))}
              </div>
            </div>
            <div className="rounded-lg border border-white/15 bg-white/5 p-3">
              <p className="text-[11px] uppercase tracking-[0.12em] text-[#e8dbc7]/80">Conflict count</p>
              <div className="mt-2 flex items-end gap-1">
                {metricHistory.slice(0, 8).reverse().map((point) => (
                  <div
                    key={`conflict-${point.id}`}
                    className="w-3 rounded-sm bg-amber-300/60"
                    style={{ height: `${Math.max(8, Number(point.conflictCount || 0) * 14)}px` }}
                  />
                ))}
              </div>
            </div>
          </div>
          {metricHistory.length === 0 ? (
            <p className="mt-2 text-xs text-[#d8ccb7]/80">No snapshots yet. Capture one to start tracking trends.</p>
          ) : null}
        </section>
        <section className="grid gap-3 sm:grid-cols-2">
          <div className="rounded-xl border border-[#f1e6d6]/25 bg-[#0f1319]/45 p-3">
            <p className="text-xs uppercase tracking-[0.14em] text-[#e8dbc7]/85">Budget conflict</p>
            <p className="mt-1 text-sm text-[#f1e7d7]">
              {metrics?.budgetConflict ? "Detected: group budgets have no overlap." : "No conflict detected."}
            </p>
          </div>
          <div className="rounded-xl border border-[#f1e6d6]/25 bg-[#0f1319]/45 p-3">
            <p className="text-xs uppercase tracking-[0.14em] text-[#e8dbc7]/85">Transport conflict</p>
            <p className="mt-1 text-sm text-[#f1e7d7]">
              {metrics?.transportConflict ? "Detected: members selected different transport modes." : "No conflict detected."}
            </p>
          </div>
        </section>

        <section className="dashboard-section grid gap-6 lg:grid-cols-2 xl:grid-cols-3">
          <section id="itinerary-section" className="group-panel group-panel-dashboard rounded-[2rem] border border-[#efe4d0]/35 p-6">
            <h2 className="font-serif text-3xl">Itinerary</h2>
            <p className="mt-2 text-sm text-[#f1e7d7]">
              State: <span className="text-[#fff7ea]">{itinerary?.state || "NOT_CREATED"}</span>
            </p>
            {itinerary?.vote_summary ? (
              <p className="mt-1 text-xs text-[#e8dbc7]/85">
                Votes: {itinerary.vote_summary.approve ?? 0} approve / {itinerary.vote_summary.changes ?? 0} changes
                {" "}({itinerary.vote_summary.total ?? 0} total)
              </p>
            ) : null}
            <div className="mt-4 space-y-3">
              <div className="rounded-xl border border-white/20 bg-white/5 p-3">
                <p className="text-xs uppercase tracking-[0.14em] text-[#e8dbc7]/85">Planning actions</p>
                <div className="mt-2 flex flex-wrap gap-2">
                  <button
                    type="button"
                    onClick={generateItinerary}
                    disabled={!canGenerateItinerary || loading}
                    className="liquid-chip rounded-xl border border-[#f3e7d4]/30 px-4 py-2 text-sm text-[#fff8eb] disabled:cursor-not-allowed disabled:opacity-60"
                  >
                    Generate
                  </button>
                  <button
                    type="button"
                    onClick={moveToReview}
                    disabled={!canMoveToReview || loading}
                    className="liquid-chip rounded-xl border border-[#f3e7d4]/30 px-4 py-2 text-sm text-[#fff8eb] disabled:cursor-not-allowed disabled:opacity-60"
                  >
                    Move to Review
                  </button>
                </div>
              </div>
              <div className="rounded-xl border border-white/20 bg-white/5 p-3">
                <p className="text-xs uppercase tracking-[0.14em] text-[#e8dbc7]/85">Review actions</p>
                <div className="mt-2 flex flex-wrap gap-2">
                  <FluidDropdown
                    options={voteOptions}
                    value={voteValue}
                    onChange={setVoteValue}
                    disabled={!canVote || loading}
                    className="min-w-[14rem]"
                  />
                  <button
                    type="button"
                    onClick={voteItinerary}
                    disabled={!canVote || loading}
                    className="liquid-chip rounded-xl border border-[#f3e7d4]/30 px-4 py-2 text-sm text-[#fff8eb] disabled:cursor-not-allowed disabled:opacity-60"
                  >
                    Vote
                  </button>
                  {isHost ? (
                    <button
                      type="button"
                      onClick={lockItineraryNow}
                      disabled={!canLock || loading}
                      className="rounded-xl border border-[#f3e7d4]/30 bg-[#11151c]/45 px-4 py-2 text-sm text-[#efe3d1] transition hover:bg-[#161d27]/60 disabled:cursor-not-allowed disabled:opacity-60"
                    >
                      Lock (Host)
                    </button>
                  ) : (
                    <span className="rounded-xl border border-[#f3e7d4]/20 bg-[#11151c]/25 px-4 py-2 text-sm text-[#bfb39f]">
                      Lock available to host only
                    </span>
                  )}
                </div>
              </div>
            </div>
            <p className="mt-2 text-xs text-[#e8dbc7]/80">
              {itineraryState === "NOT_CREATED" ? "Generate to start planning." : null}
              {itineraryState === "DRAFT" ? "Draft ready. Move to review when the group is ready to vote." : null}
              {itineraryState === "REVIEW" ? "Review open. Members can vote; host can lock after review." : null}
              {itineraryState === "LOCKED" ? "Itinerary is locked. Generation and voting are disabled." : null}
            </p>

            <div className="mt-4 space-y-3">
              {itinerary?.days?.slice(0, 2).map((day) => (
                <div key={day.day_number} className="rounded-xl border border-[#f1e6d6]/25 bg-[#0f1319]/45 px-3 py-3">
                  <p className="text-sm uppercase tracking-[0.16em] text-[#f1e7d7]/90">Day {day.day_number}</p>
                  <div className="mt-2 space-y-2">
                    {day.items.slice(0, 2).map((item) => (
                      <div key={item.id} className="rounded-lg border border-[#f1e6d6]/20 bg-black/20 px-3 py-2">
                        <p className="text-[#f7efdf]">{item.title}</p>
                        <p className="text-xs text-[#f1e7d7]">{item.summary}</p>
                        <p className="mt-1 text-xs text-[#d2c7b3]/80">
                          ${item.estimated_cost} | {item.duration_hours}h
                        </p>
                      </div>
                    ))}
                  </div>
                </div>
              ))}
              {itinerary?.days?.length > 2 ? (
                <p className="text-xs uppercase tracking-[0.12em] text-[#f1e7d7]/80">Open next days as itinerary evolves.</p>
              ) : null}
              {!itinerary ? <p className="text-sm text-[#f1e7d7]/90">No itinerary generated yet.</p> : null}
            </div>
          </section>

          <form
            id="preferences-section"
            onSubmit={submitPreferences}
            className="group-panel group-panel-dashboard rounded-[2rem] border border-[#efe4d0]/35 p-6 space-y-4"
          >
            <h2 className="font-serif text-3xl">Preferences questionnaire</h2>
            <p className="text-sm text-[#f1e7d7]">Update your constraints to improve group fit and metrics.</p>

            <div className="grid gap-3 md:grid-cols-2">
              <input
                placeholder="Destination type"
                value={form.destination_type}
                onChange={(e) => setForm((prev) => ({ ...prev, destination_type: e.target.value }))}
                className="rounded-xl border border-[#f1e6d6]/35 bg-[#14171d]/55 px-3 py-2 text-[#f8f2e7] outline-none"
              />
              <input
                placeholder="Travel pace"
                value={form.travel_pace}
                onChange={(e) => setForm((prev) => ({ ...prev, travel_pace: e.target.value }))}
                className="rounded-xl border border-[#f1e6d6]/35 bg-[#14171d]/55 px-3 py-2 text-[#f8f2e7] outline-none"
              />
              <input
                type="number"
                placeholder="Budget min"
                value={form.budget_min}
                onChange={(e) => setForm((prev) => ({ ...prev, budget_min: e.target.value }))}
                className="rounded-xl border border-[#f1e6d6]/35 bg-[#14171d]/55 px-3 py-2 text-[#f8f2e7] outline-none"
              />
              <input
                type="number"
                placeholder="Budget max"
                value={form.budget_max}
                onChange={(e) => setForm((prev) => ({ ...prev, budget_max: e.target.value }))}
                className="rounded-xl border border-[#f1e6d6]/35 bg-[#14171d]/55 px-3 py-2 text-[#f8f2e7] outline-none"
              />
              <input
                type="number"
                placeholder="Days"
                value={form.days}
                onChange={(e) => setForm((prev) => ({ ...prev, days: e.target.value }))}
                className="rounded-xl border border-[#f1e6d6]/35 bg-[#14171d]/55 px-3 py-2 text-[#f8f2e7] outline-none"
              />
              <input
                placeholder="Transport mode"
                value={form.transport_mode}
                onChange={(e) => setForm((prev) => ({ ...prev, transport_mode: e.target.value }))}
                className="rounded-xl border border-[#f1e6d6]/35 bg-[#14171d]/55 px-3 py-2 text-[#f8f2e7] outline-none"
              />
              <input
                placeholder="Activities (comma separated)"
                value={form.activities}
                onChange={(e) => setForm((prev) => ({ ...prev, activities: e.target.value }))}
                className="rounded-xl border border-[#f1e6d6]/35 bg-[#14171d]/55 px-3 py-2 text-[#f8f2e7] outline-none md:col-span-2"
              />
              <input
                placeholder="Dietary preferences (comma separated)"
                value={form.dietary_preferences}
                onChange={(e) => setForm((prev) => ({ ...prev, dietary_preferences: e.target.value }))}
                className="rounded-xl border border-[#f1e6d6]/35 bg-[#14171d]/55 px-3 py-2 text-[#f8f2e7] outline-none md:col-span-2"
              />
            </div>

            <button
              type="submit"
              disabled={saving || loading}
              className="liquid-chip rounded-xl border border-[#f3e7d4]/30 px-4 py-2 text-sm text-[#fff8eb] disabled:cursor-not-allowed disabled:opacity-70"
            >
              {saving ? "Saving..." : "Save preferences"}
            </button>
          </form>
        </section>

        <section id="team-section" className="dashboard-section grid gap-6 lg:grid-cols-2 xl:grid-cols-4">
          <section className="group-panel group-panel-dashboard rounded-[2rem] border border-[#efe4d0]/35 p-6 xl:col-span-2" data-testid="group-members-panel">
            <div className="flex items-center gap-2">
              <Users className="h-4 w-4" />
              <h2 className="font-serif text-3xl">Group members</h2>
            </div>
            <p className="mt-2 text-sm text-[#f1e7d7]">
              Completion: {status?.completion_percent ?? metrics?.preferenceCompletionPercent ?? 0}%
            </p>
            <div className="mt-3 flex flex-wrap gap-2 text-xs uppercase tracking-[0.14em] text-[#f1e7d7]/85">
              <button
                type="button"
                onClick={() => setMemberStatusFilter("ALL")}
                className={`rounded-lg border px-2.5 py-1 transition ${
                  memberStatusFilter === "ALL"
                    ? "border-white/45 bg-white/18 text-[#fff7ea]"
                    : "border-white/20 bg-white/5 hover:bg-white/10"
                }`}
              >
                All ({members.length})
              </button>
              <button
                type="button"
                onClick={() => setMemberStatusFilter("ACTIVE")}
                className={`rounded-lg border px-2.5 py-1 transition ${
                  memberStatusFilter === "ACTIVE"
                    ? "border-emerald-300/45 bg-emerald-500/20 text-emerald-100"
                    : "border-white/20 bg-white/5 hover:bg-white/10"
                }`}
              >
                Active ({activeMembers.length})
              </button>
              <button
                type="button"
                onClick={() => setMemberStatusFilter("PENDING")}
                className={`rounded-lg border px-2.5 py-1 transition ${
                  memberStatusFilter === "PENDING"
                    ? "border-amber-300/45 bg-amber-500/20 text-amber-100"
                    : "border-white/20 bg-white/5 hover:bg-white/10"
                }`}
              >
                Pending ({pendingMembers.length})
              </button>
              <button
                type="button"
                onClick={() => setMemberStatusFilter("REJECTED")}
                className={`rounded-lg border px-2.5 py-1 transition ${
                  memberStatusFilter === "REJECTED"
                    ? "border-rose-300/45 bg-rose-500/20 text-rose-100"
                    : "border-white/20 bg-white/5 hover:bg-white/10"
                }`}
              >
                Rejected ({rejectedMembers.length})
              </button>
            </div>

            <div className="mt-4 space-y-2">
              {visibleMembers.map((member) => {
                const hasPreferences = status?.members?.find((item) => item.user_id === member.id)?.has_preferences;
                return (
                  <div
                    key={member.id}
                    data-testid={`group-member-${member.id}`}
                    className="flex flex-wrap items-center justify-between gap-3 rounded-xl border border-[#f1e6d6]/25 bg-[#0f1319]/45 px-3 py-2"
                  >
                    <div>
                      <p className="text-[#f7efdf]">{member.email}</p>
                      <p className="text-xs uppercase tracking-[0.16em] text-[#e8dbc7]/70">
                        {member.role} / {member.status}
                      </p>
                    </div>
                    <span
                      className={`rounded-lg px-2 py-1 text-xs ${
                        hasPreferences
                          ? "bg-emerald-500/20 text-emerald-200"
                          : "bg-amber-500/20 text-amber-200"
                      }`}
                    >
                      {hasPreferences ? "Preferences done" : "Pending preferences"}
                    </span>
                  </div>
                );
              })}
              {visibleMembers.length === 0 ? (
                <p className="text-sm text-[#e8dbc7]/80">No members for selected filter.</p>
              ) : null}
            </div>
          </section>
          <section className="group-panel group-panel-dashboard rounded-[2rem] border border-[#efe4d0]/35 p-6" data-testid="pending-requests-panel">
            <h2 className="font-serif text-3xl">Pending join requests</h2>
            {!isHost ? <p className="mt-2 text-xs text-[#bfb39f]">Only host can manage requests.</p> : null}
            {isHost ? (
              <p className="mt-2 text-xs uppercase tracking-[0.15em] text-[#d8ccb7]/80">
                {sortedPendingMembers.length > 0 ? `${sortedPendingMembers.length} request(s) awaiting review` : "No requests awaiting review"}
              </p>
            ) : null}
            <div className="mt-4 space-y-2">
              {sortedPendingMembers.map((member) => (
                  <div
                    key={member.membership_id}
                    data-testid={`pending-request-${member.membership_id}`}
                    className="flex flex-wrap items-center justify-between gap-2 rounded-xl border border-[#f1e6d6]/25 bg-[#0f1319]/45 px-3 py-2"
                  >
                    <div>
                      <p className="text-sm text-[#f7efdf]">{member.email}</p>
                      <p className="text-xs uppercase tracking-[0.15em] text-[#e8dbc7]/75">{member.role}</p>
                    </div>
                    <div className="flex gap-2">
                      <button
                        type="button"
                        disabled={!isHost || membershipActionId === member.membership_id}
                        onClick={() => updatePendingMembership(member.membership_id, "ACTIVE")}
                        data-testid={`approve-request-${member.membership_id}`}
                        className="rounded-lg border border-emerald-300/35 bg-emerald-500/20 px-3 py-1 text-xs text-emerald-100 disabled:cursor-not-allowed disabled:opacity-50"
                      >
                        {membershipActionId === member.membership_id ? "Approving..." : "Approve"}
                      </button>
                      <button
                        type="button"
                        disabled={!isHost || membershipActionId === member.membership_id}
                        onClick={() => updatePendingMembership(member.membership_id, "REJECTED")}
                        data-testid={`reject-request-${member.membership_id}`}
                        className="rounded-lg border border-rose-300/35 bg-rose-500/20 px-3 py-1 text-xs text-rose-100 disabled:cursor-not-allowed disabled:opacity-50"
                      >
                        {membershipActionId === member.membership_id ? "Rejecting..." : "Reject"}
                      </button>
                    </div>
                  </div>
                ))}
              {sortedPendingMembers.length === 0 ? (
                <p className="text-sm text-[#e8dbc7]/80">{isHost ? "No pending requests." : "Pending requests are visible to host only."}</p>
              ) : null}
            </div>
          </section>

          <section className="group-panel group-panel-dashboard rounded-[2rem] border border-[#efe4d0]/35 p-6">
            <h2 className="font-serif text-3xl">Invites</h2>
            <form onSubmit={sendInvite} className="mt-4 flex flex-wrap gap-2">
              <input
                type="email"
                placeholder="friend@example.com"
                value={inviteEmail}
                onChange={(e) => setInviteEmail(e.target.value)}
                className="min-w-[14rem] flex-1 rounded-xl border border-[#f1e6d6]/35 bg-[#14171d]/55 px-3 py-2 text-[#f8f2e7] outline-none"
              />
              <button
                type="submit"
                disabled={!isHost}
                className="liquid-chip rounded-xl border border-[#f3e7d4]/30 px-4 py-2 text-sm text-[#fff8eb]"
              >
                <span className="inline-flex items-center gap-2">
                  <Mail className="h-4 w-4" />
                  Send invite
                </span>
              </button>
            </form>
            {!isHost ? <p className="mt-2 text-xs text-[#bfb39f]">Only host can send invites.</p> : null}

            <div className="mt-4 space-y-2">
              <div className="flex items-center justify-between gap-2">
                <h3 className="text-xs uppercase tracking-[0.16em] text-[#e8dbc7]/75">Recent invites</h3>
                <div className="flex flex-wrap gap-1.5 text-[11px] uppercase tracking-[0.12em]">
                  {["ALL", "SENT", "ACCEPTED", "REVOKED"].map((statusKey) => (
                    <button
                      key={statusKey}
                      type="button"
                      onClick={() => setInviteStatusFilter(statusKey)}
                      className={`rounded-md border px-2 py-1 transition ${
                        inviteStatusFilter === statusKey
                          ? "border-white/45 bg-white/16 text-[#fff7ea]"
                          : "border-white/20 bg-white/5 text-[#e8dbc7]/85 hover:bg-white/12"
                      }`}
                    >
                      {statusKey}
                    </button>
                  ))}
                </div>
              </div>
              {visibleInvites.slice(0, 6).map((invite) => (
                <div
                  key={invite.id}
                  className="flex flex-wrap items-center justify-between gap-2 rounded-xl border border-[#f1e6d6]/25 bg-[#0f1319]/45 px-3 py-2"
                >
                  <div className="min-w-0">
                    <p className="truncate text-sm text-[#f7efdf]">{invite.email}</p>
                    <p className="text-[11px] uppercase tracking-[0.15em] text-[#e8dbc7]/70">
                      {new Date(invite.created_at).toLocaleString()}
                    </p>
                    <p className="text-[11px] uppercase tracking-[0.15em] text-[#d3c7b2]/70">
                      Delivery: {invite.delivery_status || "PENDING"} | Attempts: {invite.delivery_attempts ?? 0}
                    </p>
                  </div>
                  <div className="flex items-center gap-2">
                    <p className="text-xs uppercase tracking-[0.15em] text-[#e8dbc7]/75">{invite.status}</p>
                    <button
                      type="button"
                      disabled={!isHost || inviteActionId === invite.id || invite.status !== "SENT"}
                      onClick={() => resendInvite(invite)}
                      className="rounded-md border border-[#f3e7d4]/25 bg-white/8 px-2 py-1 text-[11px] uppercase tracking-[0.12em] text-[#efe3d1] disabled:cursor-not-allowed disabled:opacity-60"
                    >
                      {inviteActionId === invite.id ? "Resending..." : "Resend"}
                    </button>
                    <button
                      type="button"
                      disabled={!isHost || inviteActionId === invite.id || invite.status !== "SENT"}
                      onClick={() => revokeInvite(invite)}
                      className="rounded-md border border-rose-300/30 bg-rose-500/10 px-2 py-1 text-[11px] uppercase tracking-[0.12em] text-rose-100 disabled:cursor-not-allowed disabled:opacity-60"
                    >
                      {inviteActionId === invite.id ? "Canceling..." : "Cancel"}
                    </button>
                  </div>
                </div>
              ))}
              {visibleInvites.length === 0 ? (
                <p className="text-sm text-[#e8dbc7]/80">
                  {invites.length === 0 ? "No invites yet." : "No invites in selected status."}
                </p>
              ) : null}
            </div>
          </section>
        </section>

        <section id="updates-section" className="dashboard-section">
          <section className="group-panel group-panel-dashboard rounded-[2rem] border border-[#efe4d0]/35 p-6">
            <div className="flex items-center gap-2">
              <Bell className="h-4 w-4" />
              <h2 className="font-serif text-3xl">Notifications</h2>
              <span className="rounded-full border border-white/25 bg-white/10 px-2 py-0.5 text-xs text-[#f1e7d7]">
                {unreadNotifications} unread
              </span>
            </div>
            <div className="mt-4 space-y-2">
              {filteredNotifications.map((notification) => (
                  <div
                    key={notification.id}
                    className="rounded-xl border border-[#f1e6d6]/25 bg-[#0f1319]/45 px-3 py-2"
                  >
                    <div className="flex items-start justify-between gap-2">
                      <div>
                        <p className="text-sm text-[#f7efdf]">{notification.message}</p>
                        <p className="mt-1 text-xs uppercase tracking-[0.15em] text-[#e8dbc7]/75">{notification.kind}</p>
                      </div>
                      {notification.is_read ? (
                        <span className="rounded-md border border-white/20 bg-white/5 px-2 py-1 text-[11px] text-[#d8ccb7]">
                          Read
                        </span>
                      ) : (
                        <button
                          type="button"
                          disabled={readingNotificationId === notification.id}
                          onClick={() => markNotificationAsRead(notification.id)}
                          className="rounded-md border border-[#f3e7d4]/25 bg-white/8 px-2 py-1 text-[11px] uppercase tracking-[0.12em] text-[#efe3d1] disabled:cursor-not-allowed disabled:opacity-60"
                        >
                          {readingNotificationId === notification.id ? "Saving..." : "Mark read"}
                        </button>
                      )}
                    </div>
                  </div>
                ))}
              {filteredNotifications.length === 0 ? <p className="text-sm text-[#e8dbc7]/80">No notifications.</p> : null}
            </div>
          </section>
        </section>
      </main>
    </div>
  );
}
