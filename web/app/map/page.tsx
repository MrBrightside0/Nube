"use client";
import dynamic from "next/dynamic";
import { useEffect, useState } from "react";
import { FiMenu } from "react-icons/fi";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

// ⚡ Cargas dinámicas para evitar errores de SSR
const MapContainer = dynamic(() => import("react-leaflet").then((m) => m.MapContainer), { ssr: false });
const TileLayer = dynamic(() => import("react-leaflet").then((m) => m.TileLayer), { ssr: false });
const Marker = dynamic(() => import("react-leaflet").then((m) => m.Marker), { ssr: false });
const Popup = dynamic(() => import("react-leaflet").then((m) => m.Popup), { ssr: false });

interface City {
  name: string;
  lat: number;
  lon: number;
}

const cities: City[] = [
  { name: "Monterrey", lat: 25.67, lon: -100.31 },
  { name: "CDMX", lat: 19.43, lon: -99.13 },
  { name: "Houston", lat: 29.76, lon: -95.37 },
];

export default function MapPage() {
  const [data, setData] = useState<any>(null);
  const [trends, setTrends] = useState<any[]>([]);
  const [city, setCity] = useState<City>(cities[0]);
  const [sidebarOpen, setSidebarOpen] = useState(false);

  // Datos actuales
  useEffect(() => {
    fetch(`${process.env.NEXT_PUBLIC_API_URL}/aq/latest?lat=${city.lat}&lon=${city.lon}`)
      .then((res) => res.json())
      .then((d) => setData(d))
      .catch((err) => console.error("Error al obtener datos:", err));
  }, [city]);

  // Tendencias 7 días
  useEffect(() => {
    fetch(`${process.env.NEXT_PUBLIC_API_URL}/aq/trends?lat=${city.lat}&lon=${city.lon}&days=7`)
      .then((res) => res.json())
      .then((d) => setTrends(d.series || []))
      .catch((err) => console.error("Error al obtener tendencias:", err));
  }, [city]);

  return (
    <main className="relative flex flex-col md:flex-row pt-20 h-[calc(100vh-80px)] overflow-hidden">
      {/* Botón menú móvil */}
      <button
        className="md:hidden fixed top-24 right-4 z-50 bg-[#5ac258] text-black p-3 rounded-full shadow-lg"
        onClick={() => setSidebarOpen(!sidebarOpen)}
      >
        <FiMenu size={22} />
      </button>

      {/* Sidebar */}
      <aside
        className={`fixed md:static top-0 left-0 h-full md:h-auto w-[85%] md:w-80 bg-black/95 text-white 
        rounded-none md:rounded-2xl p-6 shadow-xl transition-transform duration-300 z-40
        ${sidebarOpen ? "translate-x-0" : "-translate-x-full md:translate-x-0"}`}
      >
        <h2 className="text-2xl font-bold mb-4">Air Quality</h2>

        {/* Selector de ciudad */}
        <select
          value={city.name}
          onChange={(e) => {
            const selected = cities.find((c) => c.name === e.target.value);
            if (selected) setCity(selected);
          }}
          className="w-full mb-6 p-2 rounded-lg bg-gray-800 text-white focus:outline-none focus:ring-2 focus:ring-[#5ac258]"
        >
          {cities.map((c) => (
            <option key={c.name} value={c.name}>
              {c.name}
            </option>
          ))}
        </select>

        {data ? (
          <ul className="space-y-2 text-lg mb-6">
            <li><strong>Ciudad:</strong> {city.name}</li>
            <li><strong>AQI:</strong> {data.aqi ?? "N/A"}</li>
            <li><strong>PM2.5:</strong> {data.pm25 ?? "N/A"} µg/m³</li>
            <li><strong>NO₂:</strong> {data.no2 ?? "N/A"} µg/m³</li>
            <li><strong>Viento:</strong> {data.wind ?? "N/A"} km/h</li>
          </ul>
        ) : (
          <p>Cargando datos...</p>
        )}

        {/* Mini gráfico tendencias */}
        <div className="bg-gray-800 p-3 rounded-xl">
          <h3 className="text-lg font-semibold mb-2">Últimos 7 días</h3>
          <ResponsiveContainer width="100%" height={150}>
            <LineChart data={trends}>
              <CartesianGrid strokeDasharray="3 3" stroke="#444" />
              <XAxis dataKey="ts" tick={{ fill: "#aaa", fontSize: 10 }} />
              <YAxis tick={{ fill: "#aaa", fontSize: 10 }} />
              <Tooltip />
              <Line type="monotone" dataKey="pm25" stroke="#ff4d4d" dot={false} name="PM2.5" />
              <Line type="monotone" dataKey="no2" stroke="#5ac258" dot={false} name="NO₂" />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* Botón cerrar en móvil */}
        <button
          className="md:hidden mt-6 w-full py-2 bg-[#5ac258] text-black font-semibold rounded-xl"
          onClick={() => setSidebarOpen(false)}
        >
          Cerrar panel
        </button>
      </aside>

      {/* 🌍 Mapa principal */}
      <div className="flex-1 w-full h-full rounded-none md:rounded-2xl overflow-hidden shadow-lg">
        <MapContainer
          key={`${city.lat}-${city.lon}`} // 👈 fuerza un nuevo mapa por ciudad
          center={[city.lat, city.lon]}
          zoom={11}
          scrollWheelZoom={true}
          className="w-full h-full z-10"
        >
          <TileLayer
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            attribution='&copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors'
          />

          {data && (
            <Marker position={[city.lat, city.lon]}>
              <Popup>
                <strong>{city.name}</strong> <br />
                AQI: {data.aqi ?? "N/A"} <br />
                PM2.5: {data.pm25 ?? "N/A"} µg/m³ <br />
                NO₂: {data.no2 ?? "N/A"} µg/m³ <br />
                Viento: {data.wind ?? "N/A"} km/h <br />
                Fuente: {data.sources?.join(", ") || "N/A"}
              </Popup>
            </Marker>
          )}
        </MapContainer>
      </div>
    </main>
  );
}
