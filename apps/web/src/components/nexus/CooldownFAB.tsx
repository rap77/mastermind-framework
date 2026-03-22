'use client'

import { useEffect, useRef } from 'react'
import { useRouter } from 'next/navigation'
import { cn } from '@/lib/utils'

interface CooldownFABProps {
  visible: boolean
  taskId: string | null
  onEscape?: () => void
}

/**
 * CooldownFAB — Floating Action Bar after task completion
 *
 * Renders at bottom-center when visible=true.
 * Keyboard shortcuts: [Enter] → Command Center, [V] → Strategy Vault,
 * [R] → Re-run (disabled, Day 2), [Esc] → clear Ghost Trace.
 * Auto-focuses [Enter] button when visible becomes true (keyboard-first UX).
 * Motion guard on entrance animation.
 */
export function CooldownFAB({ visible, taskId: _taskId, onEscape }: CooldownFABProps) {
  const router = useRouter()
  const enterButtonRef = useRef<HTMLButtonElement>(null)

  // Auto-focus [Enter] button when FAB becomes visible
  useEffect(() => {
    if (visible && enterButtonRef.current) {
      enterButtonRef.current.focus()
    }
  }, [visible])

  // Keyboard shortcuts
  useEffect(() => {
    if (!visible) return

    const handleKeyDown = (e: KeyboardEvent) => {
      // Prevent triggering inside input fields
      if (
        e.target instanceof HTMLInputElement ||
        e.target instanceof HTMLTextAreaElement
      ) return

      switch (e.key) {
        case 'Enter':
          e.preventDefault()
          router.push('/command-center')
          break
        case 'v':
        case 'V':
          e.preventDefault()
          // Strategy Vault — Phase 08 destination, not yet implemented
          // Router push will fail gracefully (Next.js shows 404)
          router.push('/strategy-vault')
          break
        case 'Escape':
          e.preventDefault()
          onEscape?.()
          break
        // [R] re-run is a Day 2 feature — no handler yet
      }
    }

    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [visible, router, onEscape])

  if (!visible) return null

  return (
    <div
      className={cn(
        'fixed bottom-6 left-1/2 -translate-x-1/2 z-50',
        'flex items-center gap-2 px-4 py-3 rounded-2xl',
        'bg-background/90 backdrop-blur-sm border shadow-lg',
        'transition-all duration-200 motion-reduce:transition-none',
      )}
      role="toolbar"
      aria-label="Task completed actions"
    >
      {/* [Enter] → Command Center */}
      <button
        ref={enterButtonRef}
        type="button"
        className="flex items-center gap-2 px-3 py-1.5 rounded-lg text-sm font-medium bg-primary text-primary-foreground hover:bg-primary/90 transition-colors"
        onClick={() => router.push('/command-center')}
        aria-label="Return to Command Center (Enter)"
      >
        <kbd className="text-xs opacity-70 font-mono bg-primary-foreground/10 px-1 rounded">
          Enter
        </kbd>
        Command Center
      </button>

      {/* [V] → Strategy Vault (disabled if route doesn't exist yet) */}
      <button
        type="button"
        className="flex items-center gap-2 px-3 py-1.5 rounded-lg text-sm font-medium text-muted-foreground hover:text-foreground hover:bg-muted transition-colors"
        onClick={() => router.push('/strategy-vault')}
        title="Strategy Vault (Phase 08)"
        aria-label="Open Strategy Vault (V)"
      >
        <kbd className="text-xs opacity-70 font-mono bg-muted px-1 rounded">V</kbd>
        Strategy Vault
      </button>

      {/* [R] → Re-run (disabled — Day 2 feature) */}
      <button
        type="button"
        className="flex items-center gap-2 px-3 py-1.5 rounded-lg text-sm font-medium text-muted-foreground/50 cursor-not-allowed"
        disabled
        aria-label="Re-run task (not yet available)"
        title="Re-run — coming soon"
      >
        <kbd className="text-xs opacity-50 font-mono bg-muted px-1 rounded">R</kbd>
        Re-run
      </button>

      {/* [Esc] → Clear Ghost Trace */}
      <button
        type="button"
        className="flex items-center gap-2 px-3 py-1.5 rounded-lg text-sm font-medium text-muted-foreground hover:text-foreground hover:bg-muted transition-colors"
        onClick={() => onEscape?.()}
        aria-label="Clear trace and return to Ghost Architecture (Escape)"
      >
        <kbd className="text-xs opacity-70 font-mono bg-muted px-1 rounded">Esc</kbd>
        Clear
      </button>
    </div>
  )
}
