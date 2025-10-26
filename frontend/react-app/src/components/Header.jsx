import React from "react";
import { ShieldCheck } from "lucide-react";

function Header() {
  return (
    <header className="bg-white/70 dark:bg-gray-900/70 backdrop-blur-md shadow-sm sticky top-0 z-50">
      <div className="max-w-5xl mx-auto flex items-center justify-between px-6 py-4">
        <div className="flex items-center gap-2">
          <ShieldCheck className="w-7 h-7 text-blue-600" />
          <h1 className="text-2xl font-bold text-gray-800 dark:text-gray-100">TruthGuard</h1>
        </div>
        <nav className="hidden md:flex gap-6 text-gray-600 dark:text-gray-300 font-medium">
          <a href="#" className="hover:text-blue-600">Home</a>
          <a href="#" className="hover:text-blue-600">About</a>
          <a href="#" className="hover:text-blue-600">Contact</a>
        </nav>
      </div>
    </header>
  );
}

export default Header;
