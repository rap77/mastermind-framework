'use client'

import React, { Component, ErrorInfo, ReactNode } from 'react'
import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'

/**
 * Props for SimulationErrorBoundary
 */
interface SimulationErrorBoundaryProps {
  children: ReactNode
  fallback?: ReactNode
}

/**
 * State for SimulationErrorBoundary
 */
interface SimulationErrorBoundaryState {
  hasError: boolean
  error: Error | null
  errorInfo: ErrorInfo | null
}

/**
 * SimulationErrorBoundary — Error boundary for Simulation component
 *
 * **Features:**
 * - Catches JavaScript errors anywhere in the Simulation component tree
 * - Displays user-friendly error messages with technical details
 * - Provides recovery options (retry, load different execution, go to dashboard)
 * - Logs errors to console for debugging
 * - Preserves component stack trace for error reporting
 *
 * @example
 * ```tsx
 * <SimulationErrorBoundary>
 *   <SimulationCanvas />
 * </SimulationErrorBoundary>
 * ```
 */
export class SimulationErrorBoundary extends Component<
  SimulationErrorBoundaryProps,
  SimulationErrorBoundaryState
> {
  constructor(props: SimulationErrorBoundaryProps) {
    super(props)
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
    }
  }

  static getDerivedStateFromError(error: Error): Partial<SimulationErrorBoundaryState> {
    // Update state so the next render will show the fallback UI
    return { hasError: true }
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo): void {
    // Log the error to console for debugging
    console.error('Simulation Error Boundary caught an error:', error, errorInfo)

    // Store error details in state for display
    this.setState({
      error,
      errorInfo,
    })

    // TODO: Send error to error reporting service (e.g., Sentry)
    // logErrorToService(error, errorInfo, 'SimulationErrorBoundary')
  }

  handleRetry = (): void => {
    // Reset error state and retry
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null,
    })
  }

  handleGoToFlowDesigner = (): void => {
    // Navigate to Flow Designer
    window.location.href = '/flow-designer'
  }

  render(): ReactNode {
    if (this.state.hasError) {
      // Custom fallback UI
      if (this.props.fallback) {
        return this.props.fallback
      }

      // Default error UI
      return (
        <div className="flex items-center justify-center min-h-screen bg-background p-4">
          <Card className="max-w-2xl w-full p-6 border-destructive">
            <div className="space-y-4">
              {/* Error header */}
              <div className="flex items-center gap-3">
                <div className="text-4xl" role="img" aria-label="Error icon">
                  ⚠️
                </div>
                <div>
                  <h1 className="text-xl font-semibold text-destructive">
                    Simulation Error
                  </h1>
                  <p className="text-sm text-muted-foreground">
                    Something went wrong while replaying the execution
                  </p>
                </div>
              </div>

              {/* Error message */}
              {this.state.error && (
                <div className="bg-destructive/10 border border-destructive/20 rounded-lg p-4">
                  <p className="text-sm font-mono text-destructive">
                    {this.state.error.toString()}
                  </p>
                </div>
              )}

              {/* Component stack (for debugging) */}
              {this.state.errorInfo && (
                <details className="bg-muted rounded-lg p-4">
                  <summary className="cursor-pointer text-sm font-medium">
                    Technical Details (click to expand)
                  </summary>
                  <pre className="mt-3 text-xs overflow-auto max-h-40 font-mono">
                    {this.state.errorInfo.componentStack}
                  </pre>
                </details>
              )}

              {/* Recovery actions */}
              <div className="flex gap-3 pt-2">
                <Button onClick={this.handleRetry} variant="default">
                  Try Again
                </Button>
                <Button
                  onClick={this.handleGoToFlowDesigner}
                  variant="outline"
                >
                  Go to Flow Designer
                </Button>
                <Button
                  onClick={() => (window.location.href = '/')}
                  variant="ghost"
                >
                  Go to Dashboard
                </Button>
              </div>

              {/* Help text */}
              <p className="text-xs text-muted-foreground pt-2">
                If this error persists, please try loading a different execution or contact
                support.
              </p>
            </div>
          </Card>
        </div>
      )
    }

    return this.props.children
  }
}
