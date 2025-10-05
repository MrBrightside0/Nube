"use client";

import * as React from "react";
import { Gauge } from "@mui/x-charts/Gauge"; // ✅ Import correcto para v8+
import { Box, Typography } from "@mui/material";

export default function AQIGauge({ value }: { value: number }) {
  const aqi = Math.min(Math.max(value ?? 0, 0), 500);

  const getAQIColor = (val: number) => {
    if (val <= 50) return "#5ac258"; // Verde
    if (val <= 100) return "#facc15"; // Amarillo
    if (val <= 150) return "#fb923c"; // Naranja
    if (val <= 200) return "#ef4444"; // Rojo
    if (val <= 300) return "#a855f7"; // Morado
    return "#6b7280"; // Gris oscuro
  };

  return (
    <Box
      sx={{
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        color: "white",
        width: "100%",
      }}
    >
      <Gauge
        width={200}
        height={100}
        value={aqi}
        startAngle={-90}
        endAngle={90}
        sx={{
          "& .MuiGauge-valueArc": {
            fill: getAQIColor(aqi),
          },
          "& .MuiGauge-referenceArc": {
            fill: "#1f2937",
          },
        }}
      />
      <Typography
        variant="h6"
        sx={{ mt: -4, fontWeight: "bold", color: "white" }}
      >
        AQI {aqi}
      </Typography>
    </Box>
  );
}
