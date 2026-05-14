#!/usr/bin/env node
/**
 * mm-flow-statusline.js — Statusline info for mm-flow task execution.
 *
 * C2.17: Shows active provider when a backend switch is active.
 * Example output: "│ v3.1 Task A1 [3/9] │ ⚡ openrouter"
 *
 * Reads:
 *   - .planning/.mm-flow/runtime-state.json — current task/phase info
 *   - .planning/ACTIVE-BACKEND.json — active backend (C2.16)
 *
 * Usage (from Claude Code hook or terminal):
 *   node .planning/.mm-flow/mm-flow-statusline.js
 *
 * Output: single line to stdout, empty string if no active task.
 */

'use strict'

const fs = require('fs')
const path = require('path')

// ---------------------------------------------------------------------------
// Paths
// ---------------------------------------------------------------------------

const REPO_ROOT = path.resolve(__dirname, '../..')
const RUNTIME_STATE_PATH = path.join(REPO_ROOT, '.planning/.mm-flow/runtime-state.json')
const ACTIVE_BACKEND_PATH = path.join(REPO_ROOT, '.planning/ACTIVE-BACKEND.json')
const TASK_PROGRESS_PATH = path.join(REPO_ROOT, '.planning/task-progress.json')

// ---------------------------------------------------------------------------
// Read files
// ---------------------------------------------------------------------------

function readJson(filePath) {
  try {
    return JSON.parse(fs.readFileSync(filePath, 'utf8'))
  } catch {
    return null
  }
}

// ---------------------------------------------------------------------------
// Build statusline segments
// ---------------------------------------------------------------------------

function getActiveProvider() {
  const data = readJson(ACTIVE_BACKEND_PATH)
  if (!data) return null
  const backend = data.active_backend
  // Only show if not the default 'claude' backend (non-default = switch happened)
  if (backend && backend !== 'claude') {
    return backend
  }
  return null
}

function getTaskInfo() {
  const progress = readJson(TASK_PROGRESS_PATH)
  if (!progress) return null

  const taskId = progress.task_id
  if (!taskId) return null

  // Count completed/total subtasks
  const subtasks = progress.subtasks || {}
  const total = Object.keys(subtasks).length
  const completed = Object.values(subtasks).filter((s) => s.status === 'completed').length

  return { taskId, completed, total }
}

function getRuntimeState() {
  const state = readJson(RUNTIME_STATE_PATH)
  if (!state) return null
  return state
}

// ---------------------------------------------------------------------------
// Format statusline
// ---------------------------------------------------------------------------

function buildStatusline() {
  const taskInfo = getTaskInfo()
  const runtimeState = getRuntimeState()
  const activeProvider = getActiveProvider()

  if (!taskInfo && !activeProvider) {
    return ''
  }

  const parts = []

  // Version + task info
  if (taskInfo) {
    const { taskId, completed, total } = taskInfo
    const version = runtimeState?.version || 'v3.1'
    parts.push(`${version} Task ${taskId} [${completed}/${total}]`)
  }

  // Active provider (shown when backend switch is active)
  if (activeProvider) {
    parts.push(`⚡ ${activeProvider}`)
  }

  if (parts.length === 0) return ''

  return '│ ' + parts.join(' │ ')
}

// ---------------------------------------------------------------------------
// Main
// ---------------------------------------------------------------------------

const statusline = buildStatusline()
if (statusline) {
  process.stdout.write(statusline + '\n')
}
process.exit(0)
