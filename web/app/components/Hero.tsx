"use client";
import Link from "next/link";
import { useEffect, useState } from "react";

export default function Hero() {
  const [offsetY, setOffsetY] = useState(0);

  useEffect(() => {
    const handleScroll = () => setOffsetY(window.scrollY);
    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  return (
    <section className="relative min-h-screen w-full flex flex-col items-center justify-center text-center text-white overflow-hidden px-4">
      {/* Video con parallax */}
      <video
        autoPlay
        muted
        loop
        playsInline
        className="absolute top-0 left-0 right-0 bottom-0 w-full h-full object-cover -z-20"
        style={{ transform: `translateY(${offsetY * 0.2}px)` }}
      >
        <source src="/air-quality.mp4" type="video/mp4" />
        Your browser does not support video.
      </video>

      {/* Overlay */}
      <div
        className="absolute inset-0 bg-black/60 -z-10"
        style={{ transform: `translateY(${offsetY * 0.1}px)` }}
      />

      {/* Contenido */}
      <div
        className="max-w-2xl space-y-6"
        style={{ transform: `translateY(${offsetY * 0.05}px)` }}
      >
        <h1 className="text-4xl md:text-6xl font-bold leading-tight">
          Monitoring the{" "}
          <span className="text-[#5ac258]">Air</span> <br className="md:hidden" />
          for Your Health
          <span className="ml-2 text-[#5ac258] animate-blink">|</span>
        </h1>

        <p className="text-gray-300 text-base md:text-lg">
          Powered by{" "}
          <Link
            href="https://science.nasa.gov/mission/tempo/"
            target="_blank"
            rel="noopener noreferrer"
            className="text-[#3b82f6] font-semibold hover:underline"
          >
            TEMPO (NASA)
          </Link>
        </p>
      </div>
    </section>
  );
}
