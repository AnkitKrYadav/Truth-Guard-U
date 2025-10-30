import React, { createContext, useCallback, useContext, useMemo, useState } from "react";

const ToastContext = createContext({ toast: () => {} });

let idSeq = 1;

export function ToastProvider({ children }) {
  const [toasts, setToasts] = useState([]);

  const dismiss = useCallback((id) => {
    setToasts((list) => list.filter((t) => t.id !== id));
  }, []);

  const toast = useCallback((opts) => {
    const id = idSeq++;
    const t = {
      id,
      title: opts?.title || "",
      message: opts?.message || "",
      type: opts?.type || "info", // info | success | warning | error
      timeout: typeof opts?.timeout === "number" ? opts.timeout : 2500,
    };
    setToasts((list) => [...list, t]);
    if (t.timeout > 0) {
      setTimeout(() => dismiss(id), t.timeout);
    }
    return id;
  }, [dismiss]);

  const value = useMemo(() => ({ toast, dismiss }), [toast, dismiss]);

  return (
    <ToastContext.Provider value={value}>
      {children}
      {/* Viewport */}
      <div className="fixed bottom-4 right-4 z-50 space-y-2">
        {toasts.map((t) => (
          <div key={t.id} className={
            `max-w-sm w-80 rounded-xl border shadow-lg px-4 py-3 backdrop-blur
             ${t.type === 'success' ? 'bg-emerald-50/90 border-emerald-200 text-emerald-900 dark:bg-emerald-900/40 dark:border-emerald-800 dark:text-emerald-100'
               : t.type === 'warning' ? 'bg-amber-50/90 border-amber-200 text-amber-900 dark:bg-amber-900/40 dark:border-amber-800 dark:text-amber-100'
               : t.type === 'error' ? 'bg-rose-50/90 border-rose-200 text-rose-900 dark:bg-rose-900/40 dark:border-rose-800 dark:text-rose-100'
               : 'bg-white/90 border-gray-200 text-gray-900 dark:bg-gray-900/60 dark:border-gray-700 dark:text-gray-100'}`
          }>
            {t.title && <div className="font-semibold mb-0.5">{t.title}</div>}
            {t.message && <div className="text-sm opacity-90">{t.message}</div>}
            <button onClick={() => dismiss(t.id)} className="absolute top-1.5 right-2 text-xs opacity-70 hover:opacity-100">✕</button>
          </div>
        ))}
      </div>
    </ToastContext.Provider>
  );
}

export function useToast() {
  return useContext(ToastContext);
}
