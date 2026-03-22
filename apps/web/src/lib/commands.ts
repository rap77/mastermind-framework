/**
 * Keyboard shortcut utilities for the War Room
 */

/**
 * Registers a Cmd+Enter (or Ctrl+Enter on Windows/Linux) keyboard shortcut
 *
 * @param onTrigger - Callback function to execute when shortcut is triggered
 * @returns Cleanup function to remove event listener
 *
 * @example
 * ```tsx
 * useEffect(() => {
 *   const cleanup = registerCommandShortcut(() => {
 *     setIsModalOpen(true)
 *   })
 *   return cleanup
 * }, [])
 * ```
 */
export function registerCommandShortcut(onTrigger: () => void): () => void {
  const handleKeyDown = (event: KeyboardEvent) => {
    // Check for Cmd+Enter (Mac) or Ctrl+Enter (Windows/Linux)
    const isCmdOrCtrl = event.metaKey || event.ctrlKey
    const isEnter = event.key === 'Enter'

    if (isCmdOrCtrl && isEnter) {
      event.preventDefault()
      onTrigger()
    }
  }

  document.addEventListener('keydown', handleKeyDown)

  // Return cleanup function
  return () => {
    document.removeEventListener('keydown', handleKeyDown)
  }
}
