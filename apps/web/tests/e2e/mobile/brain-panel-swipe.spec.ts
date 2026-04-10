/**
 * Brain Panel Swipe Gesture Tests (Mobile)
 *
 * Brain #7 Condition 4 ✅ FIXED:
 * - Swipe gesture success rate ≥ 95%
 * - Measured via 100 test swipes per device
 * - Success = action revealed on first swipe
 *
 * NOTE: BrowserStack account required ($39/month)
 * - Use device emulators for now (defer BrowserStack to v3.1)
 * - Tests: iPhone 14, Pixel 5 (or equivalent emulators)
 */

import { test, expect } from '@playwright/test'

test.describe('Brain Panel Mobile Swipe Gestures', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to brain panel
    await page.goto('/dashboard')
    await page.waitForSelector('[data-testid="active-agents-panel"]')
  })

  test('swipe left reveals brain actions', async ({ page }) => {
    // Find a brain card
    const brainCard = page.locator('[data-testid="brain-card"]').first()

    // Swipe left on the brain card
    await brainCard.evaluate((el) => {
      const touchStart = new TouchEvent('touchstart', {
        bubbles: true,
        touches: [{ clientX: 300, clientY: 100 }] as any
      })
      const touchMove = new TouchEvent('touchmove', {
        bubbles: true,
        touches: [{ clientX: 100, clientY: 100 }] as any
      })
      const touchEnd = new TouchEvent('touchend', {
        bubbles: true,
        changedTouches: [{ clientX: 100, clientY: 100 }] as any
      })

      el.dispatchEvent(touchStart)
      el.dispatchEvent(touchMove)
      el.dispatchEvent(touchEnd)
    })

    // Verify actions button is revealed
    const actionsButton = brainCard.locator('[aria-label^="Actions for"]')
    await expect(actionsButton).toBeVisible()
  })

  test('touch targets meet WCAG size requirements (≥ 44x44px)', async ({ page }) => {
    const brainCard = page.locator('[data-testid="brain-card"]').first()

    // Get button bounding box
    const button = brainCard.locator('button')
    const box = await button.boundingBox()

    expect(box).toBeTruthy()
    expect(box!.width).toBeGreaterThanOrEqual(44)
    expect(box!.height).toBeGreaterThanOrEqual(44)
  })

  /**
   * Swipe Gesture Success Rate Test
   *
   * Brain #7 Condition 4: Measure 100 test swipes per device
   * Target: ≥ 95% success rate (success = action revealed on first swipe)
   *
   * Run with: npx playwright test brain-panel-swipe.spec.ts --project=chromium
   */
  test('swipe gesture success rate ≥ 95%', async ({ page }) => {
    const totalSwipes = 100
    let successCount = 0

    for (let i = 0; i < totalSwipes; i++) {
      const brainCard = page.locator('[data-testid="brain-card"]').first()

      // Swipe left
      await brainCard.evaluate((el) => {
        const touchStart = new TouchEvent('touchstart', {
          bubbles: true,
          touches: [{ clientX: 300, clientY: 100 }] as any
        })
        const touchMove = new TouchEvent('touchmove', {
          bubbles: true,
          touches: [{ clientX: 100, clientY: 100 }] as any
        })
        const touchEnd = new TouchEvent('touchend', {
          bubbles: true,
          changedTouches: [{ clientX: 100, clientY: 100 }] as any
        })

        el.dispatchEvent(touchStart)
        el.dispatchEvent(touchMove)
        el.dispatchEvent(touchEnd)
      })

      // Check if actions button is revealed
      const actionsButton = brainCard.locator('[aria-label^="Actions for"]')
      const isVisible = await actionsButton.isVisible().catch(() => false)

      if (isVisible) {
        successCount++
      }

      // Reset for next swipe (swipe right to hide)
      await brainCard.evaluate((el) => {
        const touchStart = new TouchEvent('touchstart', {
          bubbles: true,
          touches: [{ clientX: 100, clientY: 100 }] as any
        })
        const touchMove = new TouchEvent('touchmove', {
          bubbles: true,
          touches: [{ clientX: 300, clientY: 100 }] as any
        })
        const touchEnd = new TouchEvent('touchend', {
          bubbles: true,
          changedTouches: [{ clientX: 300, clientY: 100 }] as any
        })

        el.dispatchEvent(touchStart)
        el.dispatchEvent(touchMove)
        el.dispatchEvent(touchEnd)
      })
    }

    const successRate = (successCount / totalSwipes) * 100
    console.log(`Swipe gesture success rate: ${successRate}% (${successCount}/${totalSwipes})`)

    expect(successRate).toBeGreaterThanOrEqual(95)
  })
})

/**
 * BrowserStack Device Testing
 *
 * TODO (Deferred to v3.1):
 * - Create BrowserStack account ($39/month commitment)
 * - Install @browserstack/playwright plugin
 * - Configure devices: iPhone 14, Pixel 5
 * - Run swipe gesture tests on real devices
 * - Document touch response times (< 100ms target)
 *
 * For now, use device emulators in Playwright.
 */
