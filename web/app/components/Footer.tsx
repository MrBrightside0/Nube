"use client";
import Link from "next/link";

export default function Footer() {
  return (
    <footer className="w-full bg-black/90 text-gray-400 py-8 mt-24 border-t border-white/10">
      <div className="max-w-6xl mx-auto flex flex-col md:flex-row justify-between items-center px-6 gap-4">
        
        {/* Logo + nombre */}
        <div className="flex items-center gap-2">
          <img
            src="/satellite-new.png"
            alt="SatAirlite Logo"
            className="w-8 h-8"
          />
          <span className="text-white font-bold text-lg">
            Sat<span className="text-[#5ac258]">Air</span>lite
          </span>
        </div>

        {/* Links */}
        <nav className="flex gap-6 text-sm">
          <Link href="/" className="hover:text-white transition">
            Home
          </Link>
          <Link href="/map" className="hover:text-white transition">
            Map
          </Link>
          <Link href="/dashboard" className="hover:text-white transition">
            Dashboard
          </Link>
          <Link href="/trends" className="hover:text-white transition">
            Trends
          </Link>
          <Link href="/alerts" className="hover:text-white transition">
            Alerts
          </Link>
        </nav>

        {/* Derechos */}
        <p className="text-xs text-gray-500 text-center md:text-right">
          © {new Date().getFullYear()} SatAirlite · Powered by{" "}
          <a
            href="https://science.nasa.gov/mission/tempo/"
            target="_blank"
            rel="noopener noreferrer"
            className="text-[#3b82f6] hover:underline"
          >
            TEMPO (NASA)
          </a>
        </p>
      </div>
    </footer>
  );
}
