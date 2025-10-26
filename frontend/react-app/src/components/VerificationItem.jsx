import React from 'react';

const VerificationItem = ({ item }) => {
  return (
    <div className="p-4 border rounded bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100">
      <div className="flex justify-between items-start">
        <div>
          <h3 className="font-semibold">{item.claim}</h3>
          <p className="text-sm text-gray-600 dark:text-gray-300">{item.summary}</p>
        </div>
        <div className="text-right">
          <div className="font-bold">{item.status}</div>
          <div className="text-xs text-gray-500">{item.created_at}</div>
        </div>
      </div>
      <div className="mt-2 text-xs text-gray-700 dark:text-gray-300">
        Sources: {item.sources && item.sources.length ? item.sources.join(', ') : '—'}
      </div>
    </div>
  );
};

export default VerificationItem;
