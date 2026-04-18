/**
 * Centralized error handling utilities
 *
 * Provides a consistent way to handle, format, and report errors across the application.
 * Includes custom error classes, error formatters, and error logging utilities.
 */

// ─── Custom Error Classes ───────────────────────────────────────────────────────

/**
 * Base application error class
 * All custom errors should extend this class
 */
export class AppError extends Error {
  constructor(
    message: string,
    public code: string,
    public statusCode: number = 500,
    public details?: Record<string, unknown>
  ) {
    super(message)
    this.name = this.constructor.name
    Error.captureStackTrace?.(this, this.constructor)
  }
}

/**
 * API request error
 * Thrown when API requests fail
 */
export class APIError extends AppError {
  constructor(
    message: string,
    public statusCode: number = 500,
    public endpoint?: string,
    details?: Record<string, unknown>
  ) {
    super(message, 'API_ERROR', statusCode, details)
    this.name = 'APIError'
  }
}

/**
 * Network error
 * Thrown when network requests fail due to connectivity issues
 */
export class NetworkError extends AppError {
  constructor(message: string = 'Network request failed', details?: Record<string, unknown>) {
    super(message, 'NETWORK_ERROR', 0, details)
    this.name = 'NetworkError'
  }
}

/**
 * Validation error
 * Thrown when user input validation fails
 */
export class ValidationError extends AppError {
  constructor(message: string, public field?: string, details?: Record<string, unknown>) {
    super(message, 'VALIDATION_ERROR', 400, details)
    this.name = 'ValidationError'
  }
}

/**
 * Authentication error
 * Thrown when authentication fails or session expires
 */
export class AuthenticationError extends AppError {
  constructor(message: string = 'Authentication failed', details?: Record<string, unknown>) {
    super(message, 'AUTH_ERROR', 401, details)
    this.name = 'AuthenticationError'
  }
}

/**
 * Authorization error
 * Thrown when user lacks permission to perform an action
 */
export class AuthorizationError extends AppError {
  constructor(message: string = 'Permission denied', details?: Record<string, unknown>) {
    super(message, 'AUTHORIZATION_ERROR', 403, details)
    this.name = 'AuthorizationError'
  }
}

/**
 * Not found error
 * Thrown when a requested resource is not found
 */
export class NotFoundError extends AppError {
  constructor(resource: string, identifier?: string) {
    const message = identifier
      ? `${resource} '${identifier}' not found`
      : `${resource} not found`
    super(message, 'NOT_FOUND', 404, { resource, identifier })
    this.name = 'NotFoundError'
  }
}

/**
 * Flow execution error
 * Thrown when flow execution fails
 */
export class FlowExecutionError extends AppError {
  constructor(
    message: string,
    public flowId?: string,
    public executionId?: string,
    details?: Record<string, unknown>
  ) {
    super(message, 'FLOW_EXECUTION_ERROR', 500, {
      flowId,
      executionId,
      ...details,
    })
    this.name = 'FlowExecutionError'
  }
}

/**
 * Simulation error
 * Thrown when simulation replay fails
 */
export class SimulationError extends AppError {
  constructor(
    message: string,
    public executionId?: string,
    details?: Record<string, unknown>
  ) {
    super(message, 'SIMULATION_ERROR', 500, { executionId, ...details })
    this.name = 'SimulationError'
  }
}

// ─── Error Utilities ─────────────────────────────────────────────────────────────

/**
 * Check if an error is an instance of AppError or a standard Error
 */
export function isError(error: unknown): error is Error {
  return error instanceof Error
}

/**
 * Check if an error is an instance of a specific error class
 */
export function isErrorCode<T extends AppError>(
  error: unknown,
  errorCode: string
): error is T {
  return error instanceof AppError && error.code === errorCode
}

/**
 * Get a user-friendly error message
 * Falls back to a generic message if the error is not recognized
 */
export function getErrorMessage(error: unknown): string {
  if (isError(error)) {
    return error.message
  }
  if (typeof error === 'string') {
    return error
  }
  return 'An unexpected error occurred. Please try again.'
}

/**
 * Get error code from an error
 * Returns 'UNKNOWN_ERROR' if no code is found
 */
export function getErrorCode(error: unknown): string {
  if (error instanceof AppError) {
    return error.code
  }
  return 'UNKNOWN_ERROR'
}

