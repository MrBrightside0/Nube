"use client";
import { useEffect, useState } from "react";
import dynamic from "next/dynamic";
import { motion, AnimatePresence } from "framer-motion";
import { FiAlertTriangle, FiSearch, FiNavigation } from "react-icons/fi";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

// ✅ Dynamic Leaflet imports
const MapContainer = dynamic(() => import("react-leaflet").then((m) => m.MapContainer), { ssr: false });
const TileLayer = dynamic(() => import("react-leaflet").then((m) => m.TileLayer), { ssr: false });
const CircleMarker = dynamic(() => import("react-leaflet").then((m) => m.CircleMarker), { ssr: false });
const Popup = dynamic(() => import("react-leaflet").then((m) => m.Popup), { ssr: false });

interface City {
  name: string;
  lat: number;
  lon: number;
  aqi: number;
  pm25: number;
  no2: number;
  wind: number;
  trend: any[];
}

export default function MapPage() {
  const [cities, setCities] = useState<City[]>([]);
  const [selected, setSelected] = useState<City | null>(null);
  const [query, setQuery] = useState("");
  const [center, setCenter] = useState<[number, number]>([25.67, -100.31]);
  const [myLocation, setMyLocation] = useState<[number, number] | null>(null);
  const [loading, setLoading] = useState(false);
  const [searching, setSearching] = useState(false);
  const [simulated, setSimulated] = useState(false);

  // 🎨 Funciones visuales
  const getAQIColor = (aqi: number) =>
    aqi <= 50 ? "#5ac258" :
    aqi <= 100 ? "#facc15" :
    aqi <= 150 ? "#fb923c" :
    aqi <= 200 ? "#ef4444" : "#991b1b";

  const getAQISummary = (aqi: number) =>
    aqi <= 50 ? "Excellent air quality — enjoy outdoor activities safely." :
    aqi <= 100 ? "Moderate — some pollutants may affect sensitive groups." :
    aqi <= 150 ? "Unhealthy for sensitive groups — limit prolonged outdoor exposure." :
    aqi <= 200 ? "Unhealthy — avoid outdoor activities." :
    "Hazardous — stay indoors and avoid exertion.";

  // 📍 Obtener ubicación del usuario
  const handleMyLocation = () => {
    if (!navigator.geolocation) return alert("Geolocation not supported.");
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        const { latitude, longitude } = pos.coords;
        setMyLocation([latitude, longitude]);
        setCenter([latitude, longitude]);
        fetchCityData(latitude, longitude, "My Location");
      },
      () => alert("Unable to retrieve location.")
    );
  };

  // 🔍 Buscador global
  const handleSearch = async (e: any) => {
    e.preventDefault();
    if (!query.trim()) return;
    setSearching(true);

    try {
      const res = await fetch(
        `https://api.openweathermap.org/geo/1.0/direct?q=${encodeURIComponent(query)}&limit=1&appid=${process.env.NEXT_PUBLIC_OWM_KEY}`
      );
      const json = await res.json();

      let lat, lon, name;
      if (json && json.length > 0) {
        ({ lat, lon, name } = json[0]);
        name = name || query;
      } else {
        name = query;
        lat = Math.random() * 160 - 80;
        lon = Math.random() * 360 - 180;
      }

      setCenter([lat, lon]);
      fetchCityData(lat, lon, name);
    } catch {
      const lat = Math.random() * 160 - 80;
      const lon = Math.random() * 360 - 180;
      fetchCityData(lat, lon, query);
    } finally {
      setSearching(false);
    }
  };

  // 🚀 Backend o datos simulados
  const fetchCityData = async (lat: number, lon: number, name: string) => {
    setLoading(true);
    setSimulated(false);
    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/aq/predict?lat=${lat}&lon=${lon}`);
      if (!res.ok) throw new Error("Backend error");
      const data = await res.json();

      const cityData: City = {
        name: name || "Current Zone",
        lat: data.lat || lat,
        lon: data.lon || lon,
        aqi: data.aqi ?? 0,
        pm25: data.pm25 ?? 0,
        no2: data.no2 ?? 0,
        wind: data.wind ?? 0,
        trend: data.trend?.length
          ? data.trend
          : Array.from({ length: 6 }).map((_, i) => ({
              ts: `Day ${i + 1}`,
              pm25: Math.floor(Math.random() * 50),
              no2: Math.floor(Math.random() * 30),
            })),
      };

      setCities((prev) => [...prev.filter((c) => c.name !== cityData.name), cityData]);
      setSelected(cityData);
    } catch {
      setSimulated(true);
      const fakeCity: City = {
        name: name || "Simulated Zone",
        lat,
        lon,
        aqi: Math.floor(Math.random() * 200),
        pm25: Math.floor(Math.random() * 60),
        no2: Math.floor(Math.random() * 40),
        wind: Math.floor(Math.random() * 15),
        trend: Array.from({ length: 6 }).map((_, i) => ({
          ts: `Day ${i + 1}`,
          pm25: Math.floor(Math.random() * 50),
          no2: Math.floor(Math.random() * 30),
        })),
      };
      setCities((prev) => [...prev.filter((c) => c.name !== fakeCity.name), fakeCity]);
      setSelected(fakeCity);
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="relative w-full h-[calc(100vh-80px)] bg-[#0A0A1A] text-white pt-20 overflow-hidden">

      {/* 🔍 Search Bar */}
      <form
        onSubmit={handleSearch}
        className="absolute top-24 left-1/2 -translate-x-1/2 z-40 flex items-center
        w-[90%] max-w-[400px] sm:max-w-[480px]
        bg-[#111122]/90 backdrop-blur-md border border-[#5ac258]/40 
        rounded-xl overflow-hidden shadow-lg"
      >
        <input
          type="text"
          placeholder="Search any city or place..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          className="px-4 py-3 flex-1 bg-transparent text-white outline-none placeholder-gray-400 text-sm sm:text-base"
        />
        <button type="submit" className="bg-[#5ac258] text-black px-4 py-3 hover:bg-[#72dc70] transition">
          <FiSearch size={18} />
        </button>
      </form>

      {/* 📍 My Location Button */}
      <button
        onClick={handleMyLocation}
        className="absolute top-40 sm:top-24 right-4 sm:right-6 z-40 bg-[#111122]/90 backdrop-blur-md border border-[#5ac258]/40 
        hover:bg-[#5ac258]/20 transition text-[#5ac258] p-3 rounded-full shadow-lg"
        title="Go to my location"
      >
        <FiNavigation size={20} />
      </button>

      {/* 🗺️ Map */}
      <MapContainer center={center} zoom={11} scrollWheelZoom className="w-full h-full z-10">
        <TileLayer
          url="https://tiles.stadiamaps.com/tiles/alidade_smooth_dark/{z}/{x}/{y}{r}.png"
          attribution='&copy; <a href="https://stadiamaps.com/">Stadia Maps</a>'
        />

        {cities.map((c) => (
          <CircleMarker
            key={c.name + c.lat}
            center={[c.lat, c.lon]}
            radius={14}
            pathOptions={{
              color: getAQIColor(c.aqi),
              fillColor: getAQIColor(c.aqi),
              fillOpacity: 0.9,
            }}
            eventHandlers={{ click: () => setSelected(c) }}
          >
            <Popup>
              <strong>{c.name}</strong><br />
              AQI: {c.aqi}<br />
              PM2.5: {c.pm25} µg/m³<br />
              NO₂: {c.no2} µg/m³<br />
              Wind: {c.wind} km/h
            </Popup>
          </CircleMarker>
        ))}

        {myLocation && (
          <CircleMarker
            center={myLocation}
            radius={10}
            pathOptions={{
              color: "#3b82f6",
              fillColor: "#3b82f6",
              fillOpacity: 0.7,
            }}
          >
            <Popup>You are here 📍</Popup>
          </CircleMarker>
        )}
      </MapContainer>

      {/* 📊 Info Panel (responsive modal) */}
      <AnimatePresence>
        {selected && (
          <motion.div
            key="panel"
            initial={{ opacity: 0, y: 100 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 100 }}
            transition={{ duration: 0.4 }}
            className="fixed sm:absolute sm:top-28 sm:right-6 bottom-0 left-0 sm:left-auto
            w-full sm:w-80 bg-[#111122]/95 backdrop-blur-lg border border-[#5ac258]/30 
            p-5 sm:p-6 rounded-t-2xl sm:rounded-2xl shadow-xl z-30 
            max-h-[70vh] sm:max-h-[65vh] overflow-y-auto"
          >
            <div className="flex justify-between items-center mb-2">
              <h3 className="text-lg sm:text-xl font-bold text-[#5ac258]">{selected.name}</h3>
              <button onClick={() => setSelected(null)} className="text-gray-400 hover:text-white transition">✕</button>
            </div>
            <p className="text-sm text-gray-300 mb-3 leading-snug">{getAQISummary(selected.aqi)}</p>
            <p className="text-lg font-semibold mb-4" style={{ color: getAQIColor(selected.aqi) }}>
              AQI: {selected.aqi}
            </p>
            <ResponsiveContainer width="100%" height={150}>
              <LineChart data={selected.trend}>
                <CartesianGrid strokeDasharray="3 3" stroke="#333" />
                <XAxis dataKey="ts" tick={{ fill: "#aaa", fontSize: 10 }} />
                <YAxis
                  tick={{ fill: "#aaa", fontSize: 10 }}
                  label={{ value: "µg/m³", angle: -90, position: "insideLeft", fill: "#aaa", fontSize: 10 }}
                />
                <Tooltip contentStyle={{ backgroundColor: "#111", border: "none", color: "#fff" }} />
                <Line type="monotone" dataKey="pm25" stroke="#ff4d4d" dot={false} />
                <Line type="monotone" dataKey="no2" stroke="#5ac258" dot={false} />
              </LineChart>
            </ResponsiveContainer>
            {selected.aqi > 150 && (
              <div className="mt-3 flex items-center gap-2 text-red-400 text-sm sm:text-base">
                <FiAlertTriangle /> <span>Unhealthy air detected</span>
              </div>
            )}
          </motion.div>
        )}
      </AnimatePresence>

      {/* 🌀 Feedback visual */}
      {loading && (
        <div className="absolute inset-0 bg-black/50 flex items-center justify-center text-[#5ac258] text-lg sm:text-xl font-bold z-50">
          Fetching air quality data...
        </div>
      )}
      {searching && (
        <div className="absolute top-36 left-1/2 -translate-x-1/2 bg-[#111122]/90 text-[#5ac258] px-6 py-2 rounded-lg shadow-lg text-xs sm:text-sm z-50">
          Searching location...
        </div>
      )}
      {simulated && !loading && (
        <div className="absolute bottom-4 left-4 bg-yellow-600/80 text-white text-xs px-3 py-1 rounded-md z-50 shadow-md">
          Simulated data mode (backend offline)
        </div>
      )}
    </main>
  );
}
