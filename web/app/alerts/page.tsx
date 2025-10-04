"use client";
import { useState } from "react";
import { motion } from "framer-motion";
import { FiMail, FiPhone, FiCheckCircle, FiMapPin } from "react-icons/fi";

const cities = [
  { name: "Monterrey", lat: 25.67, lon: -100.31 },
  { name: "CDMX", lat: 19.43, lon: -99.13 },
  { name: "Houston", lat: 29.76, lon: -95.37 },
];

export default function AlertsPage() {
  const [contact, setContact] = useState("");
  const [type, setType] = useState("email");
  const [city, setCity] = useState(cities[0]);
  const [status, setStatus] = useState<"idle" | "loading" | "success" | "error">("idle");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setStatus("loading");

    const payload = {
      contact,
      preferences: { type, city: city.name, lat: city.lat, lon: city.lon },
    };

    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/alerts/subscribe`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (res.ok) {
        setStatus("success");
        setContact("");
        setTimeout(() => setStatus("idle"), 4000);
      } else {
        throw new Error("Error en la suscripción");
      }
    } catch (error) {
      setStatus("error");
      setTimeout(() => setStatus("idle"), 4000);
    }
  };

  return (
    <section className="relative min-h-screen flex items-center justify-center text-white">
      {/* Background (puedes reemplazar con un video si quieres) */}
      <div className="absolute inset-0 bg-[url('/air-quality.mp4')] bg-cover bg-center -z-20" />
      <div className="absolute inset-0 bg-black/80 backdrop-blur-sm -z-10" />

      <motion.div
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="bg-black/80 p-8 rounded-2xl shadow-2xl w-[90%] md:w-[500px] text-center"
      >
        <h1 className="text-3xl font-bold text-[#5ac258] mb-4">Alertas de Calidad del Aire</h1>
        <p className="text-gray-300 mb-8">
          Suscríbete para recibir notificaciones cuando la calidad del aire empeore en tu ciudad.
        </p>

        <form onSubmit={handleSubmit} className="flex flex-col gap-4">
          {/* Selección de ciudad */}
          <div className="flex items-center gap-2 bg-black/60 border border-gray-700 rounded-xl px-4 py-2">
            <FiMapPin className="text-[#5ac258]" />
            <select
              value={city.name}
              onChange={(e) => {
                const selected = cities.find((c) => c.name === e.target.value);
                if (selected) setCity(selected);
              }}
              className="flex-1 bg-transparent text-white focus:outline-none"
            >
              {cities.map((c) => (
                <option key={c.name} value={c.name}>
                  {c.name}
                </option>
              ))}
            </select>
          </div>

          {/* Tipo de alerta */}
          <div className="flex justify-center gap-6 mb-4">
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="radio"
                name="type"
                value="email"
                checked={type === "email"}
                onChange={(e) => setType(e.target.value)}
                className="accent-[#5ac258]"
              />
              <FiMail /> Email
            </label>
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="radio"
                name="type"
                value="whatsapp"
                checked={type === "whatsapp"}
                onChange={(e) => setType(e.target.value)}
                className="accent-[#5ac258]"
              />
              <FiPhone /> WhatsApp
            </label>
          </div>

          {/* Input de contacto */}
          <input
            type={type === "email" ? "email" : "text"}
            placeholder={
              type === "email"
                ? "Tu correo electrónico"
                : "Tu número de WhatsApp (+52...)"
            }
            value={contact}
            onChange={(e) => setContact(e.target.value)}
            required
            className="p-3 rounded-xl bg-black/60 border border-gray-600 text-white focus:outline-none focus:ring-2 focus:ring-[#5ac258] transition"
          />

          {/* Botón */}
          <button
            type="submit"
            disabled={status === "loading"}
            className="mt-4 bg-[#5ac258] hover:bg-[#6edb6e] text-black font-semibold py-3 rounded-xl transition disabled:opacity-60"
          >
            {status === "loading" ? "Enviando..." : "Suscribirme"}
          </button>
        </form>

        {/* Mensajes */}
        {status === "success" && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="mt-6 flex items-center justify-center gap-2 text-green-400 font-semibold"
          >
            <FiCheckCircle /> ¡Suscripción registrada con éxito para {city.name}!
          </motion.div>
        )}
        {status === "error" && (
          <p className="mt-6 text-red-400 font-semibold">Ocurrió un error al suscribirte 😢</p>
        )}
      </motion.div>
    </section>
  );
}
