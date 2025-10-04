"use client";
import { useEffect, useState } from "react";
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from "recharts";

export default function Insights() {
  const [trend, setTrend] = useState([]);
  const [forecast, setForecast] = useState([]);
  const [monthly, setMonthly] = useState({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchData() {
      try {
        const sRes = await fetch("http://127.0.0.1:5000/api/ai/seasonal?location=Universidad&pollutant=pm10");
        const sData = await sRes.json();

        const fRes = await fetch("http://127.0.0.1:5000/api/aq/forecast?h=24");
        const fData = await fRes.json();

        setTrend(sData.trend || []);
        setMonthly(sData.monthly_avg || {});
        setForecast(fData.predictions || []);
      } catch (err) {
        console.error("Error fetching insights:", err);
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, []);

  if (loading) return <div className="text-center text-gray-400 py-10">Loading insights...</div>;

  return (
    <section className="p-6 bg-[#0d0d0d]/60 rounded-2xl shadow-xl mt-8">
      <h2 className="text-2xl font-semibold mb-4 text-[#5ac258]">📊 Air Quality Insights</h2>

      {/* Trend Chart */}
      <div className="mb-10">
        <h3 className="text-lg mb-2 text-gray-300">Long-Term Trend (PM10)</h3>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={trend.slice(-100)}>
            <CartesianGrid strokeDasharray="3 3" stroke="#333" />
            <XAxis dataKey="ts" hide />
            <YAxis stroke="#aaa" />
            <Tooltip contentStyle={{ backgroundColor: "#111", border: "none" }} />
            <Line type="monotone" dataKey="value" stroke="#5ac258" dot={false} />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Forecast Chart */}
      <div className="mb-10">
        <h3 className="text-lg mb-2 text-gray-300">Next 24h Forecast (PM10)</h3>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={forecast}>
            <CartesianGrid strokeDasharray="3 3" stroke="#333" />
            <XAxis dataKey="ds" hide />
            <YAxis stroke="#aaa" />
            <Tooltip contentStyle={{ backgroundColor: "#111", border: "none" }} />
            <Line type="monotone" dataKey="yhat" stroke="#5ac258" dot={false} />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {Object.entries(monthly).map(([month, value]) => (
          <div key={month} className="p-3 bg-[#1a1a1a] rounded-lg text-center border border-[#5ac258]/20">
            <p className="text-gray-400 text-sm">Month {month}</p>
            <h4 className="text-xl text-[#5ac258] font-semibold">{value.toFixed(1)}</h4>
          </div>
        ))}
      </div>
    </section>
  );
}
