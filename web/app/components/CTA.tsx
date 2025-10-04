"use client";
import { motion } from "framer-motion";
import Link from "next/link";

export default function CTA() {
  return (
    <section className="w-full bg-black text-white py-24 px-8 text-center relative overflow-hidden">
      {/* Glow decorativo */}
      <div className="absolute inset-0 bg-gradient-to-r from-[#5ac258]/20 via-transparent to-[#3b82f6]/20 blur-3xl -z-10"></div>

      <motion.h2
        initial={{ opacity: 0, y: 30 }}
        whileInView={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8 }}
        className="text-4xl md:text-5xl font-bold mb-6"
      >
        Join us in building a{" "}
        <span className="text-[#5ac258]">cleaner future</span>
      </motion.h2>

      <motion.p
        initial={{ opacity: 0 }}
        whileInView={{ opacity: 1 }}
        transition={{ delay: 0.4, duration: 0.8 }}
        className="text-gray-400 text-lg mb-10"
      >
        Explore SatAirlite and see how technology is reshaping our air.
      </motion.p>

      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        whileInView={{ opacity: 1, scale: 1 }}
        transition={{ delay: 0.6, duration: 0.6 }}
      >
        <Link
          href="/map"
          className="px-10 py-4 bg-[#5ac258] hover:bg-[#3b82f6] rounded-xl font-bold text-lg shadow-lg transition-all duration-300 hover:shadow-[#5ac258]/50"
        >
          Get Started →
        </Link>
      </motion.div>
    </section>
  );
}
