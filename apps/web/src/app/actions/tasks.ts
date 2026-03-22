/**
 * Server Actions for Task Management
 *
 * **Purpose:** Server Actions that can be imported by client components
 * **Context:** Phase 06-03
 *
 * NOTE: This file is outside app/api/ to avoid Next.js route handler conflicts.
 */

"use server"

import { cookies } from "next/headers"

/** Strip HTML tags server-side (DOMPurify is browser-only). Backend does html.escape() for actual XSS prevention. */
function stripHtml(input: string): string {
  return input.replace(/<[^>]*>/g, "")
}

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

  // XSS Prevention: Strip HTML tags server-side (defense in depth, backend does html.escape())
  const sanitizedBrief = stripHtml(brief)

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
