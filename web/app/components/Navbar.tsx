import Link from "next/link";

export default function Navbar() {
  return (
    <nav className="flex gap-6 p-4 bg-gray-900 text-white">
      <Link href="/map">Map</Link>
      <Link href="/dashboard">Dashboard</Link>
      <Link href="/trends">Trends</Link>
      <Link href="/alerts">Alerts</Link>
    </nav>
  );
}
