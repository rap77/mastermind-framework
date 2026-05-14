#!/usr/bin/env node
/**
 * mm-flow-context-monitor.js — Claude Code PostToolUse hook
 *
 * Monitors context token usage and triggers automatic backend switch when
 * approaching the critical threshold defined in .planning/.mm-flow/config.yml.
 *
 * C2.12: BACKEND_LIMITS read from config.yml at runtime (not hardcoded).
 * C2.13: At 95% threshold → writes .planning/BACKEND-SWITCH-REQUIRED.json
 * C2.16: Active backend read from .planning/ACTIVE-BACKEND.json (not hardcoded)
 *
 * Hook type: PostToolUse (runs after each tool call)
 * Input: JSON on stdin with { tool_name, tool_input, tool_response, session_id }
 *
 * Usage in .claude/settings.json hooks:
 *   {
 *     "type": "PostToolUse",
 *     "command": "node .planning/.mm-flow/mm-flow-context-monitor.js"
 *   }
 */

'use strict'

const fs = require('fs')
const path = require('path')

// ---------------------------------------------------------------------------
// Config paths (relative to repo root, resolved from this file's location)
// ---------------------------------------------------------------------------

const REPO_ROOT = path.resolve(__dirname, '../..')
const CONFIG_PATH = path.join(REPO_ROOT, '.planning/.mm-flow/config.yml')
const ACTIVE_BACKEND_PATH = path.join(REPO_ROOT, '.planning/ACTIVE-BACKEND.json')
const BACKEND_SWITCH_REQUIRED_PATH = path.join(REPO_ROOT, '.planning/BACKEND-SWITCH-REQUIRED.json')

// ---------------------------------------------------------------------------
// Minimal YAML parser for the backend_limits section (avoids dependency)
// Parses only the specific nested structure we need.
// ---------------------------------------------------------------------------

function parseBackendLimitsFromYaml(yamlText) {
  const defaults = {
    claude: { token_limit: 200000, critical_threshold: 0.95, priority: 1 },
    openrouter: { token_limit: 200000, critical_threshold: 0.95, priority: 2 },
    z_ai: { token_limit: 200000, critical_threshold: 0.95, priority: 3 },
  }

  if (!yamlText) return defaults

  // Find backend_limits section
  const sectionMatch = yamlText.match(/^backend_limits:\s*\n((?:[ \t]+[^\n]+\n?)*)/m)
  if (!sectionMatch) return defaults

  const sectionText = sectionMatch[1]
  const result = {}
  let currentBackend = null

  for (const line of sectionText.split('\n')) {
    const backendMatch = line.match(/^  ([a-z_]+):/)
    if (backendMatch) {
      currentBackend = backendMatch[1]
      result[currentBackend] = { ...defaults[currentBackend] }
      continue
    }
    if (currentBackend) {
      const tokenLimitMatch = line.match(/^\s+token_limit:\s*(\d+)/)
      if (tokenLimitMatch) {
        result[currentBackend].token_limit = parseInt(tokenLimitMatch[1], 10)
      }
      const thresholdMatch = line.match(/^\s+critical_threshold:\s*([\d.]+)/)
      if (thresholdMatch) {
        result[currentBackend].critical_threshold = parseFloat(thresholdMatch[1])
      }
      const priorityMatch = line.match(/^\s+priority:\s*(\d+)/)
      if (priorityMatch) {
        result[currentBackend].priority = parseInt(priorityMatch[1], 10)
      }
    }
  }

  return Object.keys(result).length > 0 ? result : defaults
}

// ---------------------------------------------------------------------------
// Load config at runtime (C2.12 — NOT hardcoded)
// ---------------------------------------------------------------------------

