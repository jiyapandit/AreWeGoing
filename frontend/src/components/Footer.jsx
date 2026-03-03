// src/components/Footer.jsx
export default function Footer() {
  return (
    <footer className="pb-10">
      <div className="mx-auto max-w-6xl px-6">
        <div className="rounded-[2rem] bg-white/40 border border-black/5 shadow-glass px-7 py-6 flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
          <div className="text-sm text-neutral-700">
            © {new Date().getFullYear()} AreWeGoing
          </div>
          <div className="flex gap-6 text-sm text-neutral-600">
            <a className="hover:text-neutral-900" href="#privacy">Privacy</a>
            <a className="hover:text-neutral-900" href="#terms">Terms</a>
            <a className="hover:text-neutral-900" href="#contact">Contact</a>
          </div>
        </div>
      </div>
    </footer>
  );
}