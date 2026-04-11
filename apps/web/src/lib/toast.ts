/**
 * Simple toast notification utility for command palette feedback
 */

export type ToastType = 'success' | 'error' | 'info';

export interface Toast {
  id: string;
  message: string;
  type: ToastType;
}

let toasts: Toast[] = [];
let listeners: ((toasts: Toast[]) => void)[] = [];

function generateId(): string {
  return `toast-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
}

export function toast(message: string, type: ToastType = 'info'): void {
  const newToast: Toast = {
    id: generateId(),
    message,
    type,
  };

  toasts = [...toasts, newToast];
  notifyListeners();

  // Auto-remove after 3 seconds
  setTimeout(() => {
    removeToast(newToast.id);
  }, 3000);
}

export function removeToast(id: string): void {
  toasts = toasts.filter((t) => t.id !== id);
  notifyListeners();
}

export function subscribe(listener: (toasts: Toast[]) => void): () => void {
  listeners = [...listeners, listener];
  listener(toasts);

  // Return unsubscribe function
  return () => {
    listeners = listeners.filter((l) => l !== listener);
  };
}

function notifyListeners(): void {
  listeners.forEach((listener) => listener(toasts));
}

// Convenience functions
export const toastSuccess = (message: string) => toast(message, 'success');
export const toastError = (message: string) => toast(message, 'error');
export const toastInfo = (message: string) => toast(message, 'info');
