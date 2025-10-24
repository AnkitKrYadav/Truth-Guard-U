import React from "react";

function About() {
  return (
    <div className="p-6 bg-gray-50 dark:bg-gray-900 text-gray-900 dark:text-gray-100 min-h-screen">
      <h2 className="text-2xl font-semibold mb-4">About TruthGuard</h2>
      <div className="prose prose-gray dark:prose-invert max-w-none">
        <p>
          TruthGuard is an AI-powered fact-verification platform designed to combat misinformation.
          It orchestrates LLMs, trusted news APIs, and community/expert feedback to verify claims in near real time.
        </p>
        <ul>
          <li>Live trending and verification with OpenAI/HuggingFace fallback</li>
          <li>Expert overrides and badges</li>
          <li>Region and category filters</li>
          <li>Admin dashboard for users/experts/badges/regions/categories</li>
        </ul>
        <p className="text-sm text-gray-600 dark:text-gray-300">
          Built with Flask, React, Tailwind, and LangChain. Feedback welcome.
        </p>
      </div>
    </div>
  );
}

export default About;
