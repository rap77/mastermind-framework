'use client';

import { useEffect, useRef } from 'react';
import { useCommandStore } from '@/stores/commandStore';
import { CommandInput } from './CommandInput';
import { CommandList } from './CommandList';
import { VirtualizedCommandList } from './VirtualizedCommandList';

export function CommandPalette() {
  const { isOpen, close, filteredCommands, executeCommand } =
    useCommandStore();
  const overlayRef = useRef<HTMLDivElement>(null);

  // Focus trap and click outside handling
  useEffect(() => {
    if (!isOpen) return;

    const handleKeyDown = (e: KeyboardEvent) => {
      const startTime = performance.now();

      if (e.key === 'ArrowDown') {
        e.preventDefault();
        const { selectedIndex, filteredCommands } = useCommandStore.getState();
        const newIndex = Math.min(selectedIndex + 1, filteredCommands.length - 1);
        useCommandStore.setState({ selectedIndex: newIndex });

        // Measure latency per Brain #7 Condition 4
        const endTime = performance.now();
        const latency = endTime - startTime;
        if (latency > 50) {
          console.warn(`Keyboard navigation latency: ${latency.toFixed(2)}ms (target: <50ms)`);
        }
      }

      if (e.key === 'ArrowUp') {
        e.preventDefault();
        const { selectedIndex } = useCommandStore.getState();
        const newIndex = Math.max(selectedIndex - 1, 0);
        useCommandStore.setState({ selectedIndex: newIndex });

        const endTime = performance.now();
        const latency = endTime - startTime;
        if (latency > 50) {
          console.warn(`Keyboard navigation latency: ${latency.toFixed(2)}ms (target: <50ms)`);
        }
      }

      if (e.key === 'Enter') {
        e.preventDefault();
        const { filteredCommands, selectedIndex } = useCommandStore.getState();
        const selectedCommand = filteredCommands[selectedIndex];
        if (selectedCommand) {
          executeCommand(selectedCommand);
        }
      }
    };

    const handleClickOutside = (e: MouseEvent) => {
      if (
        overlayRef.current &&
        !overlayRef.current.contains(e.target as Node)
      ) {
        close();
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    document.addEventListener('mousedown', handleClickOutside);

    return () => {
      window.removeEventListener('keydown', handleKeyDown);
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [isOpen, close, executeCommand]);

  if (!isOpen) return null;

  return (
    <div
      ref={overlayRef}
      className="fixed inset-0 z-50 flex items-start justify-center pt-[20vh]"
      role="dialog"
      aria-modal="true"
      aria-labelledby="command-palette-title"
    >
      {/* Backdrop with blur per Brain #4 requirement */}
      <div
        className="fixed inset-0 bg-black/50 backdrop-blur-sm"
        aria-hidden="true"
      />

      {/* Dialog */}
      <div className="relative z-50 w-full max-w-2xl mx-4 overflow-hidden rounded-lg bg-background shadow-xl border">
        {/* Header */}
        <div className="flex items-center border-b px-4">
          <CommandInput />
        </div>

        {/* Command List - use virtualization if command count > 75 per Brain #4 requirement */}
        <div className="max-h-[400px] overflow-y-auto">
          {filteredCommands.length > 75 ? <VirtualizedCommandList /> : <CommandList />}
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between border-t px-4 py-2 text-sm text-muted-foreground">
          <div className="flex items-center gap-4">
            <span className="flex items-center gap-1">
              <kbd className="px-1.5 py-0.5 rounded bg-muted text-xs">↑↓</kbd>
              <span>navigate</span>
            </span>
            <span className="flex items-center gap-1">
              <kbd className="px-1.5 py-0.5 rounded bg-muted text-xs">↵</kbd>
              <span>select</span>
            </span>
            <span className="flex items-center gap-1">
              <kbd className="px-1.5 py-0.5 rounded bg-muted text-xs">esc</kbd>
              <span>close</span>
            </span>
          </div>

          {/* Known conflicts documentation per Brain #7 Condition 1 */}
          <div className="text-xs">
            Chrome Mac: <kbd className="px-1 py-0.5 rounded bg-muted">⌘K</kbd> may open dev console
          </div>
        </div>
      </div>
    </div>
  );
}
