/**
 * FilterBar Component Tests
 *
 * **Purpose:** Verify filter control bar behavior — level toggles, auto-follow, isolation
 * **Context:** Phase 08-03 — Task 4
 */

import { render, screen, fireEvent } from '@testing-library/react'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { FilterBar } from '../FilterBar'
import { useLogFilterStore } from '@/stores/logFilterStore'

// ─── Reset store before each test ─────────────────────────────────────────────

beforeEach(() => {
  useLogFilterStore.getState().reset()
})

// ─── Level toggle tests ────────────────────────────────────────────────────────

describe('FilterBar level toggles', () => {
  it('renders all three level buttons', () => {
    render(<FilterBar />)
    expect(screen.getByText('INFO')).toBeInTheDocument()
    expect(screen.getByText('WARN')).toBeInTheDocument()
    expect(screen.getByText('ERROR')).toBeInTheDocument()
  })

  it('shows active state for all levels initially', () => {
    render(<FilterBar />)
    const infoBtn = screen.getByLabelText('Toggle info logs')
    expect(infoBtn).toHaveAttribute('aria-pressed', 'true')
    expect(infoBtn).toHaveClass('bg-blue-600')
  })

  it('toggles level off on click', () => {
    render(<FilterBar />)
    fireEvent.click(screen.getByLabelText('Toggle warn logs'))
    const warnBtn = screen.getByLabelText('Toggle warn logs')
    expect(warnBtn).toHaveAttribute('aria-pressed', 'false')
    expect(warnBtn).toHaveClass('bg-slate-700')
  })

  it('updates store on level toggle', () => {
    render(<FilterBar />)
    fireEvent.click(screen.getByLabelText('Toggle error logs'))
    const { filterLevels } = useLogFilterStore.getState()
    expect(filterLevels.has('error')).toBe(false)
  })

  it('calls onFilterChange on level toggle', () => {
    const onFilterChange = vi.fn()
    render(<FilterBar onFilterChange={onFilterChange} />)
    fireEvent.click(screen.getByLabelText('Toggle info logs'))
    expect(onFilterChange).toHaveBeenCalledTimes(1)
  })
})

// ─── Auto-follow tests ─────────────────────────────────────────────────────────

describe('FilterBar auto-follow', () => {
  it('renders auto-follow checkbox', () => {
    render(<FilterBar />)
    expect(screen.getByLabelText('Auto-follow newest log')).toBeInTheDocument()
  })

  it('auto-follow is checked by default', () => {
    render(<FilterBar />)
    const checkbox = screen.getByLabelText('Auto-follow newest log') as HTMLInputElement
    expect(checkbox.checked).toBe(true)
  })

  it('unchecks auto-follow on change', () => {
    render(<FilterBar />)
    const checkbox = screen.getByLabelText('Auto-follow newest log') as HTMLInputElement
    // fireEvent.click toggles checked and fires change event in jsdom
    fireEvent.click(checkbox)
    expect(useLogFilterStore.getState().autoFollow).toBe(false)
  })

  it('re-checks auto-follow', () => {
    useLogFilterStore.getState().setAutoFollow(false)
    render(<FilterBar />)
    const checkbox = screen.getByLabelText('Auto-follow newest log') as HTMLInputElement
    // checkbox starts unchecked, click toggles it to checked
    fireEvent.click(checkbox)
    expect(useLogFilterStore.getState().autoFollow).toBe(true)
  })
})

// ─── Isolation display tests ───────────────────────────────────────────────────

describe('FilterBar isolation display', () => {
  it('does not show isolation display by default', () => {
    render(<FilterBar />)
    expect(screen.queryByText(/Viewing:/)).not.toBeInTheDocument()
  })

  it('shows isolation display when brain is isolated', () => {
    useLogFilterStore.getState().setIsolatedBrain('marketing-01')
    render(<FilterBar />)
    expect(screen.getByText('Viewing: marketing-01')).toBeInTheDocument()
  })

  it('clears isolation on X button click', () => {
    useLogFilterStore.getState().setIsolatedBrain('marketing-01')
    render(<FilterBar />)
    fireEvent.click(screen.getByLabelText('Clear brain isolation'))
    expect(useLogFilterStore.getState().isolatedBrainId).toBeNull()
  })

  it('calls onFilterChange on isolation clear', () => {
    useLogFilterStore.getState().setIsolatedBrain('product-01')
    const onFilterChange = vi.fn()
    render(<FilterBar onFilterChange={onFilterChange} />)
    fireEvent.click(screen.getByLabelText('Clear brain isolation'))
    expect(onFilterChange).toHaveBeenCalledTimes(1)
  })
})
