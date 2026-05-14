/**
 * Tests for modelProfileStore — C2.10
 *
 * Verifies:
 * - Changing dropdown selection updates Zustand store
 * - Store profile is correctly read and updated
 */

import { describe, it, expect, beforeEach } from 'vitest'
import { useModelProfileStore, MODEL_PROFILE_OPTIONS } from '../modelProfileStore'

beforeEach(() => {
  useModelProfileStore.setState({ profile: 'balanced' })
})

describe('modelProfileStore — C2.10', () => {
  it('defaults to balanced profile', () => {
    expect(useModelProfileStore.getState().profile).toBe('balanced')
  })

  it('setProfile updates the store to quality', () => {
    useModelProfileStore.getState().setProfile('quality')
    expect(useModelProfileStore.getState().profile).toBe('quality')
  })

  it('setProfile updates the store to budget', () => {
    useModelProfileStore.getState().setProfile('budget')
    expect(useModelProfileStore.getState().profile).toBe('budget')
  })

  it('setProfile cycling through all profiles', () => {
    for (const opt of MODEL_PROFILE_OPTIONS) {
      useModelProfileStore.getState().setProfile(opt.value)
      expect(useModelProfileStore.getState().profile).toBe(opt.value)
    }
  })

  it('MODEL_PROFILE_OPTIONS has all three profiles', () => {
    const values = MODEL_PROFILE_OPTIONS.map((o) => o.value)
    expect(values).toContain('quality')
    expect(values).toContain('balanced')
    expect(values).toContain('budget')
    expect(values).toHaveLength(3)
  })
})
