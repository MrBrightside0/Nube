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
} from "recharts";
import { motion } from "framer-motion";
import { WiDust, WiStrongWind, WiSmoke, WiDaySunny } from "react-icons/wi";

// 🌎 Subzonas dentro del área metropolitana de Monterrey
const mtyZones = [
  { name: "Universidad", lat: 25.7251, lon: -100.311 },
  { name: "San Nicolás", lat: 25.747, lon: -100.302 },
  { name: "San Pedro", lat: 25.657, lon: -100.401 },
  { name: "Santa Catarina", lat: 25.674, lon: -100.458 },
  { name: "Apodaca", lat: 25.777, lon: -100.188 },
  { name: "Escobedo", lat: 25.823, lon: -100.327 },
  { name: "Cadereyta", lat: 25.589, lon: -100.002 },
  { name: "Garcia", lat: 25.818, lon: -100.597 },
  { name: "Juárez", lat: 25.646, lon: -100.084 },
  { name: "Obispado", lat: 25.670, lon: -100.348 },
  { name: "Pesquería", lat: 25.782, lon: -100.054 },
  { name: "San Bernabé", lat: 25.735, lon: -100.350 },
  { name: "Misión San Juan", lat: 25.639, lon: -100.176 },
  { name: "Preparatoria ITESM", lat: 25.651, lon: -100.290 },
  { name: "TECNL", lat: 25.725, lon: -100.310 },
];

// ☁️ Contaminantes
const pollutants = [
  { key: "pm10", label: "PM10 (µg/m³)" },
  { key: "pm25", label: "PM2.5 (µg/m³)" },
  { key: "no2", label: "NO₂ (µg/m³)" },
];

