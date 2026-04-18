/**
 * Mock Execution Data — Development/testing data for Simulation page
 *
 * Represents a typical execution with:
 * - 7 brain outputs (mix of success, error, slow)
 * - 5 milestone snapshots
 * - Graph snapshot with nodes and edges
 * - Total duration: 3.5 seconds
 */

import type { Execution } from '@/stores/simulationStore'

export const mockExecution: Execution = {
  id: 'exec-mock-001',
  task_id: 'task-mock-001',
  brief: 'Mock execution for simulation page testing',
  status: 'success',
  duration_ms: 3500,
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
      label: 'Brain #1 Complete',
      brain_count: 1,
    },
    {
      index: 2,
      timestamp: 1500,
      label: 'Brain #3 Complete',
      brain_count: 3,
    },
    {
      index: 3,
      timestamp: 2500,
      label: 'Brain #5 Complete',
      brain_count: 5,
    },
    {
      index: 4,
      timestamp: 3500,
      label: 'All Brains Complete',
      brain_count: 7,
    },
  ],
  brain_outputs: {
    'brain-1': {
      brain_id: 'brain-1',
      status: 'complete',
      output: 'Product strategy analysis complete',
      duration_ms: 500,
      timestamp: 0,
    },
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
      timestamp: 1300,
    },
    'brain-4': {
      brain_id: 'brain-4',
      status: 'complete',
      output: 'Frontend components generated',
      duration_ms: 600,
      timestamp: 1500,
    },
    'brain-5': {
      brain_id: 'brain-5',
      status: 'complete',
      output: 'Backend API endpoints designed',
      duration_ms: 1500, // Slow node
      timestamp: 2000,
    },
    'brain-6': {
      brain_id: 'brain-6',
      status: 'complete',
      output: 'QA test plan created',
      duration_ms: 400,
      timestamp: 2800,
    },
    'brain-7': {
      brain_id: 'brain-7',
      status: 'complete',
      output: 'Growth strategy recommendations',
      duration_ms: 700,
      timestamp: 3200,
    },
  },
  graph_snapshot: {
    nodes: [
      {
        id: 'node-1',
        type: 'brain',
        position: { x: 100, y: 100 },
        data: {
          label: 'Product Strategy',
          brainId: 'brain-1',
          description: 'Analyzes product requirements',
        },
      },
      {
        id: 'node-2',
        type: 'brain',
        position: { x: 100, y: 250 },
        data: {
          label: 'UX Research',
          brainId: 'brain-2',
          description: 'Synthesizes user research',
        },
      },
      {
        id: 'node-3',
        type: 'brain',
        position: { x: 100, y: 400 },
        data: {
          label: 'UI Design',
          brainId: 'brain-3',
          description: 'Creates UI mockups',
        },
      },
      {
        id: 'node-4',
        type: 'brain',
        position: { x: 400, y: 100 },
        data: {
          label: 'Frontend',
          brainId: 'brain-4',
          description: 'Builds frontend components',
        },
      },
      {
        id: 'node-5',
        type: 'brain',
        position: { x: 400, y: 250 },
        data: {
          label: 'Backend',
          brainId: 'brain-5',
          description: 'Designs API endpoints',
        },
      },
      {
        id: 'node-6',
        type: 'brain',
        position: { x: 400, y: 400 },
        data: {
          label: 'QA/DevOps',
          brainId: 'brain-6',
          description: 'Creates test plans',
        },
      },
      {
        id: 'node-7',
        type: 'brain',
        position: { x: 700, y: 250 },
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
      { id: 'e3-4', source: 'node-3', target: 'node-4' },
      { id: 'e4-5', source: 'node-4', target: 'node-5' },
      { id: 'e5-6', source: 'node-5', target: 'node-6' },
      { id: 'e6-7', source: 'node-6', target: 'node-7' },
    ],
    viewport: { x: 0, y: 0, zoom: 1 },
  },
}
