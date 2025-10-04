"use client";

import Hero from "./components/Hero";
import About from "./components/About";
import Stats from "./components/Stats";
import Tech from "./components/Tech";
import CTA from "./components/CTA";
import Footer from "./components/Footer";
// Aquí luego importaremos Stats, Tech, CTA cuando los vayas creando
// import Stats from "./components/Stats";
// import Tech from "./components/Tech";
// import CTA from "./components/CTA";

export default function Home() {
  return (
    <main className="w-full">
      {/* Hero Section */}
      <Hero />

      {/* About Section */}
      <About />

      {/* <Stats /> */}
      <Stats />

      {/* <Tech /> */}
      <Tech />

      {/* <CTA /> */}
      <CTA />
      {/* <Footer /> */}
      <Footer />
    </main>
  );
}
