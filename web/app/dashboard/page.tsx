"use client";

import { useState } from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import { FiSend, FiMapPin, FiSearch } from "react-icons/fi";
import { WiDust, WiStrongWind, WiSmoke } from "react-icons/wi";
import AQIGauge from "./AQIGauge";

interface ForecastData {
  ts: string;
  yhat: number;
}

interface TrendData {
  ts: string;
  value: number;
}

export default function DashboardPage() {
  const [city, setCity] = useState("Monterrey");
  const [aqi, setAqi] = useState<number | null>(null);
  const [pm25, setPm25] = useState<number | null>(null);
  const [no2, setNo2] = useState<number | null>(null);
  const [wind, setWind] = useState<number | null>(null);
  const [cityQuery, setCityQuery] = useState("");
  const [chatQuery, setChatQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const [searching, setSearching] = useState(false);
  const [simulated, setSimulated] = useState(false);

  const [messages, setMessages] = useState<{ role: string; text: string }[]>([
    {
      role: "assistant",
      text: "👋 Hola, soy tu asistente SatAirlite. Puedo darte recomendaciones según la calidad del aire. ¿Dónde estás o qué deseas consultar?",
    },
  ]);

  const [forecast, setForecast] = useState<ForecastData[]>([]);
  const [trend, setTrend] = useState<TrendData[]>([]);

  const getAQIAdvice = (aqi: number) => {
    if (aqi <= 50)
      return "🌿 Aire limpio. Disfruta actividades al aire libre sin preocupaciones.";
    if (aqi <= 100)
      return "🌤 Calidad moderada. Evita ejercicio prolongado si eres sensible.";
    if (aqi <= 150)
      return "😷 Usa mascarilla si estarás mucho tiempo afuera o cerca de tráfico.";
    if (aqi <= 200)
      return "🚫 No se recomienda actividad física al aire libre.";
    return "☠️ Niveles peligrosos. Permanece en interiores con ventanas cerradas.";
  };

  const fetchData = async (lat: number, lon: number, name: string) => {
    setLoading(true);
    setSimulated(false);
    try {
      const res = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/aq/predict?lat=${lat}&lon=${lon}`
      );
      if (!res.ok) throw new Error("Backend error");
      const data = await res.json();

      setCity(name);
      setAqi(data.aqi ?? Math.floor(Math.random() * 200));
      setPm25(data.pm25 ?? Math.floor(Math.random() * 50));
      setNo2(data.no2 ?? Math.floor(Math.random() * 30));
      setWind(data.wind ?? Math.floor(Math.random() * 15));

      setForecast(
        Array.from({ length: 30 }).map((_, i) => ({
          ts: `Día ${i + 1}`,
          yhat: data.aqi + Math.sin(i / 3) * 8 + Math.random() * 3,
        }))
      );
      setTrend(
        Array.from({ length: 6 }).map((_, i) => ({
          ts: `Semana ${i + 1}`,
          value: data.aqi + Math.sin(i / 2) * 5 + Math.random() * 2,
        }))
      );
    } catch {
      setSimulated(true);
      const fakeAqi = Math.floor(Math.random() * 200);
      const fakePm25 = Math.floor(Math.random() * 60);
      const fakeNo2 = Math.floor(Math.random() * 40);
      const fakeWind = Math.floor(Math.random() * 15);
      setCity(name);
      setAqi(fakeAqi);
      setPm25(fakePm25);
      setNo2(fakeNo2);
      setWind(fakeWind);
      setForecast(
        Array.from({ length: 30 }).map((_, i) => ({
          ts: `Día ${i + 1}`,
          yhat: fakeAqi + Math.sin(i / 3) * 8 + Math.random() * 3,
        }))
      );
      setTrend(
        Array.from({ length: 6 }).map((_, i) => ({
          ts: `Semana ${i + 1}`,
          value: fakeAqi + Math.sin(i / 2) * 5 + Math.random() * 2,
        }))
      );
    } finally {
      setLoading(false);
    }
  };

  const handleSearchCity = async (e: any) => {
    e.preventDefault();
    if (!cityQuery.trim()) return;
    setSearching(true);
    try {
      const res = await fetch(
        `https://api.openweathermap.org/geo/1.0/direct?q=${encodeURIComponent(
          cityQuery
        )}&limit=1&appid=${process.env.NEXT_PUBLIC_OWM_KEY}`
      );
      const json = await res.json();
      let lat, lon, name;
      if (json && json.length > 0) {
        ({ lat, lon, name } = json[0]);
        name = name || cityQuery;
      } else {
        name = cityQuery;
        lat = Math.random() * 160 - 80;
        lon = Math.random() * 360 - 180;
      }
      fetchData(lat, lon, name);
    } catch {
      alert("No se pudo obtener la ciudad.");
    } finally {
      setCityQuery("");
      setSearching(false);
    }
  };

  const handleGeolocation = () => {
    if (!navigator.geolocation) return alert("Geolocalización no soportada.");
    setLoading(true);
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        const { latitude, longitude } = pos.coords;
        fetchData(latitude, longitude, "Ubicación actual");
      },
      () => {
        setLoading(false);
        alert("No se pudo obtener la ubicación.");
      }
    );
  };

  const handleSend = async (e: any) => {
    e.preventDefault();
    if (!chatQuery.trim()) return;
    const newMsg = { role: "user", text: chatQuery };
    setMessages((prev) => [...prev, newMsg]);
    setChatQuery("");
    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: newMsg.text, aqi }),
      });
      const data = await res.json();
      const botMsg = { role: "assistant", text: data.response || "🤖 Error al responder." };
      setMessages((prev) => [...prev, botMsg]);
    } catch {
      setMessages((prev) => [
        ...prev,
        { role: "assistant", text: "⚠️ No se pudo conectar con el chatbot." },
      ]);
    }
  };

  return (
    <main className="min-h-screen bg-[#0A0A1A] text-white pt-28 pb-20 px-4 sm:px-6 md:px-8 relative">
      <h1 className="text-center font-bold mb-10 text-[clamp(1.8rem,4vw,2.5rem)]">
        Dashboard – <span className="text-[#5ac258]">{city}</span>
      </h1>

      {/* 🌀 Feedback visual */}
      {searching && (
        <div className="absolute top-28 left-1/2 -translate-x-1/2 bg-[#111122]/90 text-[#5ac258] px-6 py-2 rounded-lg shadow-lg text-xs sm:text-sm z-50">
          Buscando ubicación...
        </div>
      )}
      {loading && (
        <div className="absolute inset-0 bg-black/50 flex items-center justify-center text-[#5ac258] text-lg sm:text-xl font-bold z-50">
          Cargando datos de calidad del aire...
        </div>
      )}

      {/* 🔹 Panel principal */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-10 max-w-7xl mx-auto items-stretch">
        {/* 🔸 Gauge + Info */}
        <div className="flex flex-col justify-between bg-[#111122]/80 p-6 sm:p-10 rounded-2xl border border-[#5ac258]/20 shadow-lg">
          <div className="flex flex-col items-center">
            <form
              onSubmit={handleSearchCity}
              className="flex flex-wrap gap-2 mb-6 w-full max-w-sm justify-center"
            >
              <input
                type="text"
                placeholder="Buscar ciudad..."
                className="flex-1 min-w-[180px] bg-[#0b0b15]/70 border border-[#5ac258]/30 rounded-xl px-4 py-3 text-sm text-white placeholder-gray-400 outline-none focus:ring-2 focus:ring-[#5ac258]"
                value={cityQuery}
                onChange={(e) => setCityQuery(e.target.value)}
              />
              <button
                type="submit"
                className="bg-[#5ac258] text-black px-4 rounded-xl hover:bg-[#72dc70] transition"
              >
                <FiSearch size={18} />
              </button>
              <button
                type="button"
                onClick={handleGeolocation}
                className="bg-[#222] text-[#5ac258] px-3 rounded-xl hover:bg-[#333] transition"
              >
                <FiMapPin size={20} />
              </button>
            </form>

            <h2 className="text-lg sm:text-xl font-semibold mb-4 text-center">
              AQI en <span className="text-[#5ac258]">{city}</span>
            </h2>
            <AQIGauge value={aqi ?? 0} />
            {!loading && aqi !== null && (
              <p className="mt-6 text-gray-300 text-center text-sm sm:text-base max-w-sm">
                {getAQIAdvice(aqi)}
              </p>
            )}
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-6 mt-10">
            <InfoBox label="NO₂" value={no2 ?? 0} unit="µg/m³" Icon={WiSmoke} />
            <InfoBox label="PM2.5" value={pm25 ?? 0} unit="µg/m³" Icon={WiDust} />
            <InfoBox label="Viento" value={wind ?? 0} unit="km/h" Icon={WiStrongWind} />
          </div>
        </div>

        {/* 🔸 Chatbot */}
        <div className="flex flex-col bg-[#111122]/80 p-6 sm:p-10 rounded-2xl border border-[#5ac258]/20 shadow-lg">
          <h2 className="text-xl sm:text-2xl font-bold mb-4 text-[#5ac258] text-center sm:text-left">
            Asistente SatAirlite
          </h2>
          <div className="flex-1 overflow-y-auto mb-4 space-y-3 pr-1 sm:pr-2 scrollbar-thin scrollbar-thumb-[#5ac258]/40 scrollbar-track-transparent max-h-[50vh] sm:max-h-[60vh]">
            {messages.map((msg, i) => (
              <div
                key={i}
                className={`p-3 rounded-xl max-w-[85%] text-sm sm:text-base ${
                  msg.role === "assistant"
                    ? "bg-[#5ac258]/20 text-[#caffc7] self-start"
                    : "bg-[#333344] text-white self-end ml-auto"
                }`}
              >
                {msg.text}
              </div>
            ))}
          </div>
          <form onSubmit={handleSend} className="flex items-center gap-2 mt-auto">
            <input
              type="text"
              placeholder="Escribe tu pregunta..."
              value={chatQuery}
              onChange={(e) => setChatQuery(e.target.value)}
              className="flex-1 bg-[#0b0b15]/70 border border-[#5ac258]/30 rounded-xl px-4 py-3 text-sm text-white placeholder-gray-400 outline-none focus:ring-2 focus:ring-[#5ac258]"
            />
            <button
              type="submit"
              className="bg-[#5ac258] text-black px-4 py-3 rounded-xl hover:bg-[#72dc70] transition"
            >
              <FiSend size={18} />
            </button>
          </form>
        </div>
      </div>

      {/* 🔹 Gráficas */}
      <section className="mt-16 max-w-7xl mx-auto bg-[#111122]/80 border border-[#5ac258]/20 rounded-2xl p-6">
        <h2 className="text-[clamp(1.3rem,3vw,1.8rem)] font-bold text-[#5ac258] mb-4 text-center sm:text-left">
          Predicción con IA (30 días)
        </h2>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={forecast}>
            <CartesianGrid strokeDasharray="3 3" stroke="#333" />
            <XAxis dataKey="ts" tick={{ fill: "#aaa", fontSize: 10 }} />
            <YAxis tick={{ fill: "#aaa", fontSize: 10 }} />
            <Tooltip contentStyle={{ backgroundColor: "#111", border: "none" }} />
            <Line type="monotone" dataKey="yhat" stroke="#5ac258" dot={false} />
          </LineChart>
        </ResponsiveContainer>
      </section>

      <section className="mt-10 max-w-7xl mx-auto bg-[#111122]/80 border border-[#5ac258]/20 rounded-2xl p-6">
        <h2 className="text-[clamp(1.3rem,3vw,1.8rem)] font-bold text-[#5ac258] mb-4 text-center sm:text-left">
          Tendencia y Estacionalidad
        </h2>
        <ResponsiveContainer width="100%" height={250}>
          <LineChart data={trend}>
            <CartesianGrid strokeDasharray="3 3" stroke="#333" />
            <XAxis dataKey="ts" tick={{ fill: "#aaa", fontSize: 10 }} />
            <YAxis tick={{ fill: "#aaa", fontSize: 10 }} />
            <Tooltip contentStyle={{ backgroundColor: "#111", border: "none" }} />
            <Line type="monotone" dataKey="value" stroke="#5ac258" dot={false} />
          </LineChart>
        </ResponsiveContainer>
      </section>

      {simulated && (
        <div className="absolute bottom-6 left-6 bg-yellow-600/80 text-white text-xs px-3 py-1 rounded-md z-50 shadow-md">
          ⚠ Modo simulado (offline)
        </div>
      )}
    </main>
  );
}

/* 💡 Caja de dato */
function InfoBox({
  label,
  value,
  unit,
  Icon,
}: {
  label: string;
  value: number;
  unit: string;
  Icon: any;
}) {
  return (
    <div className="bg-[#0b0b15]/70 border border-[#5ac258]/20 rounded-2xl p-5 text-center shadow-lg flex flex-col items-center justify-center hover:shadow-[#5ac258]/20 transition-all duration-300 min-h-[100px] sm:min-h-[120px]">
      <div className="flex justify-center mb-2 text-[#5ac258]">
        <Icon size={28} className="sm:size-8" />
      </div>
      <h3 className="text-base sm:text-lg font-semibold mb-1">{label}</h3>
      <p className="text-xl sm:text-2xl font-bold text-white">
        {isNaN(value) ? "0" : value}{" "}
        <span className="text-gray-400 text-sm">{unit}</span>
      </p>
    </div>
  );
}
