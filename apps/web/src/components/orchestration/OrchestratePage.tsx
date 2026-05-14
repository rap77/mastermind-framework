'use client'

/**
 * OrchestratePage — Three-column Orchestration Canvas layout.
 *
 * Layout: [BrainList | OrchestrationCanvas | OutputPanel]
 *
 * Responsive:
 * - >= 1280px (xl): three columns, side-by-side
 * - < 1280px: tab-based navigation (BrainList / Canvas / Output)
 *
 * The active brain selection is lifted here so all three panels stay in sync:
 * - BrainList shows active brain highlighted
 * - OrchestrationCanvas dims non-selected nodes
 * - OutputPanel shows output for active brain
 */

import { useState } from 'react'
import type { Brain } from '@/lib/api'
import { BrainList } from './BrainList'
import { OrchestrationCanvas } from './OrchestrationCanvas'
import { OutputPanel } from './OutputPanel'
import { cn } from '@/lib/utils'

// ─── Types ─────────────────────────────────────────────────────────────────────

type OrchestrateTab = 'brains' | 'canvas' | 'output'

interface OrchestratePageProps {
  blueprintBrains: Brain[]
}

// ─── Component ─────────────────────────────────────────────────────────────────

export function OrchestratePage({ blueprintBrains }: OrchestratePageProps) {
  const [selectedBrainId, setSelectedBrainId] = useState<string | null>(null)
  const [activeTab, setActiveTab] = useState<OrchestrateTab>('canvas')

  const selectedBrain = blueprintBrains.find((b) => b.id === selectedBrainId) ?? null

  const handleBrainSelect = (brainId: string) => {
    setSelectedBrainId(brainId)
    // On mobile/tablet: switch to output tab after selecting a brain
    setActiveTab('output')
  }

  return (
    <div className="h-full flex flex-col overflow-hidden" data-testid="orchestrate-page">
      {/* ── Desktop layout (xl+): three columns side-by-side ─────────────── */}
      <div className="hidden xl:flex h-full">
        {/* Column 1: BrainList — fixed 260px */}
        <div className="w-[260px] flex-shrink-0 border-r border-border overflow-y-auto">
          <BrainList
            brains={blueprintBrains}
            selectedBrainId={selectedBrainId}
            onSelect={setSelectedBrainId}
          />
        </div>

        {/* Column 2: OrchestrationCanvas — fills remaining space */}
        <div className="flex-1 min-w-0 overflow-hidden">
          <OrchestrationCanvas
            blueprintBrains={blueprintBrains}
            selectedBrainId={selectedBrainId}
            onSelect={setSelectedBrainId}
          />
        </div>

        {/* Column 3: OutputPanel — fixed 320px */}
        <div className="w-[320px] flex-shrink-0 border-l border-border overflow-y-auto">
          <OutputPanel selectedBrain={selectedBrain} />
        </div>
      </div>

      {/* ── Mobile/tablet layout (<1280px): tab-based ────────────────────── */}
      <div className="xl:hidden flex flex-col h-full">
        {/* Tab bar */}
        <div
          className="flex border-b border-border bg-background flex-shrink-0"
          role="tablist"
          aria-label="Orchestration views"
        >
          <TabButton
            active={activeTab === 'brains'}
            onClick={() => setActiveTab('brains')}
            label="Brains"
            id="tab-brains"
            panelId="panel-brains"
          />
          <TabButton
            active={activeTab === 'canvas'}
            onClick={() => setActiveTab('canvas')}
            label="Canvas"
            id="tab-canvas"
            panelId="panel-canvas"
          />
          <TabButton
            active={activeTab === 'output'}
            onClick={() => setActiveTab('output')}
            label="Output"
            id="tab-output"
            panelId="panel-output"
          />
        </div>

        {/* Tab panels */}
        <div className="flex-1 overflow-hidden">
          <TabPanel id="panel-brains" labelledById="tab-brains" active={activeTab === 'brains'}>
            <div className="h-full overflow-y-auto">
              <BrainList
                brains={blueprintBrains}
                selectedBrainId={selectedBrainId}
                onSelect={handleBrainSelect}
              />
            </div>
          </TabPanel>

          <TabPanel id="panel-canvas" labelledById="tab-canvas" active={activeTab === 'canvas'}>
            <OrchestrationCanvas
              blueprintBrains={blueprintBrains}
              selectedBrainId={selectedBrainId}
              onSelect={(id) => {
                setSelectedBrainId(id)
                setActiveTab('output')
              }}
            />
          </TabPanel>

          <TabPanel id="panel-output" labelledById="tab-output" active={activeTab === 'output'}>
            <div className="h-full overflow-y-auto">
              <OutputPanel selectedBrain={selectedBrain} />
            </div>
          </TabPanel>
        </div>
      </div>
    </div>
  )
}

// ─── TabButton ─────────────────────────────────────────────────────────────────

interface TabButtonProps {
  active: boolean
  onClick: () => void
  label: string
  id: string
  panelId: string
}

function TabButton({ active, onClick, label, id, panelId }: TabButtonProps) {
  return (
    <button
      type="button"
      role="tab"
      id={id}
      aria-controls={panelId}
      aria-selected={active}
      onClick={onClick}
      className={cn(
        'flex-1 py-2 px-4 text-sm font-medium transition-colors',
        active
          ? 'border-b-2 border-primary text-primary'
          : 'text-muted-foreground hover:text-foreground',
      )}
    >
      {label}
    </button>
  )
}

// ─── TabPanel ──────────────────────────────────────────────────────────────────

interface TabPanelProps {
  id: string
  labelledById: string
  active: boolean
  children: React.ReactNode
}

function TabPanel({ id, labelledById, active, children }: TabPanelProps) {
  return (
    <div
      id={id}
      role="tabpanel"
      aria-labelledby={labelledById}
      className={cn('h-full', active ? 'block' : 'hidden')}
    >
      {children}
    </div>
  )
}
