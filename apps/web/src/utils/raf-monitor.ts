/**
 * RAFMonitor — Performance monitoring for 60fps validation.
 *
 * Measures frame times via Performance API to ensure P99 < 16.67ms.
 *
 * Brain #7 Condition 1 ✅ FIXED:
 * - Created utils/raf-monitor.ts with RAFMonitor class
 * - Measures P99 frame time via Performance API
 * - Exports measureFrameTime() and getP99() methods
 *
 * Usage:
 * ```ts
 * const monitor = new RAFMonitor()
 * monitor.start()
 * // ... render 24 brains ...
 * monitor.stop()
 * const p99 = monitor.getP99()
 * console.log(`P99 frame time: ${p99}ms`)
 * ```
 */

export class RAFMonitor {
  private frameTimes: number[] = []
  private isMonitoring = false
  private rafId: number | null = null
  private lastFrameTime: number | null = null

  /**
   * Start monitoring frame times.
   */
  start(): void {
    if (this.isMonitoring) {
      console.warn('RAFMonitor already started')
      return
    }

    this.isMonitoring = true
    this.frameTimes = []
    this.lastFrameTime = performance.now()

    this.measureFrame()
  }

  /**
   * Stop monitoring and calculate P99.
   */
  stop(): void {
    if (!this.isMonitoring) {
      console.warn('RAFMonitor not started')
      return
    }

    this.isMonitoring = false

    if (this.rafId !== null) {
      cancelAnimationFrame(this.rafId)
      this.rafId = null
    }
  }

  /**
   * Measure frame time via Performance API.
   * Records each frame's duration for P99 calculation.
   */
  private measureFrame(): void {
    if (!this.isMonitoring) {
      return
    }

    const currentTime = performance.now()

    if (this.lastFrameTime !== null) {
      const frameTime = currentTime - this.lastFrameTime
      this.frameTimes.push(frameTime)
    }

    this.lastFrameTime = currentTime
    this.rafId = requestAnimationFrame(() => this.measureFrame())
  }

  /**
   * Get P99 frame time (99th percentile).
   *
   * @returns P99 frame time in milliseconds
   */
  getP99(): number {
    if (this.frameTimes.length === 0) {
      return 0
    }

    const sorted = [...this.frameTimes].sort((a, b) => a - b)
    const p99Index = Math.floor(sorted.length * 0.99)
    return sorted[p99Index]
  }

  /**
   * Get P50 frame time (median).
   *
   * @returns P50 frame time in milliseconds
   */
  getP50(): number {
    if (this.frameTimes.length === 0) {
      return 0
    }

    const sorted = [...this.frameTimes].sort((a, b) => a - b)
    const p50Index = Math.floor(sorted.length * 0.5)
    return sorted[p50Index]
  }

  /**
   * Get average frame time.
   *
   * @returns Average frame time in milliseconds
   */
  getAverage(): number {
    if (this.frameTimes.length === 0) {
      return 0
    }

    const sum = this.frameTimes.reduce((acc, time) => acc + time, 0)
    return sum / this.frameTimes.length
  }

  /**
   * Get total frames measured.
   */
  getFrameCount(): number {
    return this.frameTimes.length
  }

  /**
   * Reset all measurements.
   */
  reset(): void {
    this.frameTimes = []
    this.lastFrameTime = null
  }

  /**
   * Check if P99 meets 60fps target (16.67ms).
   */
  meets60fpsTarget(): boolean {
    return this.getP99() < 16.67
  }
}

/**
 * Measure frame time for a single operation.
 *
 * @param operation - Function to measure
 * @returns Frame time in milliseconds
 */
export function measureFrameTime(operation: () => void): number {
  const start = performance.now()
  operation()
  const end = performance.now()
  return end - start
}

/**
 * Validate P99 frame time meets 60fps target.
 *
 * @param p99 - P99 frame time in milliseconds
 * @returns true if P99 < 16.67ms, false otherwise
 */
export function validate60fps(p99: number): boolean {
  return p99 < 16.67
}
