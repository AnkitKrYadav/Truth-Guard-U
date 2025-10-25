import React from "react";

const NewsCard = ({ title, source, summary, category, url, expert, frameless = false }) => {
  const categoryColors = {
    Politics: "bg-red-200 text-red-800",
    Health: "bg-green-200 text-green-800",
    Tech: "bg-yellow-200 text-yellow-800",
    Entertainment: "bg-purple-200 text-purple-800",
    World: "bg-blue-200 text-blue-800",
    Local: "bg-pink-200 text-pink-800",
    Crime: "bg-gray-300 text-gray-800",
    Environment: "bg-green-100 text-green-700",
    Education: "bg-indigo-200 text-indigo-800",
    Lifestyle: "bg-orange-200 text-orange-800",
    Travel: "bg-teal-200 text-teal-800",
    Food: "bg-yellow-100 text-yellow-700",
    Opinion: "bg-gray-100 text-gray-700",
    Business: "bg-cyan-200 text-cyan-800",
    Sports: "bg-lime-200 text-lime-800",
    Science: "bg-blue-100 text-blue-700",
    General: "bg-gray-200 text-gray-800",
    All: "bg-gray-200 text-gray-800",
  };

  // Badge color and icon logic
  const badgeColors = {
    blue: "bg-blue-500 text-white",
    gold: "bg-yellow-500 text-white",
    custom: "bg-purple-500 text-white",
  };
  const badgeIcons = {
    blue: "\u2714", // checkmark
    gold: "\u2605", // star
    custom: "\u272A", // sparkle
  };

  const containerClass = frameless
    ? ""
    : "border rounded-lg p-4 shadow hover:shadow-xl transition-all duration-300 ease-out transform bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 h-full flex flex-col";

  return (
    <div className={`${containerClass} ${frameless ? "" : "hover:-translate-y-1"}`.trim()}>
      {category && (
        <span
          className={`inline-block px-2 py-1 text-xs font-semibold rounded-full mb-2 ${
            categoryColors[category] || "bg-gray-200 text-gray-800"
          }`}
        >
          {category}
        </span>
      )}

      {url ? (
        <a href={url} target="_blank" rel="noopener noreferrer" className="font-bold text-lg mb-2 hover:underline block">
          {title}
        </a>
      ) : (
        <h3 className="font-bold text-lg mb-2">{title}</h3>
      )}
      {source && <p className="text-sm text-gray-500 mb-2">Source: {source}</p>}
      {summary && <p className="text-gray-700 dark:text-gray-300 flex-grow line-clamp-3">{summary}</p>}

      {/* Expert Verification Info */}
      {expert && expert.is_verified && (
        <div className="mt-3 flex items-center gap-2">
          <span className={`flex items-center gap-1 px-2 py-1 rounded-full text-xs font-semibold ${badgeColors[expert.badge_color] || badgeColors.blue}`}>
            <span>{badgeIcons[expert.badge_color] || badgeIcons.blue}</span>
            <span>{expert.full_name}</span>
            <span className="ml-1">Verified Expert</span>
          </span>
        </div>
      )}
    </div>
  );
};

export default NewsCard;
