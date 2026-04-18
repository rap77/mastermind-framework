/**
 * FlowPalette — Draggable node types palette
 *
 * **Features:**
 * - Sidebar with draggable node types for the Flow Designer
 * - Full accessibility with ARIA labels and descriptions
 * - Keyboard and screen reader support
 *
 * @example
 * ```tsx
 * <FlowPalette />
 * ```
 */

import { NodeType } from './types'

// CSS-in-JS for palette node hover effect
const PALETTE_NODE_CSS = `
  .palette-node-item:hover {
    border-color: var(--color-primary) !important;
  }
`

// Inject CSS styles on module load
if (typeof document !== 'undefined') {
  const styleId = 'flow-palette-node-styles'
  if (!document.getElementById(styleId)) {
    const style = document.createElement('style')
    style.id = styleId
    style.textContent = PALETTE_NODE_CSS
    document.head.appendChild(style)
  }
}

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
      role="complementary"
      aria-label="Flow node palette"
    >
      <h3 className="font-semibold mb-4 text-sm" style={{ color: 'var(--color-text-primary)' }}>
        Node Types
      </h3>

      <div
        className="space-y-2"
        role="listbox"
        aria-label="Available node types"
      >
        {NODE_TYPES.map((nodeType) => (
          <div
            key={nodeType.type}
            draggable
            onDragStart={(e) => onDragStart(e, nodeType.type)}
            className={`
              p-3 rounded-lg border cursor-move
              transition-all duration-200
              hover:shadow-md
              palette-node-item
            `}
            style={{
              backgroundColor: 'var(--color-surface)',
              borderColor: 'var(--color-border)',
            }}
            role="option"
            aria-label={nodeType.label}
            aria-describedby={`node-${nodeType.type}-description`}
          >
            <div className="flex items-center gap-2">
              <span className="text-lg" aria-hidden="true">{nodeType.icon}</span>
              <div>
                <div className="font-medium text-sm" style={{ color: 'var(--color-text-primary)' }}>
                  {nodeType.label}
                </div>
                <div
                  className="text-xs"
                  style={{ color: 'var(--color-text-secondary)' }}
                  id={`node-${nodeType.type}-description`}
                >
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
