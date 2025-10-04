"use client";
import { motion } from "framer-motion";

export default function About() {
  return (
    <section className="w-full bg-[#0A0A1A] text-white py-24 px-8">
      <div className="max-w-6xl mx-auto grid md:grid-cols-2 gap-12 items-center">
        {/* Texto */}
        <div>
          <h2 className="text-4xl font-bold mb-6">
            What is <span className="text-[#5ac258]">SatAirlite?</span>
          </h2>
          <p className="text-lg text-gray-400 leading-relaxed">
            SatAirlite is a cutting-edge platform that monitors air quality in
            real time using satellite data and AI. Our mission is simple:
            empower communities and decision-makers with accurate environmental
            insights for a healthier future.
          </p>
        </div>
    
        {/* Imagen animada */}
        <motion.div
          initial={{ opacity: 0, y: 50 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 1 }}
          className="flex justify-center"
        >
          <img
            src="/earth.png"
            alt="SatAirlite globe"
            className="w-64 h-64 drop-shadow-[0_0_25px_#3b82f6]"
          />
        </motion.div>
      </div>
    </section>


  );
}