export default function DashboardPage() {
  const [data, setData] = useState<any>(null);
  const [forecast, setForecast] = useState<any[]>([]);
  const [seasonal, setSeasonal] = useState<any[]>([]);
  const [zone, setZone] = useState(mtyZones[0]);
  const [pollutant, setPollutant] = useState(pollutants[0].key);

  // 🌍 Datos actuales
  useEffect(() => {
    fetch(
      `${process.env.NEXT_PUBLIC_API_URL}/aq/latest?lat=${zone.lat}&lon=${zone.lon}&pollutant=${pollutant}`
    )
      .then((res) => res.json())
      .then((d) => setData(d))
      .catch((err) => console.error("Error al obtener datos:", err));
  }, [zone, pollutant]);

  // 🔮 Predicción IA (Prophet local)
  useEffect(() => {
    fetch(
      `${process.env.NEXT_PUBLIC_API_URL}/ai/predict?lat=${zone.lat}&lon=${zone.lon}&pollutant=${pollutant}&days=30`
    )
      .then((res) => res.json())
      .then((d) => setForecast(d.predictions || []))
      .catch((err) => console.error("Error al obtener predicción:", err));
  }, [zone, pollutant]);

  // 📊 Tendencia y Estacionalidad
  useEffect(() => {
    fetch(
      `${process.env.NEXT_PUBLIC_API_URL}/ai/seasonal?lat=${zone.lat}&lon=${zone.lon}&pollutant=${pollutant}`
    )
      .then((res) => res.json())
      .then((d) => {
        if (d?.trend) {
          const formatted = d.trend.map((t: any) => ({
            ts: t.ts || new Date().toISOString(),
            value: t.value,
          }));
          setSeasonal(formatted);
        } else {
          setSeasonal([]);
        }
      })
      .catch((err) => console.error("Error al obtener análisis estacional:", err));
  }, [zone, pollutant]);

  // 🎨 Colores AQI
  const getAQIColor = (aqi: number | undefined) => {
    if (!aqi) return "bg-gray-700";
    if (aqi <= 50) return "bg-green-600";
    if (aqi <= 100) return "bg-yellow-500";
    if (aqi <= 150) return "bg-orange-500";
    if (aqi <= 200) return "bg-red-600";
    return "bg-purple-700";
  };
  const aqiColor = getAQIColor(data?.aqi);

  return (
    <main className="pt-24 px-6 text-white">
      {/* 🔹 Encabezado */}
      <div className="flex flex-col md:flex-row md:items-center justify-between mb-6 gap-4">
        <h1 className="text-3xl font-bold">
          Dashboard – <span className="text-[#5ac258]">{zone.name}</span>
        </h1>

        {/* Selectores */}
        <div className="flex flex-col sm:flex-row gap-4">
          <select
            value={zone.name}
            onChange={(e) => {
              const selected = mtyZones.find((c) => c.name === e.target.value);
              if (selected) setZone(selected);
            }}
            className="bg-black/70 border border-[#5ac258] text-white rounded-xl px-4 py-2 focus:ring-2 focus:ring-[#5ac258] outline-none w-full md:w-56"
          >
            {mtyZones.map((z) => (
              <option key={z.name} value={z.name}>
                {z.name}
              </option>
            ))}
          </select>

          <select
            value={pollutant}
            onChange={(e) => setPollutant(e.target.value)}
            className="bg-black/70 border border-[#5ac258] text-white rounded-xl px-4 py-2 focus:ring-2 focus:ring-[#5ac258] outline-none w-full md:w-48"
          >
            {pollutants.map((p) => (
              <option key={p.key} value={p.key}>
                {p.label}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* 🌫 Tarjetas principales */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 mb-10">
        <InfoCard
          title="AQI Actual"
          value={data?.aqi ?? "–"}
          Icon={WiDaySunny}
          customColor={aqiColor}
        />
        <InfoCard title="PM2.5 (µg/m³)" value={data?.pm25 ?? "–"} Icon={WiDust} />
        <InfoCard title="NO₂ (µg/m³)" value={data?.no2 ?? "–"} Icon={WiSmoke} />
        <InfoCard title="Viento (km/h)" value={data?.wind ?? "–"} Icon={WiStrongWind} />
      </div>

      {/* 🔮 Predicción IA */}
      <section className="bg-black/70 p-6 rounded-2xl shadow-lg mb-10">
        <h2 className="text-2xl font-bold mb-4 text-[#5ac258]">Predicción IA (30 días)</h2>
        {forecast.length > 0 ? (
          <ResponsiveContainer width="100%" height={300}>
            <LineChart
              data={forecast.map((f) => ({
                ts: f.ds || f.ts,
                yhat: f.yhat,
              }))}
            >
              <CartesianGrid strokeDasharray="3 3" stroke="#444" />
              <XAxis dataKey="ts" tick={{ fill: "#aaa", fontSize: 10 }} />
              <YAxis tick={{ fill: "#aaa", fontSize: 10 }} />
              <Tooltip />
              <Line type="monotone" dataKey="yhat" stroke="#5ac258" dot={false} />
            </LineChart>
          </ResponsiveContainer>
        ) : (
          <p>Cargando predicción IA...</p>
        )}
      </section>

      {/* 📊 Tendencia y Estacionalidad */}
      <section className="bg-black/70 p-6 rounded-2xl shadow-lg">
        <h2 className="text-2xl font-bold mb-4 text-[#5ac258]">
          Tendencia y Estacionalidad
        </h2>
        {seasonal.length > 0 ? (
          <ResponsiveContainer width="100%" height={250}>
            <LineChart data={seasonal}>
              <CartesianGrid strokeDasharray="3 3" stroke="#444" />
              <XAxis dataKey="ts" tick={{ fill: "#aaa", fontSize: 10 }} />
              <YAxis tick={{ fill: "#aaa", fontSize: 10 }} />
              <Tooltip />
              <Line type="monotone" dataKey="value" stroke="#5ac258" dot={false} />
            </LineChart>
          </ResponsiveContainer>
        ) : (
          <p>No hay tendencia disponible.</p>
        )}
      </section>
    </main>
  );
}

// 💡 Tarjeta individual
function InfoCard({
  title,
  value,
  Icon,
  customColor,
}: {
  title: string;
  value: any;
  Icon: any;
  customColor?: string;
}) {
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.5 }}
      className={`${customColor ?? "bg-black/70"} p-6 rounded-2xl shadow-lg hover:scale-105 transition-transform`}
    >
      <div className="flex items-center justify-between">
        <h2 className="text-gray-400 text-sm font-semibold">{title}</h2>
        <Icon size={38} className="text-[#5ac258]" />
      </div>
      <p className="text-5xl font-bold mt-3 text-white">{value}</p>
    </motion.div>
  );
}
