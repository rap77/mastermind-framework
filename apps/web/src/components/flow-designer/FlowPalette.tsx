/**
 * FlowPalette — Draggable node types palette
 *
 * Sidebar with draggable node types for the Flow Designer.
 */

import { NodeType } from './types'

const NODE_TYPES: Array<{
  type: NodeType
  label: string
  icon: string
  description: string
}> = [
  {
    type: NodeType.BRAIN,
    label: 'Brain',
    icon: '🧠',
    description: 'Agent brain node',
  },
  {
    type: NodeType.GATEWAY,
    label: 'Gateway',
    icon: '🚪',
    description: 'Entry/exit point',
  },
  {
    type: NodeType.ADAPTER,
    label: 'Adapter',
    icon: '🔌',
    description: 'Integration adapter',
  },
  {
    type: NodeType.ROUTER,
    label: 'Router',
    icon: '↗️',
    description: 'Conditional routing',
  },
  {
    type: NodeType.CONDITION,
    label: 'Condition',
    icon: '❓',
    description: 'Boolean logic',
  },
]

export function FlowPalette() {
  const onDragStart = (event: React.DragEvent, nodeType: NodeType) => {
    event.dataTransfer.setData('application/reactflow', nodeType)
    event.dataTransfer.effectAllowed = 'move'
  }

  return (
    <div
      className="w-64 border-r p-4 overflow-y-auto"
      style={{
        backgroundColor: 'var(--color-surface)',
        borderColor: 'var(--color-border)',
      }}
    >
      <h3 className="font-semibold mb-4 text-sm" style={{ color: 'var(--color-text-primary)' }}>
        Node Types
      </h3>

      <div className="space-y-2">
        {NODE_TYPES.map((nodeType) => (
          <div
            key={nodeType.type}
            draggable
            onDragStart={(e) => onDragStart(e, nodeType.type)}
            className={`
              p-3 rounded-lg border cursor-move
              transition-all duration-200
              hover:shadow-md
            `}
            style={{
              backgroundColor: 'var(--color-surface)',
              borderColor: 'var(--color-border)',
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.borderColor = 'var(--color-primary)'
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.borderColor = 'var(--color-border)'
            }}
          >
            <div className="flex items-center gap-2">
              <span className="text-lg">{nodeType.icon}</span>
              <div>
                <div className="font-medium text-sm" style={{ color: 'var(--color-text-primary)' }}>
                  {nodeType.label}
                </div>
                <div className="text-xs" style={{ color: 'var(--color-text-secondary)' }}>
                  {nodeType.description}
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
