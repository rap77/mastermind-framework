/**
 * Flow Designer Route — n8n-style node-based flow editor
 *
 * Main page for the Flow Designer feature.
 * Layout: Palette (left) | Canvas (center) | Toolbar (top)
 *
 * Features:
 * - Drag-and-drop node creation
 * - Visual flow editing with React Flow v12
 * - Export/Import JSON
 * - Zoom/pan controls
 * - Minimap for navigation
 */

'use client'

import { ReactFlowProvider } from '@xyflow/react'
import { FlowDesignerCanvas } from '@/components/flow-designer/FlowDesignerCanvas'

export default function FlowDesignerPage() {
  return (
    <ReactFlowProvider>
      <FlowDesignerCanvas />
    </ReactFlowProvider>
  )
}
