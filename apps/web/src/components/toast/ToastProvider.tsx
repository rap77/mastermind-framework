'use client';

import { useEffect, useState } from 'react';
import { subscribe, Toast, removeToast } from '@/lib/toast';
import { cn } from '@/lib/utils';
import { CheckCircle, AlertCircle, Info } from 'lucide-react';

export function ToastProvider() {
  const [toasts, setToasts] = useState<Toast[]>([]);

  useEffect(() => {
    const unsubscribe = subscribe(setToasts);
    return unsubscribe;
  }, []);

  if (toasts.length === 0) return null;

  return (
    <div className="fixed bottom-4 right-4 z-[100] flex flex-col gap-2">
      {toasts.map((toast) => (
        <div
          key={toast.id}
          className={cn(
            'flex items-center gap-3 px-4 py-3 rounded-lg shadow-lg border min-w-[300px] max-w-md animate-in slide-in-from-right',
            toast.type === 'success' &&
              'bg-green-50 border-green-200 text-green-900 dark:bg-green-900/20 dark:border-green-800 dark:text-green-100',
            toast.type === 'error' &&
              'bg-red-50 border-red-200 text-red-900 dark:bg-red-900/20 dark:border-red-800 dark:text-red-100',
            toast.type === 'info' &&
              'bg-blue-50 border-blue-200 text-blue-900 dark:bg-blue-900/20 dark:border-blue-800 dark:text-blue-100'
          )}
        >
          {toast.type === 'success' && (
            <CheckCircle className="w-5 h-5 flex-shrink-0" />
          )}
          {toast.type === 'error' && (
            <AlertCircle className="w-5 h-5 flex-shrink-0" />
          )}
          {toast.type === 'info' && (
            <Info className="w-5 h-5 flex-shrink-0" />
          )}
          <span className="flex-1 text-sm font-medium">{toast.message}</span>
          <button
            onClick={() => removeToast(toast.id)}
            className="text-current/60 hover:text-current transition-colors"
            aria-label="Close notification"
          >
            ×
          </button>
        </div>
      ))}
    </div>
  );
}
