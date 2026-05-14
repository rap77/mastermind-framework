'use client'

/**
 * ModelProfileDropdown — Model profile selector for the Command Center.
 *
 * C2.06 spec:
 *   - Renders a dropdown with three options: quality, balanced, budget
 *   - Selected profile is stored in Zustand modelProfileStore
 *   - Profile is read by CommandCenterWrapper to include in dispatch requests (C2.07)
 *
 * Design:
 *   - Uses a native <select> wrapped in a styled container for accessibility
 *   - Shows the profile label and description in the option list
 *   - Compact display in the Command Center header area
 */

import {
  MODEL_PROFILE_OPTIONS,
  type ModelProfile,
  useModelProfileStore,
} from '@/stores/modelProfileStore'

interface ModelProfileDropdownProps {
  /** CSS class applied to the container. */
  className?: string
}

export function ModelProfileDropdown({ className = '' }: ModelProfileDropdownProps) {
  const profile = useModelProfileStore((s) => s.profile)
  const setProfile = useModelProfileStore((s) => s.setProfile)

  return (
    <div
      className={`flex items-center gap-2 ${className}`}
      data-testid="model-profile-dropdown-container"
    >
      <label
        htmlFor="model-profile-select"
        className="text-xs text-muted-foreground font-medium whitespace-nowrap"
      >
        Model
      </label>
      <select
        id="model-profile-select"
        value={profile}
        onChange={(e) => setProfile(e.target.value as ModelProfile)}
        className="h-8 rounded-md border border-input bg-background px-2 text-xs font-medium ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 cursor-pointer"
        aria-label="Select model profile"
        data-testid="model-profile-select"
      >
        {MODEL_PROFILE_OPTIONS.map((opt) => (
          <option key={opt.value} value={opt.value} title={opt.description}>
            {opt.label}
          </option>
        ))}
      </select>
    </div>
  )
}
