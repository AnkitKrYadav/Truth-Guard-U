import React from "react";

const StatsWidget = ({ title, value, icon, bgColor, darkBg, className = "", style }) => {
  const displayIcon = icon || "📊"; // Fallback to bar chart emoji
  return (
    <div
      className={`flex items-center p-4 rounded-lg shadow-md transition-transform duration-300 hover:-translate-y-1 hover:shadow-lg ${bgColor} ${
        darkBg || "dark:bg-gray-800/40"
      } ${className}`.trim()}
      style={style}
    >
      <div className="text-3xl mr-4 text-gray-700 dark:text-gray-200" role="img" aria-label={`${title} icon`}>
        {displayIcon}
      </div>
      <div>
        <h3 className="text-gray-900 dark:text-gray-100 font-semibold">{title}</h3>
        <p className="text-xl font-bold text-gray-900 dark:text-gray-100">{value}</p>
      </div>
    </div>
  );
};

export default StatsWidget;
