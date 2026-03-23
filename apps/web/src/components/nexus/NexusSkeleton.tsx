/**
 * NexusSkeleton — Loading state for NexusCanvas
 *
 * 24 pulsing skeleton cards matching approximate dagre layout proportions.
 * Motion guard prevents animation for reduced-motion preference.
 */
export function NexusSkeleton() {
  // 1 coordinator (larger) + 23 brain satellites
  const satellites = Array.from({ length: 23 }, (_, i) => i)

  return (
    <div
      className="h-full w-full flex flex-col items-center justify-center gap-8"
      style={{ background: '#0B0C10' }}
      aria-busy="true"
      aria-label="Loading Nexus canvas"
    >
      {/* Coordinator node */}
      <div
        className="w-[100px] h-[100px] rounded-xl bg-muted/20 animate-pulse motion-reduce:animate-none"
        aria-hidden="true"
      />

      {/* Brain satellite nodes — arranged in rows */}
      <div className="flex flex-wrap gap-3 justify-center max-w-4xl">
        {satellites.map(i => (
          <div
            key={i}
            className="w-[160px] h-[60px] rounded-xl bg-muted/20 animate-pulse motion-reduce:animate-none"
            style={{
              // Stagger animation delay — max 500ms total (Brain-03 spec)
              animationDelay: `${Math.min(i * 20, 460)}ms`,
            }}
            aria-hidden="true"
          />
        ))}
      </div>
    </div>
  )
}
