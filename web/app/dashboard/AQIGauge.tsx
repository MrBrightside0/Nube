"use client";

import * as React from "react";
import { Gauge } from "@mui/x-charts/Gauge";
import { motion } from "framer-motion";

export default function AQIGauge({ value }: { value: number }) {
  const aqi = Math.min(Math.max(value ?? 0, 0), 350);

  const getAQIColor = (val: number) => {
    if (val <= 50) return "#5ac258";
    if (val <= 100) return "#facc15";
    if (val <= 150) return "#fb923c";
    if (val <= 200) return "#ef4444";
    if (val <= 275) return "#a855f7";
    return "#78350f";
  };

  return (
    <div className="flex flex-col items-center justify-center mt-4 text-white">
      <div className="relative" style={{ width: 260, height: 150 }}>
        {/* 🔹 Semicírculo base */}
        <Gauge
          value={aqi}
          startAngle={-90}
          endAngle={90}
          valueMin={0}
          valueMax={350}
          width={260}
          height={150}
          sx={{
            "& .MuiGauge-valueArc": {
              fill: getAQIColor(aqi),
              transition: "fill 0.5s ease",
            },
            "& .MuiGauge-referenceArc": {
              fill: "#1c1c1c",
            },
          }}
        />

        {/* 🔹 Texto “AQI” */}
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 19 }}
          transition={{ duration: 0.5 }}
          className="absolute w-full text-center"
          style={{
            top: 35,
            fontSize: 16,
            fontWeight: 600,
            color: "#ffffff",
          }}
        >
          AQI
        </motion.div>

        {/* 🔹 Valor numérico */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.6 }}
          className="absolute w-full text-center"
          style={{
            bottom: 12,
            fontSize: 42,
            fontWeight: 800,
            color: "#ffffff",
          }}
        >
          {Math.round(aqi)}
        </motion.div>
      </div>
    </div>
  );
}
