"use client";

import {
  GaugeContainer,
  GaugeReferenceArc,
  GaugeValueArc,
  GaugeValueText,
} from "@mui/x-charts/Gauge";

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
    <div className="flex flex-col items-center justify-center mt-4">
      <GaugeContainer
        width={260}
        height={150} // 🔹 Subido un poco el gauge completo
        startAngle={-90}
        endAngle={90}
        valueMin={0}
        valueMax={350}
        value={aqi}
        sx={{ backgroundColor: "transparent" }}
      >
        <GaugeReferenceArc style={{ fill: "#1c1c1c" }} />
        <GaugeValueArc
          style={{
            fill: getAQIColor(aqi),
            transition: "fill 0.4s ease",
          }}
        />

        {/* 🔹 Texto “AQI” */}
        <GaugeValueText
          text="AQI"
          style={{
            fill: "#ffffff",
            fontSize: 16,
            fontWeight: 600,
            transform: "translate(0px, -30px)", // más arriba
            textAnchor: "middle",
          }}
        />

        {/* 🔹 Valor numérico */}
        <GaugeValueText
          text={`${Math.round(aqi)}`}
          style={{
            fill: "#ffffff",
            fontSize: 42,
            fontWeight: 800,
            transform: "translate(0px, 8px)", // subido respecto al centro
            textAnchor: "middle",
          }}
        />
      </GaugeContainer>
    </div>
  );
}
