/**
 * BriefInputModal Component
 *
 * **Purpose:** Full-screen modal for submitting briefs to the War Room
 * **Context:** Phase 06-03 - Task 2
 *
 * **Security:** XSS prevention via DOMPurify sanitization
 * - Client-side sanitization before onSubmit
 * - ALLOWED_TAGS: [] = plain text only (no HTML)
 * - Defense in depth: Server will also sanitize
 */

"use client"

import { useState, useEffect, useCallback } from "react"
import { Dialog, DialogContent, DialogOverlay } from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import DOMPurify from "dompurify"

export interface BriefInputModalProps {
  open: boolean
  onClose: () => void
  onSubmit: (brief: string) => void
}

/**
 * Full-screen brief input modal with XSS prevention
 *
 * @example
 * ```tsx
 * <BriefInputModal
 *   open={isModalOpen}
 *   onClose={() => setIsModalOpen(false)}
 *   onSubmit={(brief) => createTask(brief)}
 * />
 * ```
 */
export function BriefInputModal({ open, onClose, onSubmit }: BriefInputModalProps) {
  const [brief, setBrief] = useState("")
  const [isSubmitting, setIsSubmitting] = useState(false)

  // Reset form when modal opens/closes
  useEffect(() => {
    if (!open) {
      setBrief("")
      setIsSubmitting(false)
    }
  }, [open])

  // Handle keyboard shortcuts within modal
  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent) => {
      // Cmd+Enter or Ctrl+Enter to submit (if not empty and not submitting)
      if ((e.metaKey || e.ctrlKey) && e.key === "Enter") {
        e.preventDefault()
        if (brief.trim().length > 0 && !isSubmitting) {
          handleSubmit()
        }
      }
    },
    [brief, isSubmitting]
  )

  /**
   * Sanitize brief with DOMPurify (XSS prevention)
   * - ALLOWED_TAGS: [] = plain text only
   * - Removes all HTML tags and event handlers
   */
  const sanitizeBrief = (input: string): string => {
    return DOMPurify.sanitize(input, {
      ALLOWED_TAGS: [], // Plain text only (no HTML)
      ALLOWED_ATTR: [], // No attributes allowed
      KEEP_CONTENT: true, // Keep text content
    })
  }

  const handleSubmit = async () => {
    if (brief.trim().length === 0 || isSubmitting) {
      return
    }

    setIsSubmitting(true)

    try {
      // Sanitize brief before submitting (defense in depth)
      const sanitizedBrief = sanitizeBrief(brief)
      await onSubmit(sanitizedBrief)

      // Close modal after successful submission
      onClose()
    } catch (error) {
      console.error("Failed to submit brief:", error)
      // Error handling would be displayed via toast/alert in real implementation
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleBackdropClick = (e: React.MouseEvent) => {
    // Close modal when clicking outside (on backdrop)
    if (e.target === e.currentTarget) {
      onClose()
    }
  }

  return (
    <Dialog open={open} onOpenChange={(open) => !open && onClose()}>
      <DialogOverlay onClick={handleBackdropClick} />
      <DialogContent
        className="fixed top-1/2 left-1/2 z-50 w-full max-w-3xl -translate-x-1/2 -translate-y-1/2 rounded-xl bg-background p-6 shadow-lg"
        showCloseButton={false}
        onKeyDown={handleKeyDown}
      >
        <div className="flex flex-col gap-4">
          {/* Header */}
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-semibold">New Brief</h2>
            <p className="text-sm text-muted-foreground">
              Press Cmd+Enter to submit
            </p>
          </div>

          {/* Textarea */}
          <textarea
            value={brief}
            onChange={(e) => setBrief(e.target.value)}
            placeholder="Describe your task..."
            className="min-h-[200px] w-full resize-none rounded-md border border-input bg-background p-3 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
            disabled={isSubmitting}
            autoFocus
          />

          {/* Footer */}
          <div className="flex justify-end gap-2">
            <Button
              type="button"
              variant="outline"
              onClick={onClose}
              disabled={isSubmitting}
            >
              Cancel
            </Button>
            <Button
              type="button"
              onClick={handleSubmit}
              disabled={brief.trim().length === 0 || isSubmitting}
            >
              {isSubmitting ? "Submitting..." : "Submit"}
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  )
}
