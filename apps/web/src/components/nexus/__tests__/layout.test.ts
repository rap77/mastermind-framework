import { describe, it, expect } from 'vitest'
import type { Node, Edge } from '@xyflow/react'
import { getLayoutedNodes } from '../NexusCanvas'

const BRAIN_NODE_W = 160
const BRAIN_NODE_H = 60
const COORDINATOR_W = 100
const COORDINATOR_H = 100

/** Build 24 fake nodes: 1 coordinator + 23 brains */
function buildTestNodes(): Node[] {
  const nodes: Node[] = []
  nodes.push({
    id: 'brain-08',
    type: 'brainNode',
    data: { label: 'Coordinator', niche: 'coordinator', onSelect: () => {} },
    position: { x: 0, y: 0 },
    width: COORDINATOR_W,
    height: COORDINATOR_H,
  })
  for (let i = 1; i <= 23; i++) {
    const id = `brain-${String(i).padStart(2, '0')}`
    nodes.push({
      id,
      type: 'brainNode',
      data: { label: `Brain ${i}`, niche: 'software', onSelect: () => {} },
      position: { x: 0, y: 0 },
      width: BRAIN_NODE_W,
      height: BRAIN_NODE_H,
    })
  }
  return nodes
}

/** Build star topology edges from coordinator to all brains */
function buildTestEdges(nodes: Node[]): Edge[] {
  return nodes
    .filter(n => n.id !== 'brain-08')
    .map(n => ({
      id: `edge-brain-08-${n.id}`,
      source: 'brain-08',
      target: n.id,
    }))
}

describe('getLayoutedNodes', () => {
  it('all nodes have non-NaN x and y positions after layout', () => {
    const nodes = buildTestNodes()
    const edges = buildTestEdges(nodes)
    const laid = getLayoutedNodes(nodes, edges)

    expect(laid).toHaveLength(24)
    for (const node of laid) {
      expect(node.position.x).not.toBeNaN()
      expect(node.position.y).not.toBeNaN()
      expect(Number.isFinite(node.position.x)).toBe(true)
      expect(Number.isFinite(node.position.y)).toBe(true)
    }
  })

  it('24 node positions are stable across multiple calls with same input', () => {
    const nodes = buildTestNodes()
    const edges = buildTestEdges(nodes)

    const first = getLayoutedNodes(nodes, edges)
    const second = getLayoutedNodes(nodes, edges)

    expect(first).toHaveLength(24)
    expect(second).toHaveLength(24)

    for (let i = 0; i < first.length; i++) {
      expect(first[i].position.x).toBe(second[i].position.x)
      expect(first[i].position.y).toBe(second[i].position.y)
    }
  })

  it('coordinator node is positioned at a different level from brain satellites', () => {
    const nodes = buildTestNodes()
    const edges = buildTestEdges(nodes)
    const laid = getLayoutedNodes(nodes, edges)

    const coordinator = laid.find(n => n.id === 'brain-08')
    const satellites = laid.filter(n => n.id !== 'brain-08')

    expect(coordinator).toBeDefined()
    expect(satellites.length).toBeGreaterThan(0)

    // Coordinator must be at a distinct Y level (TB layout: rank 0 vs rank 1)
    const coordY = coordinator!.position.y
    const satelliteYs = satellites.map(n => n.position.y)

    // At least one satellite must be at a different Y position than coordinator
    const differentLevel = satelliteYs.some(y => Math.abs(y - coordY) > 50)
    expect(differentLevel).toBe(true)
  })
})
