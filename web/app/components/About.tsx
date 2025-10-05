"use client";
import { motion } from "framer-motion";
import { FiGlobe, FiCpu, FiCloud, FiActivity } from "react-icons/fi";

export default function About() {
  return (
    <section className="relative w-full bg-gradient-to-b from-[#050510] via-[#0A0A1A] to-[#0b0b15] text-white py-28 px-6 overflow-hidden">
      {/* === Fondo estático ligero === */}
      <div className="absolute inset-0 opacity-5 bg-[url('/stars.png')] bg-cover bg-center pointer-events-none" />

      {/* === Contenido principal === */}
      <div className="relative max-w-6xl mx-auto grid md:grid-cols-2 gap-16 items-center z-10">

        {/* === Texto === */}
        <motion.div
          initial={{ opacity: 0, x: -30 }}
          whileInView={{ opacity: 1, x: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.7, ease: "easeOut" }}
        >
          <h2 className="text-5xl font-extrabold mb-6 leading-tight">
            What is <span className="text-[#5ac258]">SatAirlite?</span>
          </h2>
          <p className="text-lg text-gray-400 leading-relaxed mb-8">
            <span className="text-white font-semibold">SatAirlite</span> is an
            AI-powered platform that merges satellite and ground data to
            deliver real-time air quality insights for healthier, smarter cities.
          </p>

          {/* === Icon blocks (sin motion, solo CSS hover) === */}
          <div className="grid grid-cols-2 gap-5">
            {[
              {
                icon: <FiGlobe className="text-3xl text-[#5ac258]" />,
                title: "Global Data",
                desc: "Satellite-based pollution tracking.",
              },
              {
                icon: <FiCpu className="text-3xl text-[#5ac258]" />,
                title: "AI Forecasts",
                desc: "Predictive models for 24h air quality.",
              },
              {
                icon: <FiCloud className="text-3xl text-[#5ac258]" />,
                title: "Open APIs",
                desc: "Seamless integration with NASA & OpenAQ.",
              },
              {
                icon: <FiActivity className="text-3xl text-[#5ac258]" />,
                title: "Health Insights",
                desc: "Personalized alerts for sensitive groups.",
              },
            ].map((item, i) => (
              <div
                key={i}
                className="flex flex-col bg-[#111122]/70 p-4 rounded-xl border border-[#5ac258]/30 
                hover:border-[#5ac258]/60 hover:scale-[1.02] transition-all duration-300 ease-out will-change-transform"
              >
                {item.icon}
                <p className="font-semibold mt-2 text-white">{item.title}</p>
                <p className="text-sm text-gray-400">{item.desc}</p>
              </div>
            ))}
          </div>
        </motion.div>

        {/* === Imagen central optimizada === */}
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          whileInView={{ opacity: 1, scale: 1 }}
          viewport={{ once: true }}
          transition={{ duration: 0.8, ease: "easeOut" }}
          className="flex justify-center"
        >
          <img
            src="/earth.png"
            alt="SatAirlite Earth visualization"
            className="w-80 h-80 md:w-96 md:h-96 object-contain"
            style={{
              filter: "drop-shadow(0 0 20px #5ac258a0)",
              willChange: "transform",
            }}
          />
        </motion.div>
      </div>

      {/* === Cita final === */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true }}
        transition={{ delay: 0.3, duration: 0.6 }}
        className="text-center mt-20 z-10 relative"
      >
        <p className="text-gray-400 italic text-lg">
          “Merging space technology and human insight — for cleaner skies and smarter decisions.”
        </p>
      </motion.div>
    </section>
  );
}
