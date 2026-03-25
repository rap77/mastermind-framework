/**
 * Command Center Wrapper Component
 *
 * **Purpose:** Client component wrapper for Command Center interactivity
 * **Context:** Phase 06-03 - Task 4
 *
 * **Features:**
 * - Cmd+Enter keyboard shortcut to open brief modal
 * - Brief submission creates task via Server Action
 * - WebSocket connection established after task creation
 * - Error handling with user feedback
 */

"use client"

import { useState, useEffect, useCallback } from "react"
import { useRouter } from "next/navigation"
import { BriefInputModal } from "./BriefInputModal"
import { createTask } from "@/app/actions/tasks"
import { registerCommandShortcut } from "@/lib/commands"
import { useWSStore } from "@/stores/wsStore"
import { useOrchestratorStore } from "@/stores/orchestratorStore"

/**
 * Command Center Wrapper Component
 *
 * Wraps the Command Center page with client-side interactivity:
 * - Registers Cmd+Enter shortcut
 * - Manages modal open/close state
 * - Handles brief submission
 * - Connects WebSocket after task creation
 *
 * @param children - Command Center page content (Server Component)
 */
export function CommandCenterWrapper({ children }: { children: React.ReactNode }) {
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const wsStore = useWSStore()
  const router = useRouter()
  const startTask = useOrchestratorStore((s) => s.startTask)

  /**
   * Register Cmd+Enter keyboard shortcut
   *
   * Opens modal when Cmd/Ctrl+Enter is pressed
   * Shortcut is active when modal is closed
   */
  useEffect(() => {
    const cleanup = registerCommandShortcut(() => {
      setIsModalOpen(true)
      setError(null) // Clear previous errors
    })

    return cleanup
  }, [])

  /**
   * Handle brief submission
   *
   * Flow:
   * 1. Validate and sanitize brief (BriefInputModal)
   * 2. Create task via Server Action (createTask)
   * 3. Get WS token from /api/auth/token
   * 4. Connect WebSocket
   * 5. Close modal on success
   */
  const handleBriefSubmit = useCallback(
    async (brief: string) => {
      setIsSubmitting(true)
      setError(null)

      try {
        // Step 1: Create task via Server Action
        const result = await createTask(brief)

        if (!result.success) {
          setError(result.error || "Failed to create task")
          return
        }

        // Validate taskId exists before connecting WebSocket
        if (!result.taskId) {
          setError("Task created but no ID returned - cannot connect WebSocket")
          return
        }

        // Step 2: Get WS token
        const tokenResponse = await fetch("/api/auth/token")
        if (!tokenResponse.ok) {
          setError("Task created! Could not connect to real-time updates. Your brief is being processed — check the Strategy Vault for results.")
          return
        }

        const { access_token } = await tokenResponse.json()

        // Step 3: Connect WebSocket with taskId AND token
        wsStore.connect(result.taskId, access_token)

        // Step 4: Activate orchestrator task → triggers Focus Mode
        startTask(result.taskId, brief)

        // Step 5: Navigate to The Nexus to watch brains illuminate in real-time
        router.push('/nexus')
      } catch (err) {
        console.error("Failed to submit brief:", err)
        setError("Network error: Failed to create task")
      } finally {
        setIsSubmitting(false)
      }
    },
    [wsStore, startTask, router]
  )

  /**
   * Handle modal close
   */
  const handleCloseModal = useCallback(() => {
    setIsModalOpen(false)
    setError(null)
  }, [])

  return (
    <>
      {children}

      <BriefInputModal
        open={isModalOpen}
        onClose={handleCloseModal}
        onSubmit={handleBriefSubmit}
      />

      {error && (
        <div className="fixed bottom-4 right-4 z-50 rounded-lg bg-destructive px-4 py-2 text-destructive-foreground shadow-lg">
          {error}
        </div>
      )}
    </>
  )
}
