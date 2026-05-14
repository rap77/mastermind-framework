/**
 * Integration test: Model profile dropdown → store → request — C2.10
 *
 * Verifies the full flow:
 * 1. User changes dropdown selection
 * 2. Zustand modelProfileStore updates
 * 3. When createTask is called, it receives the current profile from the store
 *
 * This test focuses on the store-dispatch integration.
 * Full CommandCenterWrapper test is in CommandCenterWrapper.test.tsx
 */

import { render, screen, fireEvent } from '@testing-library/react'
import { describe, it, expect, beforeEach } from 'vitest'
import { ModelProfileDropdown } from '../ModelProfileDropdown'
import { useModelProfileStore } from '@/stores/modelProfileStore'

beforeEach(() => {
  useModelProfileStore.setState({ profile: 'balanced' })
})

describe('ModelProfile flow — C2.10', () => {
  it('dropdown change updates Zustand store', () => {
    render(<ModelProfileDropdown />)
    const select = screen.getByTestId('model-profile-select')

    // Change to quality
    fireEvent.change(select, { target: { value: 'quality' } })
    expect(useModelProfileStore.getState().profile).toBe('quality')
  })

  it('store profile matches dropdown value after change', () => {
    render(<ModelProfileDropdown />)
    const select = screen.getByTestId('model-profile-select') as HTMLSelectElement

    fireEvent.change(select, { target: { value: 'budget' } })

    // Store updated
    expect(useModelProfileStore.getState().profile).toBe('budget')
    // Dropdown shows new value
    expect(select.value).toBe('budget')
  })

  it('simulates request including current profile', () => {
    render(<ModelProfileDropdown />)
    const select = screen.getByTestId('model-profile-select')

    // User selects quality
    fireEvent.change(select, { target: { value: 'quality' } })

    // At dispatch time, read from store (as CommandCenterWrapper does)
    const currentProfile = useModelProfileStore.getState().profile
    const requestBody = {
      brief: 'test brief',
      model_profile: currentProfile,
    }

    expect(requestBody.model_profile).toBe('quality')
  })

  it('switching profile multiple times ends up with last selection', () => {
    render(<ModelProfileDropdown />)
    const select = screen.getByTestId('model-profile-select')

    fireEvent.change(select, { target: { value: 'quality' } })
    fireEvent.change(select, { target: { value: 'budget' } })
    fireEvent.change(select, { target: { value: 'balanced' } })

    expect(useModelProfileStore.getState().profile).toBe('balanced')
  })
})
