'use client'

import { useMemo } from 'react'
import { useRouter } from 'next/navigation'
import dagre from '@dagrejs/dagre'
import {
  Background,
  Controls,
  MiniMap,
  ReactFlow,
  type Edge,
  type Node,
} from '@xyflow/react'
import '@xyflow/react/dist/style.css'

import type { ProjectStateTask, TaskDependency } from '@/lib/project-state-api'

const NODE_WIDTH = 220
const NODE_HEIGHT = 72

const dagreGraph = new dagre.graphlib.Graph()
dagreGraph.setDefaultEdgeLabel(() => ({}))

function layoutGraph(nodes: Node[], edges: Edge[]): Node[] {
  dagreGraph.setGraph({
    rankdir: 'TB',
    nodesep: 48,
    ranksep: 72,
  })

  for (const nodeId of dagreGraph.nodes()) {
    dagreGraph.removeNode(nodeId)
  }
  for (const edgeRef of dagreGraph.edges()) {
    dagreGraph.removeEdge(edgeRef.v, edgeRef.w)
  }

  for (const node of nodes) {
    dagreGraph.setNode(node.id, { width: NODE_WIDTH, height: NODE_HEIGHT })
  }

  for (const edge of edges) {
    dagreGraph.setEdge(edge.source, edge.target)
  }

  dagre.layout(dagreGraph)

  return nodes.map((node) => {
    const { x, y } = dagreGraph.node(node.id)
    return {
      ...node,
      position: {
        x: x - NODE_WIDTH / 2,
        y: y - NODE_HEIGHT / 2,
      },
    }
  })
}

function nodeBackground(status: string, isSelected: boolean): string {
  if (isSelected) return 'rgba(99, 102, 241, 0.18)'
  switch (status) {
    case 'in_progress':
    case 'running':
    case 'active':
      return 'rgba(34, 197, 94, 0.12)'
    case 'blocked':
      return 'rgba(245, 158, 11, 0.12)'
    case 'failed':
    case 'error':
      return 'rgba(239, 68, 68, 0.12)'
    default:
      return 'rgba(148, 163, 184, 0.10)'
  }
}

function nodeBorder(status: string, isSelected: boolean): string {
  if (isSelected) return 'rgba(99, 102, 241, 0.8)'
  switch (status) {
    case 'in_progress':
    case 'running':
    case 'active':
      return 'rgba(34, 197, 94, 0.55)'
    case 'blocked':
      return 'rgba(245, 158, 11, 0.55)'
    case 'failed':
    case 'error':
      return 'rgba(239, 68, 68, 0.55)'
    default:
      return 'rgba(148, 163, 184, 0.35)'
  }
}

interface TaskGraphPanelProps {
  projectId: string
  selectedTaskId: string | null
  tasks: ProjectStateTask[]
  dependencies: TaskDependency[]
}

export function TaskGraphPanel({
  projectId,
  selectedTaskId,
  tasks,
  dependencies,
}: TaskGraphPanelProps) {
  const router = useRouter()

  const edges = useMemo<Edge[]>(() => {
    return dependencies.map((dependency) => ({
      id: dependency.dependency_id,
      source: dependency.depends_on_task_id,
      target: dependency.task_id,
      animated: dependency.task_id === selectedTaskId,
      style: {
        stroke: dependency.task_id === selectedTaskId ? '#6366f1' : '#94a3b8',
        strokeWidth: dependency.task_id === selectedTaskId ? 2.5 : 1.5,
      },
    }))
  }, [dependencies, selectedTaskId])

  const nodes = useMemo<Node[]>(() => {
    const rawNodes = tasks.map((task) => {
      const isSelected = task.task_id === selectedTaskId
      return {
        id: task.task_id,
        data: {
          label: task.title,
        },
        position: { x: 0, y: 0 },
        draggable: false,
        selectable: true,
        style: {
          width: NODE_WIDTH,
          minHeight: NODE_HEIGHT,
          borderRadius: 16,
          border: `1px solid ${nodeBorder(task.status, isSelected)}`,
          background: nodeBackground(task.status, isSelected),
          color: 'var(--foreground)',
          boxShadow: isSelected ? '0 0 0 1px rgba(99,102,241,0.18)' : 'none',
          padding: 12,
          fontSize: 13,
          fontWeight: 500,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          textAlign: 'center' as const,
        },
      } satisfies Node
    })

    return layoutGraph(rawNodes, edges)
  }, [edges, selectedTaskId, tasks])

  return (
    <div className="h-[420px] overflow-hidden rounded-xl border border-border/60 bg-background/70">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        fitView
        panOnScroll
        nodesDraggable={false}
        elementsSelectable
        onNodeClick={(_, node) => {
          router.push(`/project-state?project=${projectId}&task=${node.id}`)
        }}
      >
        <MiniMap
          pannable
          zoomable
          nodeStrokeWidth={2}
          nodeColor={(node) => {
            if (node.id === selectedTaskId) return '#6366f1'
            return '#94a3b8'
          }}
        />
        <Background />
        <Controls />
      </ReactFlow>
    </div>
  )
}
