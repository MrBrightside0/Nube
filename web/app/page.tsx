"use client";
import { useEffect } from "react";

export default function Home() {
  useEffect(() => {
    fetch(process.env.NEXT_PUBLIC_API_URL + "/health")
      .then((res) => res.json())
      .then((data) => console.log("Backend /health response:", data))
      .catch((err) => console.error("Error fetching /health:", err));
  }, []);

  return (
    <div>
      <h1 className="text-2xl font-bold">Home Placeholder</h1>
      <p>Check console for /health response</p>
    </div>
  );
}
