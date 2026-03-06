import * as React from "react";
import { AnimatePresence, MotionConfig, motion } from "framer-motion";
import { ChevronDown } from "lucide-react";

function cn(...classes) {
  return classes.filter(Boolean).join(" ");
}

function useClickAway(ref, handler) {
  React.useEffect(() => {
    const listener = (event) => {
      if (!ref.current || ref.current.contains(event.target)) return;
      handler(event);
    };
    document.addEventListener("mousedown", listener);
    document.addEventListener("touchstart", listener);
    return () => {
      document.removeEventListener("mousedown", listener);
      document.removeEventListener("touchstart", listener);
    };
  }, [ref, handler]);
}

function IconWrapper({ icon: Icon, isHovered, color }) {
  return (
    <motion.div className="relative mr-2 h-4 w-4" initial={false} animate={isHovered ? { scale: 1.15 } : { scale: 1 }}>
      <Icon className="h-4 w-4" />
      {isHovered ? (
        <motion.div
          className="absolute inset-0"
          style={{ color }}
          initial={{ pathLength: 0, opacity: 0 }}
          animate={{ pathLength: 1, opacity: 1 }}
          transition={{ duration: 0.35, ease: "easeInOut" }}
        >
          <Icon className="h-4 w-4" strokeWidth={2} />
        </motion.div>
      ) : null}
    </motion.div>
  );
}

const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      when: "beforeChildren",
      staggerChildren: 0.08,
    },
  },
};

const itemVariants = {
  hidden: { opacity: 0, y: -8 },
  visible: {
    opacity: 1,
    y: 0,
    transition: {
      duration: 0.22,
      ease: [0.25, 0.1, 0.25, 1],
    },
  },
};

export function FluidDropdown({
  options,
  value,
  onChange,
  disabled = false,
  className = "",
  buttonClassName = "",
  menuClassName = "",
}) {
  const [isOpen, setIsOpen] = React.useState(false);
  const [hovered, setHovered] = React.useState(null);
  const dropdownRef = React.useRef(null);
  const selected = React.useMemo(
    () => options.find((option) => option.id === value) || options[0],
    [options, value]
  );

  useClickAway(dropdownRef, () => setIsOpen(false));

  const handleKeyDown = (e) => {
    if (e.key === "Escape") setIsOpen(false);
  };

  return (
    <MotionConfig reducedMotion="user">
      <div ref={dropdownRef} className={cn("relative w-full min-w-[12rem] max-w-xs", className)}>
        <button
          type="button"
          disabled={disabled}
          onClick={() => setIsOpen((prev) => !prev)}
          className={cn(
            "inline-flex h-10 w-full items-center justify-between rounded-xl border border-[#f1e6d6]/35 bg-[#14171d]/55 px-3 text-sm text-[#f8f2e7] transition-all",
            "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#f3e7d4]/35",
            "disabled:pointer-events-none disabled:opacity-60",
            isOpen ? "bg-[#1a212b]/75 text-[#fff8eb]" : "hover:bg-[#1a212b]/65",
            buttonClassName
          )}
          aria-expanded={isOpen}
          aria-haspopup="listbox"
          aria-label="Choose an option"
        >
          <span className="flex items-center">
            <IconWrapper icon={selected.icon} isHovered={false} color={selected.color} />
            {selected.label}
          </span>
          <motion.div animate={{ rotate: isOpen ? 180 : 0 }} transition={{ duration: 0.2 }} className="flex h-5 w-5 items-center justify-center">
            <ChevronDown className="h-4 w-4" />
          </motion.div>
        </button>

        <AnimatePresence>
          {isOpen ? (
            <motion.div
              className="absolute left-0 right-0 top-full z-50 mt-2"
              initial={{ opacity: 1, y: 0, height: 0 }}
              animate={{
                opacity: 1,
                y: 0,
                height: "auto",
                transition: { type: "spring", stiffness: 500, damping: 32, mass: 1 },
              }}
              exit={{
                opacity: 0,
                y: 0,
                height: 0,
                transition: { type: "spring", stiffness: 500, damping: 32, mass: 1 },
              }}
              onKeyDown={handleKeyDown}
            >
              <motion.div
                className={cn("w-full rounded-lg border border-neutral-800 bg-neutral-900 p-1 shadow-lg", menuClassName)}
                initial={{ borderRadius: 8 }}
                animate={{ borderRadius: 12, transition: { duration: 0.2 } }}
                style={{ transformOrigin: "top" }}
              >
                <motion.div className="relative py-1" variants={containerVariants} initial="hidden" animate="visible">
                  <motion.div
                    layoutId="dropdown-hover-highlight"
                    className="absolute inset-x-1 rounded-md bg-neutral-800"
                    animate={{
                      y: options.findIndex((option) => (hovered || selected.id) === option.id) * 40,
                      height: 40,
                    }}
                    transition={{ type: "spring", bounce: 0.12, duration: 0.4 }}
                  />
                  {options.map((option) => (
                    <motion.button
                      key={option.id}
                      type="button"
                      role="option"
                      aria-selected={selected.id === option.id}
                      onClick={() => {
                        onChange(option.id);
                        setIsOpen(false);
                      }}
                      onHoverStart={() => setHovered(option.id)}
                      onHoverEnd={() => setHovered(null)}
                      className={cn(
                        "relative flex w-full items-center rounded-md px-4 py-2.5 text-sm transition-colors duration-150 focus:outline-none",
                        selected.id === option.id || hovered === option.id ? "text-neutral-200" : "text-neutral-400"
                      )}
                      whileTap={{ scale: 0.98 }}
                      variants={itemVariants}
                    >
                      <IconWrapper icon={option.icon} isHovered={hovered === option.id} color={option.color} />
                      {option.label}
                    </motion.button>
                  ))}
                </motion.div>
              </motion.div>
            </motion.div>
          ) : null}
        </AnimatePresence>
      </div>
    </MotionConfig>
  );
}
