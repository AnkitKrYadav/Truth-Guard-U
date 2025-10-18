import React from "react";

const NewsCard = ({ title, source, summary, category, url }) => {
  const categoryColors = {
    Politics: "bg-red-200 text-red-800",
    Health: "bg-green-200 text-green-800",
    Tech: "bg-yellow-200 text-yellow-800",
    Entertainment: "bg-purple-200 text-purple-800",
    All: "bg-gray-200 text-gray-800",
  };

  return (
    <div className="border rounded-lg p-4 shadow hover:shadow-lg transition bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100">
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
        <a href={url} target="_blank" rel="noopener noreferrer" className="font-bold text-lg mb-2 hover:underline">
          {title}
        </a>
      ) : (
        <h3 className="font-bold text-lg mb-2">{title}</h3>
      )}
      {source && <p className="text-sm text-gray-500 mb-2">Source: {source}</p>}
      {summary && <p className="text-gray-700 dark:text-gray-300">{summary}</p>}
    </div>
  );
};

export default NewsCard;
