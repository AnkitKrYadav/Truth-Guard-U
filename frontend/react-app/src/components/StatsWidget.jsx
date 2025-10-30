import React from "react";

const StatsWidget = ({ title, value, icon, bgColor, darkBg, className = "", style }) => {
  const displayIcon = icon || "📊"; // Fallback to bar chart emoji
  return (
    <div
      className={`flex items-center p-5 rounded-2xl shadow-xl backdrop-blur-md bg-white/50 dark:bg-gray-800/30 border border-gray-200/60 dark:border-gray-700/60 transition-all duration-300 hover:-translate-y-2 hover:shadow-2xl hover:bg-white/60 dark:hover:bg-gray-800/40 ${className}`.trim()}
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
