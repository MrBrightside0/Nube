"use client";
import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import {
  FiMail,
  FiPhone,
  FiCheckCircle,
  FiMapPin,
  FiAlertTriangle,
} from "react-icons/fi";
import Image from "next/image";
import Footer from "../components/Footer";

const cities = [
  { name: "Monterrey", lat: 25.67, lon: -100.31 },
  { name: "Mexico City", lat: 19.43, lon: -99.13 },
  { name: "Houston", lat: 29.76, lon: -95.37 },
];

export default function AlertsPage() {
  const [contact, setContact] = useState("");
  const [type, setType] = useState<"email" | "whatsapp">("email");
  const [city, setCity] = useState(cities[0]);
  const [cityInput, setCityInput] = useState(cities[0].name);
  const [aqi, setAqi] = useState<number | null>(null);
  const [status, setStatus] = useState<"idle" | "loading" | "success" | "error">(
    "idle"
  );

  useEffect(() => {
    const fetchAQI = async () => {
      try {
        const res = await fetch(
          `${process.env.NEXT_PUBLIC_API_URL}/aq/latest?lat=${city.lat}&lon=${city.lon}`
        );
        const data = await res.json();
        setAqi(data.aqi ?? null);
      } catch {
        setAqi(null);
      }
    };
    fetchAQI();
  }, [city]);

  const handleCityChange = (value: string) => {
    setCityInput(value);
    const match = cities.find(
      (c) => c.name.toLowerCase() === value.toLowerCase()
    );
    if (match) setCity(match);
    else
      setCity({
        name: value,
        lat: 0,
        lon: 0,
      }); // fallback (user-defined)
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!contact.trim()) return;
    setStatus("loading");

    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/alerts/subscribe`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          contact,
          preferences: { type, city: city.name, lat: city.lat, lon: city.lon },
        }),
      });

      if (!res.ok) throw new Error("Subscription failed");
      setStatus("success");
      setContact("");
      setTimeout(() => setStatus("idle"), 4000);
    } catch {
      setStatus("error");
      setTimeout(() => setStatus("idle"), 4000);
    }
  };

  return (
    <section className="pt-44 relative flex flex-col min-h-screen justify-between text-white overflow-hidden">
      {/* ✅ Background image */}
      <div className="absolute inset-0 -z-20">
        <Image
          src="/fondo-contacto.png"
          alt="background"
          fill
          priority
          quality={90}
          className="object-cover object-center"
        />
      </div>

      {/* ✅ Overlay */}
      <div className="absolute inset-0 bg-black/65 -z-10" />
      <div className="absolute inset-0 bg-stars -z-30" />

      {/* 🔹 Branding */}
      <motion.div
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8 }}
        className="flex flex-col items-center justify-center mb-6"
      >
        <Image
          src="/satellite-new.png"
          alt="SatAirlite Logo"
          width={90}
          height={90}
          className="drop-shadow-[0_0_10px_#5ac25860]"
        />
        <h1 className="text-4xl font-bold mt-2 tracking-wide text-white">
          Sat<span className="text-[#5ac258]">Air</span>lite
        </h1>
        <p className="text-gray-400 text-sm mt-1">
          Empowering smarter air-quality decisions.
        </p>
      </motion.div>

      {/* 🔹 Main content */}
      <div className="flex flex-col items-center justify-center px-6 py-10 flex-1">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4, ease: "easeOut" }}
          className="bg-black/70 backdrop-blur-sm rounded-2xl w-full max-w-md p-8 text-center border border-gray-700 shadow-lg shadow-black/40"
        >
          <h2 className="text-2xl font-bold mb-3 text-[#5ac258]">
            Air Quality Alerts
          </h2>
          <p className="text-gray-300 mb-8 text-sm">
            Enter your city or country to receive instant air quality updates.
          </p>

          {/* FORM */}
          <form onSubmit={handleSubmit} className="flex flex-col gap-4">
            {/* City input (replaces dropdown) */}
            <div className="flex items-center gap-2 bg-black/40 border border-gray-700 rounded-xl px-4 py-2">
              <FiMapPin className="text-[#5ac258]" />
              <input
                type="text"
                placeholder="Enter your city or country"
                value={cityInput}
                onChange={(e) => handleCityChange(e.target.value)}
                className="flex-1 bg-transparent text-white focus:outline-none"
              />
            </div>

            {/* Contact method */}
            <div className="flex justify-center gap-6 text-sm">
              {[{ label: "Email", value: "email", icon: <FiMail /> },
                { label: "WhatsApp", value: "whatsapp", icon: <FiPhone /> }].map((opt) => (
                <label
                  key={opt.value}
                  className={`flex items-center gap-2 cursor-pointer transition ${
                    type === opt.value ? "text-[#5ac258]" : "text-gray-300"
                  }`}
                >
                  <input
                    type="radio"
                    name="type"
                    value={opt.value}
                    checked={type === opt.value}
                    onChange={(e) =>
                      setType(e.target.value as "email" | "whatsapp")
                    }
                    className="accent-[#5ac258]"
                  />
                  {opt.icon} {opt.label}
                </label>
              ))}
            </div>

            {/* Contact input */}
            <input
              type={type === "email" ? "email" : "text"}
              placeholder={
                type === "email"
                  ? "Your email address"
                  : "Your WhatsApp number (+52...)"
              }
              value={contact}
              onChange={(e) => setContact(e.target.value)}
              required
              className="p-3 rounded-xl bg-black/40 border border-gray-700 text-white placeholder-gray-400 focus:outline-none focus:ring-1 focus:ring-[#5ac258] transition"
            />

            {/* Submit */}
            <button
              type="submit"
              disabled={status === "loading"}
              className="mt-3 bg-[#5ac258] hover:bg-[#6edb6e] text-black font-semibold py-3 rounded-xl transition disabled:opacity-60"
            >
              {status === "loading" ? "Sending..." : "Subscribe"}
            </button>

            {/* Status messages */}
            {status === "success" && (
              <p className="mt-5 flex items-center justify-center gap-2 text-green-400 text-sm font-semibold">
                <FiCheckCircle /> Subscription successful for {city.name}!
              </p>
            )}
            {status === "error" && (
              <p className="mt-5 flex items-center justify-center gap-2 text-red-400 text-sm font-semibold">
                <FiAlertTriangle /> Something went wrong. Try again.
              </p>
            )}
          </form>

          {/* AQI info */}
          {aqi !== null && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className="mt-8 p-4 bg-black/40 border border-gray-700 rounded-xl text-left text-sm"
            >
              <h3 className="text-lg font-semibold mb-2 text-[#5ac258]">
                Current Air Quality — {city.name}
              </h3>
              <p className="text-gray-300">
                AQI: <span className="text-white font-bold">{aqi}</span>
              </p>
              <p className="text-gray-400">
                Status:{" "}
                {aqi > 150
                  ? "Unhealthy"
                  : aqi > 100
                  ? "Moderate"
                  : "Good"}
              </p>
            </motion.div>
          )}

          {/* Info grid */}
          <div className="mt-10 grid grid-cols-1 sm:grid-cols-3 gap-6 text-gray-300 text-xs">
            <div className="flex flex-col items-center text-center">
              <FiAlertTriangle className="text-[#5ac258] text-2xl mb-2" />
              <p>Get notified when air quality drops.</p>
            </div>
            <div className="flex flex-col items-center text-center">
              <FiMail className="text-[#5ac258] text-2xl mb-2" />
              <p>Personalized alerts via Email or WhatsApp.</p>
            </div>
            <div className="flex flex-col items-center text-center">
              <FiMapPin className="text-[#5ac258] text-2xl mb-2" />
              <p>Tailored by your city or country.</p>
            </div>
          </div>
        </motion.div>
      </div>

      <Footer />
    </section>
  );
}
