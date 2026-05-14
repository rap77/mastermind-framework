/**
 * Tests for ModelProfileDropdown — C2.06
 *
 * Verifies:
 * - Renders with default "balanced" selected
 * - Shows all three profile options (quality, balanced, budget)
 * - Changing selection updates the Zustand modelProfileStore
 */

import { render, screen, fireEvent } from '@testing-library/react'
import { describe, it, expect, beforeEach } from 'vitest'
import { ModelProfileDropdown } from '../ModelProfileDropdown'
import { useModelProfileStore } from '@/stores/modelProfileStore'

// Reset store before each test to avoid state leakage
beforeEach(() => {
  useModelProfileStore.setState({ profile: 'balanced' })
})

describe('ModelProfileDropdown', () => {
  it('renders with default balanced profile selected', () => {
    render(<ModelProfileDropdown />)
    const select = screen.getByTestId('model-profile-select') as HTMLSelectElement
    expect(select.value).toBe('balanced')
  })

  it('renders all three profile options', () => {
    render(<ModelProfileDropdown />)
    const select = screen.getByTestId('model-profile-select')
    expect(select).toBeInTheDocument()

    expect(screen.getByRole('option', { name: /quality/i })).toBeInTheDocument()
    expect(screen.getByRole('option', { name: /balanced/i })).toBeInTheDocument()
    expect(screen.getByRole('option', { name: /budget/i })).toBeInTheDocument()
  })

  it('renders label for accessibility', () => {
    render(<ModelProfileDropdown />)
    expect(screen.getByLabelText(/select model profile/i)).toBeInTheDocument()
  })

  it('changing selection updates Zustand store', () => {
    render(<ModelProfileDropdown />)
    const select = screen.getByTestId('model-profile-select') as HTMLSelectElement

    fireEvent.change(select, { target: { value: 'quality' } })
    expect(useModelProfileStore.getState().profile).toBe('quality')

    fireEvent.change(select, { target: { value: 'budget' } })
    expect(useModelProfileStore.getState().profile).toBe('budget')
  })

  it('reflects external store changes', () => {
    render(<ModelProfileDropdown />)

    // Simulate external store update
    useModelProfileStore.setState({ profile: 'quality' })

    // Re-render to reflect the new state
    const { rerender } = render(<ModelProfileDropdown />)
    rerender(<ModelProfileDropdown />)
    const select = screen.getAllByTestId('model-profile-select')[1] as HTMLSelectElement
    expect(select.value).toBe('quality')
  })
})
