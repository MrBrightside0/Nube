"use client";
import { motion } from "framer-motion";
import {
  FaCity,
  FaSatelliteDish,
  FaBolt,
  FaBrain,
} from "react-icons/fa";

export default function Stats() {
  const stats = [
    {
      icon: <FaCity className="text-6xl text-[#5ac258]" />,
      num: "1,200+",
      label: "Cities Monitored",
      desc: "Urban and rural air quality coverage worldwide.",
    },
    {
      icon: <FaSatelliteDish className="text-6xl text-white" />,
      num: "NASA",
      label: "Powered by TEMPO",
      desc: "Real-time satellite observations from space.",
    },
    {
      icon: <FaBolt className="text-6xl text-yellow-400" />,
      num: "5 min",
      label: "Update Frequency",
      desc: "Continuous refresh of pollution data and trends.",
    },
    {
      icon: <FaBrain className="text-6xl text-pink-500" />,
      num: "AI",
      label: "Forecast Engine",
      desc: "Machine learning models predict air quality shifts.",
    },
  ];

  return (
    <section className="relative w-full py-28 overflow-hidden text-white">
      {/* 🌌 Background */}
      <div className="absolute inset-0 bg-gradient-to-br from-black via-[#0A0A1A] to-[#041004] -z-20" />
      <div className="absolute inset-0 bg-stars opacity-40 -z-10" />

      {/* Title */}
      <motion.div
        initial={{ opacity: 0, y: 40 }}
        whileInView={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8 }}
        viewport={{ once: true }}
        className="max-w-6xl mx-auto text-center px-6 mb-16"
      >
        <h2 className="text-4xl md:text-5xl font-extrabold tracking-wide">
          Air Quality <span className="text-[#5ac258]">in Numbers</span>
        </h2>
        <p className="text-gray-400 mt-4 text-lg max-w-2xl mx-auto">
          Monitoring powered by <span className="text-white font-semibold">NASA TEMPO</span> and advanced artificial intelligence systems.
        </p>
      </motion.div>

      {/* Stats Grid */}
      <div className="grid md:grid-cols-4 sm:grid-cols-2 grid-cols-1 gap-10 max-w-6xl mx-auto px-6">
        {stats.map((stat, i) => (
          <motion.div
            key={i}
            initial={{ opacity: 0, y: 80 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: i * 0.15 }}
            viewport={{ once: true }}
            whileHover={{ y: -10, scale: 1.05 }}
            className="relative bg-black/50 border border-white/10 rounded-2xl p-8 text-center shadow-lg transition-all duration-300 hover:border-[#5ac258]/70 hover:shadow-[0_0_25px_#5ac25830]"
          >
            {/* Halo */}
            <motion.div
              className="absolute inset-0 rounded-2xl bg-[#5ac258]/10 opacity-0 hover:opacity-100 blur-2xl transition-opacity duration-500"
              whileHover={{ scale: 1.1 }}
            />
            {/* Icon */}
            <div className="relative flex justify-center mb-5">
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: i * 0.2 }}
                className="drop-shadow-[0_0_8px_rgba(90,194,88,0.5)]"
              >
                {stat.icon}
              </motion.div>
            </div>
            {/* Number */}
            <h3 className="text-3xl md:text-4xl font-bold text-white">
              {stat.num}
            </h3>
            <p className="text-[#5ac258] mt-1 text-lg font-medium">
              {stat.label}
            </p>
            <p className="text-gray-400 text-sm mt-3">{stat.desc}</p>
          </motion.div>
        ))}
      </div>
    </section>
  );
}
