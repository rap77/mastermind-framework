/**
 * Application-wide constants
 *
 * Centralized location for magic numbers and configuration values
 * to improve maintainability and prevent duplication.
 */

// ─── Timeline & Animation ───────────────────────────────────────────────────────

/**
 * Minimum touch target size for mobile accessibility (WCAG AA)
 * @see https://www.w3.org/WAI/WCAG21/Understanding/target-size.html
 */
export const MIN_TOUCH_TARGET_SIZE = 44;

/**
 * Default animation duration in milliseconds for smooth transitions
 */
export const DEFAULT_ANIMATION_DURATION = 200;

/**
 * Timeline scrubber thumb animation duration in milliseconds
 */
export const SCRUBBER_THUMB_ANIMATION_DURATION = 100;

// ─── Simulation ─────────────────────────────────────────────────────────────────

/**
 * Default simulation playback speed multiplier
 */
export const DEFAULT_PLAYBACK_SPEED = 1;

/**
 * Maximum simulation playback speed multiplier
 */
export const MAX_PLAYBACK_SPEED = 5;

/**
 * Minimum simulation playback speed multiplier
 */
export const MIN_PLAYBACK_SPEED = 0.5;

/**
 * Available playback speed options
 */
export const PLAYBACK_SPEEDS = [0.5, 1, 2, 5] as const;

/**
 * Latency threshold in milliseconds for showing "SLOW" badge on nodes
 */
export const SLOW_NODE_THRESHOLD_MS = 1000;

// ─── Flow Designer ──────────────────────────────────────────────────────────────

/**
 * Default node width in pixels for React Flow
 */
export const DEFAULT_NODE_WIDTH = 200;

/**
 * Default node height in pixels for React Flow
 */
export const DEFAULT_NODE_HEIGHT = 80;

/**
 * Minimum zoom level for React Flow canvas
 */
export const MIN_ZOOM_LEVEL = 0.1;

/**
 * Maximum zoom level for React Flow canvas
 */
export const MAX_ZOOM_LEVEL = 2;

/**
 * Default zoom level for React Flow canvas
 */
export const DEFAULT_ZOOM_LEVEL = 1;

// ─── UI Components ───────────────────────────────────────────────────────────────

/**
 * Default toast notification duration in milliseconds
 */
export const DEFAULT_TOAST_DURATION = 3000;

/**
 * Default border radius for rounded components in pixels
 */
export const DEFAULT_BORDER_RADIUS = 8;

/**
 * Small border radius for subtly rounded components in pixels
 */
export const SMALL_BORDER_RADIUS = 4;

/**
 * Large border radius for highly rounded components in pixels
 */
export const LARGE_BORDER_RADIUS = 12;

// ─── API & Data ─────────────────────────────────────────────────────────────────

/**
 * Maximum number of retry attempts for failed API requests
 */
export const MAX_API_RETRY_ATTEMPTS = 3;

/**
 * Delay between API retry attempts in milliseconds
 */
export const API_RETRY_DELAY_MS = 1000;

/**
 * Default timeout for API requests in milliseconds
 */
export const DEFAULT_API_TIMEOUT_MS = 30000;

// ─── Performance ────────────────────────────────────────────────────────────────

/**
 * Maximum number of items to render in a virtual list before enabling virtualization
 */
export const VIRTUAL_LIST_THRESHOLD = 100;

/**
 * Debounce delay for search inputs in milliseconds
 */
export const SEARCH_DEBOUNCE_DELAY_MS = 300;

/**
 * Throttle delay for scroll events in milliseconds
 */
export const SCROLL_THROTTLE_DELAY_MS = 100;

// ─── Accessibility ───────────────────────────────────────────────────────────────

/**
 * Maximum label length for screen readers before truncation
 */
export const MAX_ARIA_LABEL_LENGTH = 100;

/**
 * Delay before showing keyboard focus indicators in milliseconds
 */
export const FOCUS_INDICATOR_DELAY_MS = 150;
