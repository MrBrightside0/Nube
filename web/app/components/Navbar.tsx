"use client";
import Link from "next/link";
import Image from "next/image";
import { useEffect, useState } from "react";
import { FiMenu, FiX } from "react-icons/fi";
import { motion, AnimatePresence } from "framer-motion";
import { usePathname } from "next/navigation";

export default function Navbar() {
  const [scrolled, setScrolled] = useState(false);
  const [open, setOpen] = useState(false);
  const pathname = usePathname();

  // 🔹 Detecta scroll solo si pasa cierto umbral
  useEffect(() => {
    const handleScroll = () => setScrolled(window.scrollY > 120);
    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  const linkBase =
    "relative text-xl transition-all duration-300 after:absolute after:left-0 after:bottom-0 after:h-[2px] after:bg-[#5ac258] after:transition-all after:duration-300";
  const linkDefault = `${linkBase} text-white after:w-0 hover:text-[#5ac258] hover:after:w-full`;
  const linkActive = `${linkBase} text-[#5ac258] after:w-full`;

  const links = [
    { href: "/", label: "Home" },
    { href: "/map", label: "Map" },
    { href: "/dashboard", label: "Dashboard" },
    { href: "/trends", label: "Trends" },
    { href: "/alerts", label: "Alerts" },
  ];

  return (
    <motion.header
      initial={false}
      animate={{
        backgroundColor: scrolled
          ? "rgba(0, 0, 0, 0.85)"
          : "rgba(0, 0, 0, 0.0)",
        boxShadow: scrolled
          ? "0 8px 25px rgba(0,0,0,0.5)"
          : "0 0px 0px rgba(0,0,0,0)",
        opacity: scrolled ? 1 : 0.95,
        y: scrolled ? 0 : -2,
      }}
      transition={{
        duration: 0.6,
        ease: "easeInOut",
      }}
      style={{
        position: "fixed",
        top: 5,
        left: 0,
        width: "100%",
        zIndex: 50,
        backdropFilter: scrolled ? "blur(12px)" : "none",
        WebkitBackdropFilter: scrolled ? "blur(12px)" : "none",
        transition: "background-color 0.6s ease, box-shadow 0.6s ease, backdrop-filter 0.6s ease",
      }}
    >
      <div className="flex items-center justify-between px-6 md:px-12 py-4 relative">
        {/* Logo */}
        <Link href="/" className="flex items-center gap-3">
          <motion.div
            animate={{
              scale: scrolled ? 0.9 : 1,
              opacity: scrolled ? 0.9 : 1,
            }}
            transition={{ duration: 0.4 }}
          >
            <Image
              src="/satellite-new.png"
              alt="SatAirlite Logo"
              width={50}
              height={50}
            />
          </motion.div>
          <span className="text-2xl md:text-3xl font-bold text-white">
            Sat<span className="text-[#5ac258]">Air</span>lite
          </span>
        </Link>

        {/* Links desktop */}
        <nav className="hidden md:flex absolute left-1/2 transform -translate-x-1/2 gap-12">
          {links.map((link) => (
            <Link
              key={link.href}
              href={link.href}
              className={pathname === link.href ? linkActive : linkDefault}
            >
              {link.label}
            </Link>
          ))}
        </nav>

        {/* Menú móvil */}
        <button
          onClick={() => setOpen(!open)}
          className="md:hidden text-3xl text-white z-50"
        >
          {open ? <FiX /> : <FiMenu />}
        </button>
      </div>

      {/* Menú móvil */}
      <AnimatePresence>
        {open && (
          <motion.div
            initial={{ opacity: 0, y: -30 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -30 }}
            transition={{ duration: 0.3 }}
            className="md:hidden flex flex-col items-center gap-8 py-8 bg-black/90 backdrop-blur-lg"
          >
            {links.map((link) => (
              <Link
                key={link.href}
                href={link.href}
                onClick={() => setOpen(false)}
                className={pathname === link.href ? linkActive : linkDefault}
              >
                {link.label}
              </Link>
            ))}
          </motion.div>
        )}
      </AnimatePresence>
    </motion.header>
  );
}
