import axios from "axios";
import { RefreshCcw, Users } from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import Navbar from "../components/Navbar";

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
  const [form, setForm] = useState(DEFAULT_FORM);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");
  const [successMessage, setSuccessMessage] = useState("");

  const rawApiBaseUrl = (import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000").replace(/\/$/, "");
  const groupsApiBaseUrl = useMemo(
    () => (rawApiBaseUrl.endsWith("/api/v1") ? `${rawApiBaseUrl}/groups` : `${rawApiBaseUrl}/api/v1/groups`),
    [rawApiBaseUrl]
  );

  const authHeaders = useMemo(() => ({ Authorization: `Bearer ${authToken}` }), [authToken]);

  useEffect(() => {
    if (!authToken) {
      navigate("/login", { replace: true });
      return;
    }

    let isMounted = true;
    async function loadGroupData() {
      setLoading(true);
      setErrorMessage("");
      try {
        const [groupRes, membersRes, statusRes, metricsRes] = await Promise.all([
          axios.get(`${groupsApiBaseUrl}/${groupId}`, { headers: authHeaders }),
          axios.get(`${groupsApiBaseUrl}/${groupId}/members`, { headers: authHeaders }),
          axios.get(`${groupsApiBaseUrl}/${groupId}/preferences/status`, { headers: authHeaders }),
          axios.get(`${groupsApiBaseUrl}/${groupId}/metrics`, { headers: authHeaders }),
        ]);
        if (!isMounted) return;
        setGroup(groupRes.data);
        setMembers(membersRes.data?.members || []);
        setStatus(statusRes.data);
        setMetrics(metricsRes.data);
      } catch (error) {
        if (!isMounted) return;
        if (error?.response?.status === 403) {
          setErrorMessage("You do not have access to this group.");
        } else if (error?.response?.status === 404) {
          setErrorMessage("Group not found.");
        } else {
          setErrorMessage("Could not load group dashboard.");
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
  }, [authHeaders, authToken, groupId, groupsApiBaseUrl, navigate]);

  async function refreshDashboard() {
    setSuccessMessage("");
    setErrorMessage("");
    setLoading(true);
    try {
      const [membersRes, statusRes, metricsRes] = await Promise.all([
        axios.get(`${groupsApiBaseUrl}/${groupId}/members`, { headers: authHeaders }),
        axios.get(`${groupsApiBaseUrl}/${groupId}/preferences/status`, { headers: authHeaders }),
        axios.get(`${groupsApiBaseUrl}/${groupId}/metrics`, { headers: authHeaders }),
      ]);
      setMembers(membersRes.data?.members || []);
      setStatus(statusRes.data);
      setMetrics(metricsRes.data);
    } catch {
      setErrorMessage("Could not refresh dashboard data.");
    } finally {
      setLoading(false);
    }
  }

  async function submitPreferences(event) {
    event.preventDefault();
    setSaving(true);
    setErrorMessage("");
    setSuccessMessage("");
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
      setSuccessMessage("Preferences saved.");
      await refreshDashboard();
    } catch (error) {
      if (error?.response?.status === 422) {
        setErrorMessage("Invalid preferences. Check values and try again.");
      } else if (error?.response?.status === 403) {
        setErrorMessage("You are not an active member of this group.");
      } else {
        setErrorMessage("Could not save preferences.");
      }
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="group-scene relative min-h-screen overflow-hidden text-[#f7f1e6]">
      <div className="group-bg-gradient-create absolute inset-0" />
      <div className="group-orb-a absolute -left-24 top-8 h-[22rem] w-[22rem] rounded-full login-float-fast" />
      <div className="group-orb-b absolute -right-24 bottom-10 h-[25rem] w-[25rem] rounded-full login-float-slow" />
      <div className="absolute inset-0 grain" />

      <Navbar />
      <main className="relative z-10 mx-auto max-w-6xl space-y-6 px-6 pb-16 pt-6 md:pt-10">
        <section className="group-panel rounded-[2rem] border border-[#efe4d0]/35 p-6">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div>
              <p className="text-xs uppercase tracking-[0.16em] text-[#f0e4d0]/85">Group dashboard</p>
              <h1 className="mt-2 font-serif text-4xl leading-tight">{group?.name || `Group #${groupId}`}</h1>
              <p className="mt-2 text-sm text-[#e8dcc8]/85">
                Join code: <span className="tracking-[0.15em] text-[#fff7ea]">{group?.join_code || "-"}</span>
              </p>
            </div>
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
          </div>
          {errorMessage ? <p className="mt-4 text-sm text-[#ffcfc5]">{errorMessage}</p> : null}
          {successMessage ? <p className="mt-2 text-sm text-[#d9ffdf]">{successMessage}</p> : null}
        </section>

        <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          {[
            ["Group size", metrics?.groupSize],
            ["Preferences completion", `${metrics?.preferenceCompletionPercent ?? 0}%`],
            ["Budget alignment", `${metrics?.budgetAlignmentScore ?? 0}%`],
            ["Activity match", `${metrics?.activityMatchScore ?? 0}%`],
            ["Conflict count", metrics?.conflictCount ?? 0],
            ["Itinerary confidence", `${metrics?.itineraryConfidenceScore ?? 0}%`],
            ["Approval status", metrics?.approvalStatus || "NOT_STARTED"],
            ["Members listed", members.length],
          ].map(([label, value]) => (
            <div key={label} className="group-panel rounded-2xl border border-[#efe4d0]/35 p-4">
              <p className="text-xs uppercase tracking-[0.16em] text-[#f0e4d0]/80">{label}</p>
              <p className="mt-2 text-2xl text-[#fff7ea]">{value}</p>
            </div>
          ))}
        </section>

        <section className="grid gap-6 lg:grid-cols-2">
          <form
            onSubmit={submitPreferences}
            className="group-panel rounded-[2rem] border border-[#efe4d0]/35 p-6 space-y-4"
          >
            <h2 className="font-serif text-3xl">Preferences questionnaire</h2>
            <p className="text-sm text-[#e8dcc8]/85">Update your constraints to improve group fit and metrics.</p>

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

          <section className="group-panel rounded-[2rem] border border-[#efe4d0]/35 p-6">
            <div className="flex items-center gap-2">
              <Users className="h-4 w-4" />
              <h2 className="font-serif text-3xl">Group members</h2>
            </div>
            <p className="mt-2 text-sm text-[#e8dcc8]/85">
              Completion: {status?.completion_percent ?? metrics?.preferenceCompletionPercent ?? 0}%
            </p>

            <div className="mt-4 space-y-2">
              {members.map((member) => {
                const hasPreferences = status?.members?.find((item) => item.user_id === member.id)?.has_preferences;
                return (
                  <div
                    key={member.id}
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
              {members.length === 0 ? <p className="text-sm text-[#e8dbc7]/80">No members found.</p> : null}
            </div>
          </section>
        </section>
      </main>
    </div>
  );
}
