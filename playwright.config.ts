import { defineConfig, devices } from '@playwright/test';

/**
 * Playwright E2E test configuration.
 *
 * Configuration for Phase 3 smoke tests and E2E validation.
 * Tests are located in tests/e2e/ directory.
 *
 * Requirements: UI-05, UI-09, UI-10, PERF-04
 */
export default defineConfig({
  testDir: './tests/e2e',
  fullyParallel: false,  // Run serially for smoke tests
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: 1,  // Single worker for stability
  reporter: 'html',

  use: {
    baseURL: 'http://localhost:8000',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    headless: true,
  },

  projects: [
    {
      name: 'Desktop',
      use: { ...devices['Desktop Chrome'] },
    },
    {
      name: 'Mobile',
      use: { ...devices['iPhone 13'] },
    },
  ],

  webServer: {
    command: 'uv run uvicorn mastermind_cli.api.app:create_app --factory',
    url: 'http://localhost:8000',
    reuseExistingServer: !process.env.CI,
    timeout: 120000,
  },
});
