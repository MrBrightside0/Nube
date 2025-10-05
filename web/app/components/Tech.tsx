"use client";
import { motion } from "framer-motion";
import { FaSatelliteDish, FaBrain, FaChartLine } from "react-icons/fa";

export default function Tech() {
  const features = [
    {
      icon: <FaSatelliteDish className="text-6xl text-[#5ac258]" />,
      title: "Satellite Data",
      desc: "Leveraging NASA TEMPO and OpenAQ to capture real-time atmospheric data and detect changes at the city level.",
    },
    {
      icon: <FaBrain className="text-6xl text-[#5ac258]" />,
      title: "AI Predictions",
      desc: "Machine learning models forecast pollution trends and provide actionable insights for decision-makers.",
    },
    {
      icon: <FaChartLine className="text-6xl text-[#5ac258]" />,
      title: "Interactive Dashboards",
      desc: "Dynamic, data-driven dashboards visualize current conditions, forecasts, and correlations in a clear, impactful way.",
    },
  ];

  return (
    <section className="relative w-full bg-[#0A0A1A] text-white py-28 px-8 text-center overflow-hidden">
      {/* 🌌 Fondo espacial igual que About */}
      <div className="absolute inset-0 opacity-5 bg-[url('/stars.png')] bg-cover bg-center pointer-events-none" />

      {/* === Contenido principal === */}
      <div className="relative z-10">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 40 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          viewport={{ once: true }}
          className="max-w-6xl mx-auto text-center px-6 mb-20"
        >
          <h2 className="text-4xl md:text-5xl font-extrabold tracking-wide">
            Our <span className="text-[#5ac258]">Technology</span>
          </h2>
          <p className="text-gray-400 mt-4 text-lg max-w-2xl mx-auto">
            SatAirlite fuses{" "}
            <span className="text-white font-semibold">spaceborne intelligence</span> and{" "}
            <span className="text-white font-semibold">AI forecasting</span> to empower
            communities with real-time environmental insights.
          </p>
        </motion.div>

        {/* Feature cards */}
        <div className="grid md:grid-cols-3 sm:grid-cols-2 grid-cols-1 gap-10 max-w-6xl mx-auto px-6">
          {features.map((f, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, y: 80 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: i * 0.15 }}
              viewport={{ once: true }}
              whileHover={{ y: -8, scale: 1.03 }}
              className="relative bg-[#111122]/70 border border-[#5ac258]/20 rounded-2xl p-10 text-center 
              shadow-md transition-all duration-300 hover:border-[#5ac258]/70 hover:shadow-[0_0_25px_#5ac25830]"
              style={{ willChange: "transform" }}
            >
              {/* Icon */}
              <div className="relative flex justify-center mb-6 drop-shadow-[0_0_10px_rgba(90,194,88,0.3)]">
                {f.icon}
              </div>

              {/* Title */}
              <h3 className="text-2xl md:text-3xl font-semibold mb-3 text-[#5ac258] tracking-wide">
                {f.title}
              </h3>

              {/* Divider */}
              <div className="w-16 h-[2px] bg-[#5ac258] mx-auto mb-4 opacity-60" />

              {/* Description */}
              <p className="text-gray-400 text-sm leading-relaxed">{f.desc}</p>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
