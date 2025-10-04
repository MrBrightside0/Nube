"use client";
import { motion } from "framer-motion";
import { FaCity, FaSatelliteDish, FaBolt, FaBrain } from "react-icons/fa";

export default function Stats() {
  const stats = [
    { icon: <FaCity className="text-6xl text-[#5ac258]" />, num: "1,200+", label: "Cities Monitored" },
    { icon: <FaSatelliteDish className="text-6xl text-white" />, num: "NASA", label: "Powered by TEMPO" },
    { icon: <FaBolt className="text-6xl text-yellow-400" />, num: "5 min", label: "Updates Frequency" },
    { icon: <FaBrain className="text-6xl text-pink-500" />, num: "AI", label: "Forecasts with AI" },
  ];

  return (
    <section className="w-full bg-[#0A0A1A] text-white py-24 px-8">
      {/* Título */}
      <div className="max-w-6xl mx-auto text-center mb-16">
        <h2 className="text-4xl font-bold">
          Air Quality <span className="text-[#5ac258]">in Numbers</span>
        </h2>
        <p className="text-gray-400 mt-4">
          Real-time monitoring powered by satellite data and artificial intelligence.
        </p>
      </div>

      {/* Stats grid */}
      <div className="grid md:grid-cols-4 gap-8 max-w-6xl mx-auto">
        {stats.map((stat, i) => (
          <motion.div
            key={i}
            initial={{ opacity: 0, y: 60 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: i * 0.1 }}
            whileHover={{ y: -12, scale: 1.07 }}
            className="bg-black/40 border border-white/10 p-8 rounded-xl shadow-lg text-center transition-all duration-300 hover:shadow-2xl hover:border-[#5ac258]/60"
          >
            {/* Icon */}
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: i * 0.3 }}
              className="flex justify-center mb-4"
            >
              {stat.icon}
            </motion.div>

            {/* Número */}
            <h3 className="text-3xl font-bold">{stat.num}</h3>
            <p className="text-gray-400 mt-2">{stat.label}</p>
          </motion.div>
        ))}
      </div>
    </section>
  );
}
