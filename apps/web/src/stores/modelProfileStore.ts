/**
 * modelProfileStore — Zustand store for model profile selection.
 *
 * C2.06 spec:
 *   - Tracks the active model profile (quality | balanced | budget)
 *   - Default: "balanced"
 *   - setProfile: updates the active profile
 *   - profile is included in task dispatch requests (C2.07)
 *
 * No persistence — resets to "balanced" on page refresh.
 */

import { create } from 'zustand'

// ------------------------------------------------------------------ types

export type ModelProfile = 'quality' | 'balanced' | 'budget'

export interface ModelProfileOption {
  value: ModelProfile
  label: string
  description: string
}

export const MODEL_PROFILE_OPTIONS: ModelProfileOption[] = [
  {
    value: 'quality',
    label: 'Quality',
    description: 'Best models — critical decisions, Brain #7 barrier',
  },
  {
    value: 'balanced',
    label: 'Balanced',
    description: 'Standard models — domain brains',
  },
  {
    value: 'budget',
    label: 'Budget',
    description: 'Efficient models — context recovery, status checks',
  },
]

// ------------------------------------------------------------------ store

interface ModelProfileState {
  /** Currently selected model profile. */
  profile: ModelProfile

  /** Update the active model profile. */
  setProfile: (profile: ModelProfile) => void
}

export const useModelProfileStore = create<ModelProfileState>()((set) => ({
  profile: 'balanced',

  setProfile: (profile: ModelProfile) => set({ profile }),
}))
