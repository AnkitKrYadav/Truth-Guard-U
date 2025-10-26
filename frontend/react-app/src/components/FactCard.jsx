import React from "react";
import { BadgeCheck, AlertTriangle } from "lucide-react";

function FactCard({ title, source, confidence, verdict, description }) {
  const isTrue = verdict.toLowerCase().includes("true");

  return (
    <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-md p-6 border-l-4 hover:shadow-lg transition-all duration-200 text-gray-900 dark:text-gray-100"
      style={{ borderColor: isTrue ? "#16a34a" : "#dc2626" }}>
      <div className="flex items-center justify-between">
        <h3 className="text-xl font-semibold">{title}</h3>
        {isTrue ? (
          <BadgeCheck className="text-green-600 w-6 h-6" />
        ) : (
          <AlertTriangle className="text-red-600 w-6 h-6" />
        )}
      </div>
  <p className="mt-2 text-gray-600 dark:text-gray-300">{description}</p>
  <div className="mt-3 text-sm text-gray-500 dark:text-gray-300 flex justify-between">
        <span>Source: {source}</span>
        <span>Confidence: {confidence}</span>
        <span
          className={`font-semibold ${
            isTrue ? "text-green-600" : "text-red-600"
          }`}
        >
          {verdict}
        </span>
      </div>
    </div>
  );
}

export default FactCard;
