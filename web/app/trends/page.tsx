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
  ZAxis,
} from "recharts";

// Ciudades disponibles
const cities = [
  { name: "Monterrey", lat: 25.67, lon: -100.31 },
  { name: "CDMX", lat: 19.43, lon: -99.13 },
  { name: "Houston", lat: 29.76, lon: -95.37 },
];

export default function TrendsPage() {
  const [city, setCity] = useState(cities[0]);
  const [trends, setTrends] = useState<any[]>([]);
  const [corr, setCorr] = useState<number | null>(null);

  useEffect(() => {
    fetch(`${process.env.NEXT_PUBLIC_API_URL}/aq/trends?lat=${city.lat}&lon=${city.lon}&days=7`)
      .then((res) => res.json())
      .then((d) => {
        setTrends(d.series || []);
        setCorr(d.correlation ?? null);
      })
      .catch((err) => console.error("Error al obtener tendencias:", err));
  }, [city]);

  return (
    <main className="pt-24 px-6 text-white">
      <div className="flex flex-col md:flex-row md:items-center justify-between mb-6 gap-4">
        <h1 className="text-3xl font-bold">
          Tendencias – <span className="text-[#5ac258]">{city.name}</span>
        </h1>

        {/* Selector de ciudad */}
        <select
          value={city.name}
          onChange={(e) => {
            const selected = cities.find((c) => c.name === e.target.value);
            if (selected) setCity(selected);
          }}
          className="bg-black/70 border border-[#5ac258] text-white rounded-xl px-4 py-2 focus:ring-2 focus:ring-[#5ac258] outline-none w-full md:w-60"
        >
          {cities.map((c) => (
            <option key={c.name} value={c.name}>
              {c.name}
            </option>
          ))}
        </select>
      </div>

      {/* Histórico 7 días */}
      <section className="bg-black/70 p-6 rounded-2xl shadow-lg mb-10">
        <h2 className="text-2xl font-bold mb-4 text-[#5ac258]">
          Histórico de 7 días
        </h2>

        {trends.length > 0 ? (
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={trends}>
              <CartesianGrid strokeDasharray="3 3" stroke="#444" />
              <XAxis dataKey="ts" tick={{ fill: "#aaa", fontSize: 10 }} />
              <YAxis tick={{ fill: "#aaa", fontSize: 10 }} />
              <Tooltip />
              <Line type="monotone" dataKey="pm25" stroke="#ff4d4d" dot={false} name="PM2.5" />
              <Line type="monotone" dataKey="no2" stroke="#5ac258" dot={false} name="NO₂" />
            </LineChart>
          </ResponsiveContainer>
        ) : (
          <p>Cargando tendencias...</p>
        )}
      </section>

      {/* Correlación NO₂ ↔ PM2.5 */}
      <section className="bg-black/70 p-6 rounded-2xl shadow-lg">
        <h2 className="text-2xl font-bold mb-4 text-[#5ac258]">
          Correlación NO₂ ↔ PM2.5
        </h2>

        {trends.length > 0 ? (
          <>
            <ResponsiveContainer width="100%" height={300}>
              <ScatterChart>
                <CartesianGrid strokeDasharray="3 3" stroke="#444" />
                <XAxis dataKey="no2" name="NO₂" tick={{ fill: "#aaa" }} />
                <YAxis dataKey="pm25" name="PM2.5" tick={{ fill: "#aaa" }} />
                <Tooltip cursor={{ strokeDasharray: "3 3" }} />
                <ZAxis range={[60, 400]} />
                <Scatter data={trends} fill="#5ac258" />
              </ScatterChart>
            </ResponsiveContainer>
            <p className="text-gray-300 text-lg mt-3">
              Coeficiente de correlación:{" "}
              <span className="font-bold text-[#5ac258]">
                {corr !== null ? corr.toFixed(2) : "N/A"}
              </span>
            </p>
          </>
        ) : (
          <p>Cargando correlación...</p>
        )}
      </section>
    </main>
  );
}
