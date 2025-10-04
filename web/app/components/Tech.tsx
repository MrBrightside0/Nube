"use client";
import { motion } from "framer-motion";
import { FaSatelliteDish, FaBrain, FaChartLine } from "react-icons/fa";

export default function Tech() {
  const features = [
    {
      icon: <FaSatelliteDish className="text-6xl text-[#5ac258]" />,
      title: "Satellite Data",
      desc: "Leveraging NASA TEMPO and OpenAQ to capture real-time atmospheric data.",
    },
    {
      icon: <FaBrain className="text-6xl text-[#5ac258]" />,
      title: "AI Predictions",
      desc: "Machine Learning models forecast pollution levels with unmatched precision.",
    },
    {
      icon: <FaChartLine className="text-6xl text-[#5ac258]" />,
      title: "Interactive Dashboards",
      desc: "Clean, dynamic visualizations for decision-makers and communities.",
    },
  ];

  return (
    <section className="w-full bg-[#0A0A1A] text-white py-24 px-8">
      {/* Título */}
      <div className="max-w-6xl mx-auto text-center mb-16">
        <h2 className="text-4xl font-bold">
          Our <span className="text-[#5ac258]">Technology</span>
        </h2>
        <p className="text-gray-400 mt-4 max-w-2xl mx-auto">
          SatAirlite combines cutting-edge space technology with artificial intelligence
          to deliver actionable insights for a cleaner, healthier future.
        </p>
      </div>

      {/* Features grid */}
      <div className="grid md:grid-cols-3 gap-10 max-w-6xl mx-auto">
        {features.map((f, i) => (
          <motion.div
            key={i}
            initial={{ opacity: 0, y: 40 }}
            whileInView={{ opacity: 1, y: 0 }}
            whileHover={{ y: -12, scale: 1.07 }}
            transition={{ duration: 0.8, delay: i * 0.2 }}
            className="bg-black/40 border border-white/10 p-10 rounded-2xl shadow-lg text-center transition-all duration-300 hover:shadow-2xl hover:border-[#5ac258]/60"
          >
            {/* Icon */}
            <div className="flex justify-center mb-6">{f.icon}</div>

            {/* Title */}
            <h3 className="text-2xl font-semibold mb-3">{f.title}</h3>

            {/* Description */}
            <p className="text-gray-400">{f.desc}</p>
          </motion.div>
        ))}
      </div>
    </section>
  );
}
