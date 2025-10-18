import React from "react";
import { useUserPrefs } from "../context/UserPrefsContext";

function CustomizationPanel() {
  const { userPrefs, updatePrefs } = useUserPrefs();

  return (
    <div className="bg-white dark:bg-gray-800 shadow-md rounded-lg p-4 space-y-4">
      <div>
        <label className="block text-gray-700 dark:text-gray-300 font-medium mb-1">
          Preferred Language
        </label>
        <select
          value={userPrefs.preferredLanguage}
          onChange={(e) => updatePrefs({ preferredLanguage: e.target.value })}
          className="w-full p-2 border rounded dark:bg-gray-700 dark:border-gray-600"
        >
          <option>English</option>
          <option>Hindi</option>
          <option>Spanish</option>
          <option>French</option>
        </select>
      </div>

      <div>
        <label className="flex items-center gap-2 text-gray-700 dark:text-gray-300 font-medium">
          <input
            type="checkbox"
            checked={userPrefs.showConfidence}
            onChange={(e) => updatePrefs({ showConfidence: e.target.checked })}
            className="rounded"
          />
          Show confidence levels in results
        </label>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label className="block text-gray-700 dark:text-gray-300 font-medium mb-1">Default Region</label>
          <select
            value={userPrefs.defaultRegion || "in"}
            onChange={(e) => updatePrefs({ defaultRegion: e.target.value })}
            className="w-full p-2 border rounded dark:bg-gray-700 dark:border-gray-600"
          >
            {['in','us','gb','au','ca','de','fr','jp'].map(r => (
              <option key={r} value={r}>{r.toUpperCase()}</option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-gray-700 dark:text-gray-300 font-medium mb-1">Default Model</label>
          <select
            value={userPrefs.defaultModel || "openai"}
            onChange={(e) => updatePrefs({ defaultModel: e.target.value })}
            className="w-full p-2 border rounded dark:bg-gray-700 dark:border-gray-600"
          >
            <option value="openai">OpenAI</option>
            <option value="hf">HuggingFace</option>
          </select>
        </div>
      </div>

      <div>
        <label className="flex items-center gap-2 text-gray-700 dark:text-gray-300 font-medium">
          <input
            type="checkbox"
            checked={userPrefs.compactCards || false}
            onChange={(e) => updatePrefs({ compactCards: e.target.checked })}
            className="rounded"
          />
          Compact cards layout
        </label>
      </div>
    </div>
  );
}

export default CustomizationPanel;
