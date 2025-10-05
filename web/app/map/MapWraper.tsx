"use client";
import { useEffect, useRef, useState } from "react";
import { MapContainer, TileLayer, Marker, Popup, Circle } from "react-leaflet";
import { FiAlertTriangle } from "react-icons/fi";

export default function MapWrapper({ city, data, getAQIColor, getAQISummary }: any) {
  const mapRef = useRef<any>(null);
  const [mapReady, setMapReady] = useState(false);

  useEffect(() => {
    if (mapReady && mapRef.current) {
      mapRef.current.setView([city.lat, city.lon], 11);
    }
  }, [city, mapReady]);

  return (
    <div className="relative w-full h-[85vh] md:h-[90vh] overflow-hidden">
      {/* 🌫️ Efecto smog */}
      {data && (
        <div
          className="absolute inset-0 z-20 pointer-events-none transition-all duration-1000"
          style={{
            background:
              data.aqi > 150
                ? "radial-gradient(circle at 50% 60%, rgba(255,0,0,0.12), transparent 70%)"
                : data.aqi > 100
                ? "radial-gradient(circle at 50% 60%, rgba(255,165,0,0.08), transparent 70%)"
                : "none",
          }}
        />
      )}

      {/* 🌍 Mapa */}
      <div
        className={`w-full h-full z-10 transition-opacity duration-700 ${
          mapReady ? "opacity-100" : "opacity-0"
        }`}
      >
        <MapContainer
          ref={mapRef}
          center={[city.lat, city.lon]}
          zoom={11}
          scrollWheelZoom={true}
          whenReady={() => setMapReady(true)}
          className="w-full h-full z-10"
        >
          <TileLayer
            url="https://tiles.stadiamaps.com/tiles/alidade_smooth_dark/{z}/{x}/{y}{r}.png"
            attribution='&copy; <a href="https://stadiamaps.com/">Stadia Maps</a>'
          />

          {mapReady && data && (
            <>
              {data.aqi > 80 && (
                <Circle
                  center={[city.lat, city.lon]}
                  radius={2000 + data.aqi * 10}
                  pathOptions={{
                    color: getAQIColor(data.aqi),
                    fillColor: getAQIColor(data.aqi),
                    fillOpacity: 0.35,
                  }}
                />
              )}

              <Marker position={[city.lat, city.lon]}>
                <Popup>
                  <strong>{city.name}</strong> <br />
                  AQI: {data.aqi ?? "N/A"} <br />
                  PM2.5: {data.pm25 ?? "N/A"} µg/m³ <br />
                  NO₂: {data.no2 ?? "N/A"} µg/m³ <br />
                  Wind: {data.wind ?? "N/A"} km/h <br />
                  {data.aqi > 150 && (
                    <p className="text-red-500 font-semibold mt-2 flex items-center gap-1">
                      <FiAlertTriangle /> Unhealthy air!
                    </p>
                  )}
                </Popup>
              </Marker>
            </>
          )}
        </MapContainer>
      </div>

      {/* 📊 Tarjeta flotante */}
      {data && (
        <div
          className="
            absolute 
            bottom-4 right-4 
            sm:bottom-6 sm:right-6 
            bg-[#111122]/90 
            backdrop-blur-lg 
            border border-[#5ac258]/30 
            p-4 sm:p-5 
            rounded-xl 
            shadow-lg 
            text-xs sm:text-sm 
            w-64 sm:w-72 
            z-30 
            transition-all 
            duration-500 
            hover:scale-[1.02]
          "
        >
          <h4 className="font-bold text-[#5ac258] mb-2 text-base sm:text-lg">Zone Summary</h4>
          <p
            className="font-bold text-lg sm:text-xl"
            style={{ color: getAQIColor(data.aqi) }}
          >
            AQI: {data.aqi ?? "N/A"}
          </p>
          <p className="text-gray-300 mt-1 leading-relaxed">
            {getAQISummary(data.aqi)}
          </p>
        </div>
      )}
    </div>
  );
}
