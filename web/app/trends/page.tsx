"use client";

import { useEffect, useState } from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ScatterChart,
  Scatter,
} from "recharts";
import { motion } from "framer-motion";
import Footer from "../components/Footer";
import {
  FiActivity,
  FiTrendingUp,
  FiAlertTriangle,
  FiWind,
  FiHeart,
  FiSearch,
} from "react-icons/fi";

export default function TrendsPage() {
  const [city, setCity] = useState("Monterrey");
  const [coords, setCoords] = useState({ lat: 25.67, lon: -100.31 });
  const [trends, setTrends] = useState<any[]>([]);
  const [corr, setCorr] = useState<number | null>(null);
  const [loading, setLoading] = useState(true);

  // 🔹 Obtener coordenadas desde OpenWeather
  const fetchCityCoords = async (name: string) => {
    try {
      const geo = await fetch(
        `https://api.openweathermap.org/geo/1.0/direct?q=${encodeURIComponent(
          name
        )}&limit=1&appid=${process.env.NEXT_PUBLIC_OWM_KEY}`
      );
      const data = await geo.json();
      if (data.length > 0) {
        setCoords({ lat: data[0].lat, lon: data[0].lon });
        setCity(data[0].name || name);
      } else {
        simulateData(name);
      }
    } catch (err) {
      console.error("Error fetching city coordinates:", err);
      simulateData(name);
    }
  };

  // 🔹 Función principal: obtener datos del backend o simular
  const fetchTrends = async (lat: number, lon: number, name?: string) => {
    setLoading(true);
    try {
      const res = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/aq/trends?lat=${lat}&lon=${lon}&days=7`
      );
      if (!res.ok) throw new Error("Backend error");

      const d = await res.json();
      if (!d.trend || d.trend.length === 0) throw new Error("Empty data");

      setTrends(
        d.trend.map((item: any) => ({
          ts: item.ts ?? `Day ${Math.random().toFixed(2)}`,
          pm25: isNaN(item.pm25) ? 0 : item.pm25,
          no2: isNaN(item.no2) ? 0 : item.no2,
        }))
      );
      setCorr(d.correlation ?? null);
      if (name) setCity(name);
    } catch (err) {
      console.warn("⚠️ Backend offline or failed, generating simulated data...");
      simulateData(name || city);
    } finally {
      setLoading(false);
    }
  };

  // 🔹 Simular datos si no hay backend o respuesta válida
  const simulateData = (name: string) => {
    const fake = Array.from({ length: 7 }).map((_, i) => ({
      ts: `Day ${i + 1}`,
      pm25: 15 + Math.random() * 40,
      no2: 10 + Math.random() * 25,
    }));

    setTrends(fake);
    setCity(name);

    // Calcular correlación
    const pm = fake.map((x) => x.pm25);
    const no = fake.map((x) => x.no2);
    const meanPm = pm.reduce((a, b) => a + b, 0) / pm.length;
    const meanNo = no.reduce((a, b) => a + b, 0) / no.length;
    const num = pm.reduce((acc, _, i) => acc + (pm[i] - meanPm) * (no[i] - meanNo), 0);
    const den =
      Math.sqrt(
        pm.reduce((acc, x) => acc + (x - meanPm) ** 2, 0) *
          no.reduce((acc, x) => acc + (x - meanNo) ** 2, 0)
      ) || 1;
    setCorr(num / den);
  };

  // 🔹 Cargar tendencias al inicio y cuando cambian coords
  useEffect(() => {
    fetchTrends(coords.lat, coords.lon, city);
  }, [coords]);

  // 🔹 Buscar nueva ciudad manualmente
  const handleSubmit = (e: any) => {
    e.preventDefault();
    if (city.trim() !== "") fetchCityCoords(city.trim());
  };

  return (
    <main className="flex flex-col min-h-screen bg-gradient-to-b from-black via-[#0c0c0c] to-[#101010] text-white">
      <div className="flex-1 pt-40 pb-10 px-6">
        <div className="max-w-6xl mx-auto">
          {/* ================= HEADER ================= */}
          <motion.div
            className="flex flex-col md:flex-row justify-between items-start md:items-center mb-10 gap-6"
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
          >
            <div>
              <h1 className="text-4xl font-extrabold tracking-tight flex items-center gap-3">
                <FiActivity className="text-[#5ac258]" />
                Air Quality <span className="text-[#5ac258]">Trends</span>
              </h1>
              <p className="text-gray-400 mt-2 max-w-lg">
                Track pollutant variations (PM2.5 & NO₂) in{" "}
                <span className="text-[#5ac258]">{city}</span> with NASA TEMPO
                and OpenAQ. Data is auto-simulated if unavailable.
              </p>
            </div>

            {/* 🔍 Search */}
            <form
              onSubmit={handleSubmit}
              className="flex items-center bg-black/60 border border-[#5ac258]/40 rounded-xl px-4 py-2 w-full md:w-72"
            >
              <FiSearch className="text-[#5ac258] mr-2" />
              <input
                type="text"
                placeholder="Enter a city or country"
                value={city}
                onChange={(e) => setCity(e.target.value)}
                className="bg-transparent text-white w-full outline-none placeholder-gray-400"
              />
              <button
                type="submit"
                className="ml-2 bg-[#5ac258] text-black px-3 py-1 rounded-lg font-semibold hover:bg-[#72dc70] transition-all"
              >
                Go
              </button>
            </form>
          </motion.div>

          {/* ================= HISTORICAL VARIATION ================= */}
          <motion.section
            className="bg-[#0f0f0f]/80 p-6 rounded-2xl shadow-lg mb-10 border border-[#5ac258]/30 backdrop-blur-sm"
            initial={{ opacity: 0, y: 40 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2, duration: 0.7 }}
          >
            <h2 className="text-2xl font-semibold mb-4 text-[#5ac258] flex items-center gap-2">
              <FiTrendingUp /> 7-Day Historical Variation
            </h2>

            {loading ? (
              <p className="text-gray-400">Loading data...</p>
            ) : trends.length > 0 ? (
              <ResponsiveContainer width="100%" height={320}>
                <LineChart data={trends}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#333" />
                  <XAxis dataKey="ts" tick={{ fill: "#aaa", fontSize: 10 }} />
                  <YAxis tick={{ fill: "#aaa", fontSize: 10 }} />
                  <Tooltip
                    formatter={(v) => (isNaN(Number(v)) ? "0" : v)}
                    contentStyle={{
                      backgroundColor: "#111",
                      border: "1px solid #5ac258",
                      borderRadius: "10px",
                    }}
                  />
                  <Line
                    type="monotone"
                    dataKey="pm25"
                    stroke="#ff4d4d"
                    strokeWidth={2}
                    dot={false}
                    name="PM2.5 (µg/m³)"
                  />
                  <Line
                    type="monotone"
                    dataKey="no2"
                    stroke="#5ac258"
                    strokeWidth={2}
                    dot={false}
                    name="NO₂ (µg/m³)"
                  />
                </LineChart>
              </ResponsiveContainer>
            ) : (
              <p className="text-gray-400">No data available for this location.</p>
            )}
          </motion.section>

          {/* ================= CORRELATION ================= */}
          <motion.section
            className="bg-[#0f0f0f]/80 p-6 rounded-2xl shadow-lg mb-10 border border-[#5ac258]/30 backdrop-blur-sm"
            initial={{ opacity: 0, y: 40 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3, duration: 0.7 }}
          >
            <h2 className="text-2xl font-semibold mb-4 text-[#5ac258] flex items-center gap-2">
              <FiActivity /> Correlation NO₂ ↔ PM2.5
            </h2>

            {loading ? (
              <p className="text-gray-400">Loading correlation...</p>
            ) : trends.length > 0 ? (
              <>
                <ResponsiveContainer width="100%" height={320}>
                  <ScatterChart>
                    <CartesianGrid strokeDasharray="3 3" stroke="#333" />
                    <XAxis dataKey="no2" name="NO₂ (µg/m³)" tick={{ fill: "#aaa" }} />
                    <YAxis dataKey="pm25" name="PM2.5 (µg/m³)" tick={{ fill: "#aaa" }} />
                    <Tooltip
                      cursor={{ strokeDasharray: "3 3" }}
                      contentStyle={{
                        backgroundColor: "#111",
                        border: "1px solid #5ac258",
                        borderRadius: "10px",
                      }}
                    />
                    <Scatter data={trends} fill="#5ac258" />
                  </ScatterChart>
                </ResponsiveContainer>
                <div className="mt-4 flex flex-col sm:flex-row justify-between items-start sm:items-center">
                  <p className="text-gray-300 text-lg">
                    Correlation coefficient:{" "}
                    <span className="font-bold text-[#5ac258]">
                      {corr !== null ? corr.toFixed(2) : "N/A"}
                    </span>
                  </p>
                  <p className="text-sm text-gray-400 mt-2 sm:mt-0">
                    A higher coefficient indicates stronger pollution linkage.
                  </p>
                </div>
              </>
            ) : (
              <p className="text-gray-400">No correlation data available.</p>
            )}
          </motion.section>

          {/* ================= INSIGHTS ================= */}
          <motion.section
            className="grid md:grid-cols-3 gap-6 mb-10"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.5 }}
          >
            <InsightCard
              icon={<FiHeart />}
              title="Health Impact"
              text="Fine particles (PM2.5) can penetrate deep into the lungs, aggravating asthma and heart disease."
            />
            <InsightCard
              icon={<FiWind />}
              title="Context"
              text="Low wind speeds or thermal inversions trap pollutants, increasing concentrations."
            />
            <InsightCard
              icon={<FiAlertTriangle />}
              title="Advisory"
              text="Limit outdoor activity if AQI exceeds 100. Prefer early mornings or evenings."
            />
          </motion.section>

          {/* ================= SOURCES ================= */}
          <motion.section
            className="text-center text-gray-400 text-sm mt-10"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.7 }}
          >
            <p>
              Data sourced from{" "}
              <span className="text-[#5ac258]">NASA TEMPO</span>,{" "}
              <span className="text-[#5ac258]">OpenAQ</span> &{" "}
              <span className="text-[#5ac258]">OpenWeather</span>.
            </p>
            <p className="mt-1 italic">
              “Empowering decisions through open environmental data.”
            </p>
          </motion.section>
        </div>
      </div>

      <Footer />
    </main>
  );
}

// 💡 Tarjeta de insight reutilizable
function InsightCard({
  icon,
  title,
  text,
}: {
  icon: any;
  title: string;
  text: string;
}) {
  return (
    <div className="bg-[#0f0f0f]/80 p-5 rounded-xl border border-[#5ac258]/30 shadow-lg flex flex-col gap-2">
      <div className="flex items-center gap-2 text-[#5ac258] font-semibold text-lg">
        {icon} {title}
      </div>
      <p className="text-gray-300 text-sm">{text}</p>
    </div>
  );
}