function loadBackendLimits() {
  try {
    const raw = fs.readFileSync(CONFIG_PATH, 'utf8')
    return parseBackendLimitsFromYaml(raw)
  } catch {
    // Graceful degradation if config file is missing
    return {
      claude: { token_limit: 200000, critical_threshold: 0.95, priority: 1 },
      openrouter: { token_limit: 200000, critical_threshold: 0.95, priority: 2 },
      z_ai: { token_limit: 200000, critical_threshold: 0.95, priority: 3 },
    }
  }
}

// ---------------------------------------------------------------------------
// Read active backend (C2.16 — from ACTIVE-BACKEND.json, not hardcoded)
// ---------------------------------------------------------------------------

function getActiveBackend() {
  try {
    const raw = fs.readFileSync(ACTIVE_BACKEND_PATH, 'utf8')
    const data = JSON.parse(raw)
    return data.active_backend || 'claude'
  } catch {
    return 'claude' // default to primary backend
  }
}

// ---------------------------------------------------------------------------
// Determine next backend in priority order (C2.13)
// ---------------------------------------------------------------------------

function getNextBackend(currentBackend, backendLimits) {
  const sorted = Object.entries(backendLimits)
    .sort(([, a], [, b]) => (a.priority || 99) - (b.priority || 99))
    .map(([name]) => name)

  const currentIdx = sorted.indexOf(currentBackend)
  if (currentIdx < 0 || currentIdx >= sorted.length - 1) {
    return null // no next backend available
  }
  return sorted[currentIdx + 1]
}

// ---------------------------------------------------------------------------
// Write BACKEND-SWITCH-REQUIRED.json (C2.13)
// ---------------------------------------------------------------------------

function writeBackendSwitchRequired(currentBackend, nextBackend, reason) {
  const signal = {
    current_backend: currentBackend,
    next_backend: nextBackend,
    reason: 'token_depletion',
    reason_detail: reason,
    timestamp: new Date().toISOString(),
  }
  const dir = path.dirname(BACKEND_SWITCH_REQUIRED_PATH)
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true })
  }
  fs.writeFileSync(BACKEND_SWITCH_REQUIRED_PATH, JSON.stringify(signal, null, 2) + '\n')
  process.stderr.write(
    `[mm-flow-context-monitor] BACKEND SWITCH REQUIRED: ${currentBackend} → ${nextBackend} (${reason})\n`
  )
}

// ---------------------------------------------------------------------------
// Main: process stdin hook payload
// ---------------------------------------------------------------------------

let input = ''
process.stdin.setEncoding('utf8')
process.stdin.on('data', (chunk) => {
  input += chunk
})

process.stdin.on('end', () => {
  try {
    const hook = JSON.parse(input)

    // Extract token usage from hook payload
    // Claude Code hook provides context_tokens_used in various locations
    const tokensUsed =
      hook?.tool_response?.context_tokens_used ||
      hook?.session?.context_tokens_used ||
      hook?.context_tokens_used

    if (!tokensUsed || typeof tokensUsed !== 'number') {
      process.exit(0) // No token info — skip silently
    }

    // C2.12: load limits from config at runtime
    const backendLimits = loadBackendLimits()

    // C2.16: read active backend from ACTIVE-BACKEND.json
    const activeBackend = getActiveBackend()
    const limits = backendLimits[activeBackend]

    if (!limits) {
      process.exit(0)
    }

    const usageFraction = tokensUsed / limits.token_limit
    const threshold = limits.critical_threshold || 0.95

    // C2.13: at critical threshold, write switch signal
    if (usageFraction >= threshold) {
      // Idempotent: only write once
      if (!fs.existsSync(BACKEND_SWITCH_REQUIRED_PATH)) {
        const nextBackend = getNextBackend(activeBackend, backendLimits)
        if (nextBackend) {
          const usagePct = Math.round(usageFraction * 100)
          writeBackendSwitchRequired(
            activeBackend,
            nextBackend,
            `token_depletion (${usagePct}% of ${limits.token_limit})`
          )
        }
      }
    }
  } catch {
    // Graceful degradation — never block Claude on monitor errors
  }

  process.exit(0)
})
