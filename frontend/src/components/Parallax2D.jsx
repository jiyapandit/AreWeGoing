import { motion, useScroll, useTransform } from "framer-motion";

export default function Parallax2D() {
  const { scrollYProgress } = useScroll();

  // Back layer moves slowest
  const yBack = useTransform(scrollYProgress, [0, 1], [0, -80]);

  // Middle layer moves mid range
  const yMid = useTransform(scrollYProgress, [0, 1], [0, -160]);

  // Front layer moves fastest
  const yFront = useTransform(scrollYProgress, [0, 1], [0, -230]);

  return (
    <section className="relative h-screen overflow-hidden">
      {/* BACKGROUND LAYER */}
      <motion.div
        style={{ y: yBack }}
  className="absolute inset-0 will-change-transform"
      >
        <img
          src="https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=2000"
          alt="background"
          className="h-full w-full object-cover"
        />
      </motion.div>

      {/* MIDDLE ELEMENT */}
      <motion.div
        style={{ y: yMid }}
        className="absolute top-1/4 left-1/2 -translate-x-1/2"
      >
        <div className="bg-white/80 p-6 rounded-3xl text-black shadow-xl">
          <h2 className="text-3xl font-bold">Welcome to AreWeGoing</h2>
          <p className="mt-2 text-lg">Scroll for motion depth effect</p>
        </div>
      </motion.div>

      {/* FOREGROUND ELEMENT */}
      <motion.div
        style={{ y: yFront }}
        className="absolute bottom-10 right-10"
      >
        <div className="bg-white/90 p-4 rounded-full shadow-lg">
          🧭 Travel Depth
        </div>
      </motion.div>

      
    </section>
  );
}