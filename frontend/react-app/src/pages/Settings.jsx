import React from "react";
import CustomizationPanel from "../components/CustomizationPanel";

function Settings() {
  return (
    <div className="p-6 bg-gray-50 dark:bg-gray-900 text-gray-900 dark:text-gray-100 min-h-screen">
      <h2 className="text-2xl font-semibold mb-4">Settings</h2>
      <CustomizationPanel />
    </div>
  );
}

export default Settings;
