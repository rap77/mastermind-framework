'use client'

import { useBrainStore, useBrainState } from '@/stores/brainStore'
import type { BrainStatus } from '@/stores/brainStore'

const TEST_BRAIN_IDS = Array.from({ length: 24 }, (_, i) => `brain-${i}`)

function BrainTile({ id }: { id: string }) {
  const brain = useBrainState(id)
  return (
    <div className="rounded border p-2">
      <div className="text-sm font-medium">{id}</div>
      <div className="text-xs text-gray-500">{brain?.status ?? 'idle'}</div>
    </div>
  )
}

export default function WarRoomPage() {
  const brains = useBrainStore(state => state.brains)

  const simulate24Events = () => {
    const statuses: BrainStatus[] = ['idle', 'active', 'complete', 'error']
    const now = Date.now()

    // Trigger 24 simultaneous updates (tests RAF batching)
    TEST_BRAIN_IDS.forEach((id, i) => {
      setTimeout(() => {
        useBrainStore.getState().updateBrain({
          id,
          status: statuses[i % 4],
          lastUpdated: now,
        })
      }, i * 10)  // Stagger slightly to simulate real WS burst
    })
  }

  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold mb-4">WS Pipeline Test</h1>
      <button onClick={simulate24Events} className="mb-4 rounded bg-blue-500 px-4 py-2">
        Simulate 24 Brain Events
      </button>
      <div className="grid grid-cols-4 gap-2">
        {TEST_BRAIN_IDS.map(id => <BrainTile key={id} id={id} />)}
      </div>
      <div className="mt-4 text-sm text-gray-500">
        Brains in store: {brains.size}
      </div>
    </div>
  )
}
