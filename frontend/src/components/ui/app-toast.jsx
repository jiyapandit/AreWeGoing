import { AnimatePresence, motion } from "framer-motion";
import { CheckCircle2, Info, X, XCircle } from "lucide-react";
import { useEffect } from "react";

const TOAST_STYLES = {
  success: {
    border: "border-emerald-300/35",
    bg: "bg-emerald-500/12",
    text: "text-emerald-100",
    icon: CheckCircle2,
  },
  error: {
    border: "border-rose-300/35",
    bg: "bg-rose-500/12",
    text: "text-rose-100",
    icon: XCircle,
  },
  info: {
    border: "border-sky-300/35",
    bg: "bg-sky-500/12",
    text: "text-sky-100",
    icon: Info,
  },
};

export default function AppToast({ message, type = "info", onClose, durationMs = 3500 }) {
  useEffect(() => {
    if (!message || !onClose) return;
    const timer = window.setTimeout(() => onClose(), durationMs);
    return () => window.clearTimeout(timer);
  }, [message, onClose, durationMs]);

  const style = TOAST_STYLES[type] || TOAST_STYLES.info;
  const Icon = style.icon;

  return (
    <AnimatePresence>
      {message ? (
        <motion.div
          initial={{ opacity: 0, y: -12, scale: 0.98 }}
          animate={{ opacity: 1, y: 0, scale: 1 }}
          exit={{ opacity: 0, y: -10, scale: 0.98 }}
          transition={{ duration: 0.2 }}
          className={`toast-chip fixed right-5 top-20 z-[120] w-[min(92vw,26rem)] rounded-xl border ${style.border} ${style.bg} p-3 shadow-xl backdrop-blur-xl`}
          role="status"
          aria-live="polite"
        >
          <div className="flex items-start gap-2">
            <Icon className={`mt-0.5 h-4 w-4 shrink-0 ${style.text}`} />
            <p className={`flex-1 text-sm ${style.text}`}>{message}</p>
            <button
              type="button"
              onClick={onClose}
              className="rounded-md p-1 text-white/70 transition hover:bg-white/10 hover:text-white"
              aria-label="Close notification"
            >
              <X className="h-4 w-4" />
            </button>
          </div>
        </motion.div>
      ) : null}
    </AnimatePresence>
  );
}
