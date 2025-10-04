"use client";
import Link from "next/link";
import Image from "next/image";
import { useEffect, useState } from "react";
import { FiMenu, FiX } from "react-icons/fi";
import { motion, AnimatePresence } from "framer-motion";

export default function Navbar() {
  const [scrolled, setScrolled] = useState(false);
  const [open, setOpen] = useState(false);

  useEffect(() => {
    const handleScroll = () => setScrolled(window.scrollY > 30);
    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  const linkClass =
    "relative text-xl text-white transition-all duration-300 " +
    "after:absolute after:left-0 after:bottom-0 after:h-[2px] after:w-0 after:bg-[#5ac258] " +
    "after:transition-all after:duration-300 hover:text-[#5ac258] hover:after:w-full";

  return (
    <header
      className={`fixed top-0 left-0 w-full z-50 ${
        scrolled
          ? "bg-black/50 backdrop-blur-lg shadow-lg"
          : "bg-transparent"
      }`}
    >
      <div className="flex items-center justify-between px-6 md:px-12 py-4 relative">
        {/* Logo */}
        <Link href="/" className="flex items-center gap-3">
          <Image
            src="/satellite-new.png"
            alt="SatAirlite Logo"
            width={50}
            height={50}
          />
          <span className="text-2xl md:text-3xl font-bold text-white">
            Sat<span className="text-[#5ac258]">Air</span>lite
          </span>
        </Link>

        {/* Links centrados en desktop */}
        <nav className="hidden md:flex absolute left-1/2 transform -translate-x-1/2 gap-12">
          <Link href="/" className={linkClass}>Home</Link>
          <Link href="/map" className={linkClass}>Map</Link>
          <Link href="/dashboard" className={linkClass}>Dashboard</Link>
          <Link href="/trends" className={linkClass}>Trends</Link>
          <Link href="/alerts" className={linkClass}>Alerts</Link>
        </nav>

        {/* Botón hamburguesa en móvil */}
        <button
          onClick={() => setOpen(!open)}
          className="md:hidden text-3xl text-white z-50"
        >
          {open ? <FiX /> : <FiMenu />}
        </button>
      </div>

      {/* Menú móvil animado */}
      <AnimatePresence>
        {open && (
          <motion.div
            initial={{ opacity: 0, y: -30 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -30 }}
            transition={{ duration: 0.3 }}
            className="md:hidden flex flex-col items-center gap-8 py-8 bg-black/90 backdrop-blur-lg"
          >
            <Link href="/" className={linkClass} onClick={() => setOpen(false)}>Home</Link>
            <Link href="/map" className={linkClass} onClick={() => setOpen(false)}>Map</Link>
            <Link href="/dashboard" className={linkClass} onClick={() => setOpen(false)}>Dashboard</Link>
            <Link href="/trends" className={linkClass} onClick={() => setOpen(false)}>Trends</Link>
            <Link href="/alerts" className={linkClass} onClick={() => setOpen(false)}>Alerts</Link>
          </motion.div>
        )}
      </AnimatePresence>
    </header>
  );
}
