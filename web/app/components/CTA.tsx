"use client";
import { motion } from "framer-motion";
import Link from "next/link";
import { FiArrowRight, FiCloudLightning, FiUsers } from "react-icons/fi";

export default function CTA() {
  return (
    <section className="relative w-full bg-[#0A0A1A] text-white py-28 px-8 text-center overflow-hidden">
      {/* 🌌 Fondo de estrellas estático */}
      <div className="absolute inset-0 opacity-5 bg-[url('/stars.png')] bg-cover bg-center pointer-events-none" />

      {/* === Contenido principal === */}
      <motion.div
        initial={{ opacity: 0, y: 30 }}
        whileInView={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8 }}
        className="relative z-10 max-w-3xl mx-auto"
      >
        {/* Icono decorativo */}
        <div className="flex justify-center mb-6">
          <FiCloudLightning className="text-[#5ac258] text-5xl drop-shadow-[0_0_10px_#5ac25860]" />
        </div>

        {/* Título principal */}
        <h2 className="text-4xl md:text-5xl font-extrabold mb-6 leading-tight">
          Join us in building a{" "}
          <span className="text-[#5ac258]">cleaner, smarter future</span>
        </h2>

        {/* Descripción */}
        <p className="text-gray-400 text-lg max-w-2xl mx-auto mb-10">
          SatAirlite merges{" "}
          <span className="text-white font-semibold">space technology</span> and{" "}
          <span className="text-white font-semibold">artificial intelligence</span>{" "}
          to empower communities with data-driven environmental awareness.
        </p>

        {/* Botón principal */}
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          whileInView={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.4, duration: 0.6 }}
        >
          <Link
            href="/map"
            className="group inline-flex items-center gap-2 px-10 py-4 bg-[#5ac258] text-black rounded-xl 
            font-bold text-lg shadow-lg transition-all duration-300 hover:scale-[1.05] hover:shadow-[#5ac258]/40"
          >
            <span>Get Started</span>
            <FiArrowRight className="group-hover:translate-x-1 transition-transform duration-300" />
          </Link>
        </motion.div>

        {/* Línea decorativa inferior */}
        <div className="mt-14 flex flex-col items-center space-y-3">
          <div className="w-20 h-[2px] bg-[#5ac258] opacity-60" />
          <div className="flex items-center gap-2 text-gray-400 text-sm">
            <FiUsers className="text-[#5ac258]" />
            <p>Developed by the QuantumSky team for NASA Space Apps Challenge 2025</p>
          </div>
        </div>
      </motion.div>
    </section>
  );
}
