/**
 * Server Action: Task Creation
 *
 * **Purpose:** Create task via POST to FastAPI with XSS prevention
 * **Context:** Phase 06-03 - Task 3
 *
 * **Security:**
 * - JWT token from httpOnly cookie (not exposed to client)
 * - DOMPurify sanitization (defense in depth)
 * - Validation: brief min length 10 chars
 * - OWASP A03 (XSS) mitigated
 */

"use server"

import { cookies } from "next/headers"
import DOMPurify from "dompurify"

// FastAPI base URL (from env or default)
const FASTAPI_URL = process.env.FASTAPI_URL || "http://localhost:8000"

/**
 * Server Action response for task creation
 */
export interface CreateTaskResult {
  success: boolean
  taskId?: string
  error?: string
}

/**
 * Create task Server Action
 *
 * Validates brief, sanitizes with DOMPurify, calls FastAPI POST /api/tasks
 *
 * @param brief - User's task brief (will be sanitized)
 * @returns Task creation result with success status and taskId or error
 *
 * @example
 * ```tsx
 * const result = await createTask("Build a feature")
 * if (result.success) {
 *   console.log("Task created:", result.taskId)
 * }
 * ```
 */
export async function createTask(brief: string): Promise<CreateTaskResult> {
  // Validation: brief is required
  if (!brief || brief.trim().length === 0) {
    return { success: false, error: "Brief is required" }
  }

  // Validation: brief min length 10 chars
  if (brief.trim().length < 10) {
    return {
      success: false,
      error: "Brief must be at least 10 characters long",
    }
  }

  // XSS Prevention: Sanitize with DOMPurify (defense in depth)
  // ALLOWED_TAGS: [] = plain text only (no HTML)
  const sanitizedBrief = DOMPurify.sanitize(brief, {
    ALLOWED_TAGS: [],
    ALLOWED_ATTR: [],
    KEEP_CONTENT: true,
  })

  // Get JWT token from httpOnly cookie
  const cookieStore = await cookies()
  const token = cookieStore.get("access_token")?.value

  if (!token) {
    return { success: false, error: "Unauthorized" }
  }

  try {
    // Call FastAPI POST /api/tasks endpoint
    const response = await fetch(`${FASTAPI_URL}/api/tasks`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({ brief: sanitizedBrief }),
    })

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))
      return {
        success: false,
        error: errorData.detail || "Failed to create task",
      }
    }

    const data = await response.json()

    return {
      success: true,
      taskId: data.task_id,
    }
  } catch (error) {
    console.error("Failed to create task:", error)
    return {
      success: false,
      error: "Network error: Failed to create task",
    }
  }
}
