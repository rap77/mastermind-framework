"use server"

import { revalidatePath } from 'next/cache'
import { cookies } from 'next/headers'

const DEFAULT_API_URL = 'http://localhost:8001'

type JsonObject = Record<string, unknown>

export interface ActionResult {
  success: boolean
  error?: string
}

interface CreateCheckpointInput {
  projectId: string
  taskId: string
  runId?: string | null
  nextStepSummary: string
  contextSummary?: JsonObject
  resumeState?: JsonObject
}

interface CreateDecisionInput {
  projectId: string
  taskId?: string | null
  title: string
  status: string
  rationaleMarkdown: string
  metadata?: JsonObject
}

async function getAuthHeaders(): Promise<HeadersInit> {
  const cookieStore = await cookies()
  const token = cookieStore.get('access_token')?.value

  if (!token) {
    throw new Error('Unauthorized')
  }

  return {
    'Content-Type': 'application/json',
    Authorization: `Bearer ${token}`,
  }
}

export async function createProjectCheckpoint(
  input: CreateCheckpointInput
): Promise<ActionResult> {
  if (!input.projectId || !input.taskId) {
    return { success: false, error: 'Project and task are required' }
  }

  if (!input.nextStepSummary.trim()) {
    return { success: false, error: 'Next step summary is required' }
  }

  try {
    const headers = await getAuthHeaders()
    const apiUrl = process.env.AGENT_RUNTIME_URL || DEFAULT_API_URL
    const response = await fetch(
      `${apiUrl}/api/projects/${input.projectId}/tasks/${input.taskId}/checkpoints`,
      {
        method: 'POST',
        headers,
        body: JSON.stringify({
          run_id: input.runId ?? null,
          context_summary: input.contextSummary ?? {},
          resume_state: input.resumeState ?? {},
          next_step_summary: input.nextStepSummary.trim(),
        }),
      }
    )

    if (!response.ok) {
      const errorData = (await response.json().catch(() => ({}))) as { detail?: string }
      return {
        success: false,
        error: errorData.detail || 'Failed to create checkpoint',
      }
    }

    revalidatePath('/project-state')
    return { success: true }
  } catch (error) {
    return {
      success: false,
      error: error instanceof Error ? error.message : 'Failed to create checkpoint',
    }
  }
}

interface UpdateTaskStatusInput {
  projectId: string
  taskId: string
  status: string
  reason?: string | null
}

export async function updateProjectTaskStatus(
  input: UpdateTaskStatusInput
): Promise<ActionResult> {
  if (!input.projectId || !input.taskId) {
    return { success: false, error: 'Project and task are required' }
  }

  if (!input.status.trim()) {
    return { success: false, error: 'Status is required' }
  }

  try {
    const headers = await getAuthHeaders()
    const apiUrl = process.env.AGENT_RUNTIME_URL || DEFAULT_API_URL
    const response = await fetch(
      `${apiUrl}/api/projects/${input.projectId}/tasks/${input.taskId}/status`,
      {
        method: 'PATCH',
        headers,
        body: JSON.stringify({
          status: input.status.trim(),
          reason: input.reason ?? null,
        }),
      }
    )

    if (!response.ok) {
      const errorData = (await response.json().catch(() => ({}))) as { detail?: string }
      return {
        success: false,
        error: errorData.detail || 'Failed to update task status',
      }
    }

    revalidatePath('/project-state')
    return { success: true }
  } catch (error) {
    return {
      success: false,
      error: error instanceof Error ? error.message : 'Failed to update task status',
    }
  }
}

export async function createProjectDecision(
  input: CreateDecisionInput
): Promise<ActionResult> {
  if (!input.projectId) {
    return { success: false, error: 'Project is required' }
  }

  if (!input.title.trim()) {
    return { success: false, error: 'Decision title is required' }
  }

  if (!input.rationaleMarkdown.trim()) {
    return { success: false, error: 'Decision rationale is required' }
  }

  try {
    const headers = await getAuthHeaders()
    const apiUrl = process.env.AGENT_RUNTIME_URL || DEFAULT_API_URL
    const response = await fetch(`${apiUrl}/api/projects/${input.projectId}/decisions`, {
      method: 'POST',
      headers,
      body: JSON.stringify({
        task_id: input.taskId ?? null,
        title: input.title.trim(),
        status: input.status,
        rationale_markdown: input.rationaleMarkdown.trim(),
        metadata: input.metadata ?? {},
      }),
    })

    if (!response.ok) {
      const errorData = (await response.json().catch(() => ({}))) as { detail?: string }
      return {
        success: false,
        error: errorData.detail || 'Failed to record decision',
      }
    }

    revalidatePath('/project-state')
    return { success: true }
  } catch (error) {
    return {
      success: false,
      error: error instanceof Error ? error.message : 'Failed to record decision',
    }
  }
}
