/**
 * Simple logger utility for consistent logging across the app
 */

type LogLevel = 'info' | 'warn' | 'error'

interface Logger {
  info: (message: string, ...args: unknown[]) => void
  warn: (message: string, ...args: unknown[]) => void
  error: (message: string, ...args: unknown[]) => void
}

const isDevelopment = process.env.NODE_ENV === 'development'

export const logger: Logger = {
  info: (message: string, ...args: unknown[]) => {
    if (isDevelopment) {
      console.log(`[INFO] ${message}`, ...args)
    }
  },
  warn: (message: string, ...args: unknown[]) => {
    if (isDevelopment) {
      console.warn(`[WARN] ${message}`, ...args)
    }
  },
  error: (message: string, ...args: unknown[]) => {
    // Always log errors
    console.error(`[ERROR] ${message}`, ...args)
  },
}
