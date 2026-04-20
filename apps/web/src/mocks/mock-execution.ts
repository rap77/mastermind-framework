/**
 * Mock Execution Data — Development/testing data for Simulation page
 *
 * Represents a typical execution with parallel branches:
 *
 *   node-1 (Product Strategy)
 *     ├── node-2 (UX Research)     ← parallel with node-3
 *     └── node-3 (UI Design)       ← parallel with node-2
 *         ├── node-4 (Frontend)     ← parallel with node-5
 *         └── node-5 (Backend)      ← parallel with node-4
 *             └── node-6 (QA/DevOps)
 *                 └── node-7 (Growth/Data)
 *
 * 5 execution waves:
 * Wave 0: Start
 * Wave 1: brain-1 (500ms)
 * Wave 2: brain-2 + brain-3 (parallel, ~1200ms)
 * Wave 3: brain-4 + brain-5 (parallel, ~1100ms)
 * Wave 4: brain-6 (800ms)
 * Wave 5: brain-7 (700ms)
 */

import type { Execution } from '@/stores/simulationStore'

export const mockExecution: Execution = {
  id: 'exec-mock-001',
  task_id: 'task-mock-001',
  brief: 'Mock execution with parallel branches for simulation testing',
  status: 'success',
  duration_ms: 4500,
  brain_count: 7,
  created_at: new Date().toISOString(),
  milestones: [
    {
      index: 0,
      timestamp: 0,
      label: 'Start',
      brain_count: 0,
    },
    {
      index: 1,
      timestamp: 500,
      label: 'Product Strategy → complete',
      brain_count: 1,
    },
    {
      index: 2,
      timestamp: 1000,
      label: 'UX Research + UI Design → parallel',
      brain_count: 3,
    },
    {
      index: 3,
      timestamp: 2200,
      label: 'Frontend + Backend → parallel',
      brain_count: 5,
    },
    {
      index: 4,
      timestamp: 3300,
      label: 'QA/DevOps → complete',
      brain_count: 6,
    },
    {
      index: 5,
      timestamp: 4100,
      label: 'Growth/Data → complete',
      brain_count: 7,
    },
  ],
  brain_outputs: {
    // Wave 1: Sequential start
    'brain-1': {
      brain_id: 'brain-1',
      status: 'complete',
      output: 'Product strategy analysis complete',
      duration_ms: 500,
      timestamp: 0,
    },
    // Wave 2: Parallel execution (both start at same time)
    'brain-2': {
      brain_id: 'brain-2',
      status: 'complete',
      output: 'UX research findings synthesized',
      duration_ms: 800,
      timestamp: 500,
    },
    'brain-3': {
      brain_id: 'brain-3',
      status: 'error',
      output: 'Failed to generate UI mockups: timeout error',
      duration_ms: 1200,
      timestamp: 500, // Same start as brain-2 — parallel!
    },
    // Wave 3: Parallel execution
    'brain-4': {
      brain_id: 'brain-4',
      status: 'complete',
      output: 'Frontend components generated',
      duration_ms: 600,
      timestamp: 1700, // After wave 2 completes
    },
    'brain-5': {
      brain_id: 'brain-5',
      status: 'complete',
      output: 'Backend API endpoints designed',
      duration_ms: 1100,
      timestamp: 1700, // Same start as brain-4 — parallel!
    },
    // Wave 4: Sequential
    'brain-6': {
      brain_id: 'brain-6',
      status: 'complete',
      output: 'QA test plan created',
      duration_ms: 800,
      timestamp: 2800,
    },
    // Wave 5: Sequential
    'brain-7': {
      brain_id: 'brain-7',
      status: 'complete',
      output: 'Growth strategy recommendations',
      duration_ms: 700,
      timestamp: 3600,
    },
  },
  graph_snapshot: {
    nodes: [
      {
        id: 'node-1',
        type: 'brain',
        position: { x: 50, y: 200 },
        data: {
          label: 'Product Strategy',
          brainId: 'brain-1',
          description: 'Analyzes product requirements',
        },
      },
      {
        id: 'node-2',
        type: 'brain',
        position: { x: 350, y: 50 },
        data: {
          label: 'UX Research',
          brainId: 'brain-2',
          description: 'Synthesizes user research',
        },
      },
      {
        id: 'node-3',
        type: 'brain',
        position: { x: 350, y: 350 },
        data: {
          label: 'UI Design',
          brainId: 'brain-3',
          description: 'Creates UI mockups',
        },
      },
      {
        id: 'node-4',
        type: 'brain',
        position: { x: 650, y: 50 },
        data: {
          label: 'Frontend',
          brainId: 'brain-4',
          description: 'Builds frontend components',
        },
      },
      {
        id: 'node-5',
        type: 'brain',
        position: { x: 650, y: 350 },
        data: {
          label: 'Backend',
          brainId: 'brain-5',
          description: 'Designs API endpoints',
        },
      },
      {
        id: 'node-6',
        type: 'brain',
        position: { x: 950, y: 200 },
        data: {
          label: 'QA/DevOps',
          brainId: 'brain-6',
          description: 'Creates test plans',
        },
      },
      {
        id: 'node-7',
        type: 'brain',
        position: { x: 1250, y: 200 },
        data: {
          label: 'Growth/Data',
          brainId: 'brain-7',
          description: 'Analyzes growth metrics',
        },
      },
    ],
    edges: [
      { id: 'e1-2', source: 'node-1', target: 'node-2' },
      { id: 'e1-3', source: 'node-1', target: 'node-3' },
      { id: 'e2-4', source: 'node-2', target: 'node-4' },
      { id: 'e3-5', source: 'node-3', target: 'node-5' },
      { id: 'e4-6', source: 'node-4', target: 'node-6' },
      { id: 'e5-6', source: 'node-5', target: 'node-6' },
      { id: 'e6-7', source: 'node-6', target: 'node-7' },
    ],
    viewport: { x: 0, y: 0, zoom: 0.8 },
  },
}