/**
 * Get HTTP status code from an error
 * Returns 500 if no status code is found
 */
export function getErrorStatusCode(error: unknown): number {
  if (error instanceof AppError) {
    return error.statusCode
  }
  return 500
}

/**
 * Format error for logging
 * Includes error message, code, stack trace, and details
 */
export function formatErrorForLogging(error: unknown): string {
  if (error instanceof AppError) {
    return [
      `[${error.code}] ${error.message}`,
      error.stack || '',
      error.details ? JSON.stringify(error.details, null, 2) : '',
    ].filter(Boolean).join('\n')
  }
  if (isError(error)) {
    return [error.message, error.stack || ''].filter(Boolean).join('\n')
  }
  return String(error)
}

/**
 * Format error for display to user
 * Sanitizes error details and removes sensitive information
 */
export function formatErrorForDisplay(error: unknown): string {
  if (error instanceof ValidationError) {
    return error.message
  }
  if (error instanceof AuthenticationError) {
    return 'Your session has expired. Please log in again.'
  }
  if (error instanceof AuthorizationError) {
    return 'You do not have permission to perform this action.'
  }
  if (error instanceof NotFoundError) {
    return error.message
  }
  if (error instanceof NetworkError) {
    return 'Network connection failed. Please check your internet connection.'
  }
  if (error instanceof APIError) {
    // Don't expose internal API errors to users
    if (error.statusCode >= 500) {
      return 'A server error occurred. Please try again later.'
    }
    return error.message
  }
  return getErrorMessage(error)
}

/**
 * Log error to console
 * In production, this should send errors to an error tracking service
 */
export function logError(error: unknown, context?: string): void {
  const errorMessage = formatErrorForLogging(error)
  const contextPrefix = context ? `[${context}] ` : ''

  if (error instanceof AppError) {
    console.error(`${contextPrefix}${errorMessage}`)
  } else {
    console.error(`${contextPrefix}Unexpected error:`, error)
  }

  // TODO: Send to error tracking service (e.g., Sentry, LogRocket)
  // if (typeof window !== 'undefined' && window.Sentry) {
  //   window.Sentry.captureException(error)
  // }
}

/**
 * Handle error with user notification
 * Logs the error and returns a user-friendly message
 */
export function handleError(error: unknown, context?: string): string {
  logError(error, context)
  return formatErrorForDisplay(error)
}

/**
 * Create an error handler for React components
 * Returns a function that can be used in catch blocks
 */
export function createErrorHandler(context: string) {
  return (error: unknown): string => {
    return handleError(error, context)
  }
}

/**
 * Assert a condition is true, throw error if not
 * Useful for invariant checking
 */
export function assert(condition: unknown, message: string): asserts condition {
  if (!condition) {
    throw new Error(`Assertion failed: ${message}`)
  }
}

/**
 * Assert a value is not null/undefined, throw error if it is
 * Useful for type narrowing
 */
export function assertNonNull<T>(
  value: T | null | undefined,
  message: string = 'Value should not be null'
): T {
  if (value === null || value === undefined) {
    throw new Error(`Assertion failed: ${message}`)
  }
  return value
}

// ─── Error Recovery Strategies ───────────────────────────────────────────────────

/**
 * Error recovery strategy options
 */
export enum RecoveryStrategy {
  /** Show error to user and let them decide */
  NONE = 'none',
  /** Automatically retry the failed operation */
  RETRY = 'retry',
  /** Fall back to a default value or behavior */
  FALLBACK = 'fallback',
  /** Redirect to a safe location */
  REDIRECT = 'redirect',
  /** Reload the page */
  RELOAD = 'reload',
}

/**
 * Determine recovery strategy based on error type
 */
export function getRecoveryStrategy(error: unknown): RecoveryStrategy {
  if (error instanceof NetworkError) {
    return RecoveryStrategy.RETRY
  }
  if (error instanceof AuthenticationError) {
    return RecoveryStrategy.REDIRECT
  }
  if (error instanceof ValidationError) {
    return RecoveryStrategy.NONE
  }
  if (error instanceof APIError && error.statusCode >= 500) {
    return RecoveryStrategy.RETRY
  }
  return RecoveryStrategy.NONE
}
