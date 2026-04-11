'use client';

import { useMemo } from 'react';
import { useCommandStore } from '@/stores/commandStore';
import { fuzzySearch } from '@/lib/fuzzySearch';
import { COMMANDS } from '@/lib/commands';
import {
  Navigation,
  Brain,
  Zap,
  Settings,
  LucideIcon,
  ChevronRight,
} from 'lucide-react';
import { cn } from '@/lib/utils';

const CATEGORY_ICONS: Record<string, LucideIcon> = {
  Navigation,
  Brains: Brain,
  Actions: Zap,
  Settings,
};

export function VirtualizedCommandList() {
  const { query, selectedIndex } = useCommandStore();

  const filteredCommands = useMemo(() => {
    if (!query) return COMMANDS;
    return fuzzySearch(COMMANDS, query);
  }, [query]);

  // Update filtered commands in store
  useCommandStore.setState({ filteredCommands });

  if (filteredCommands.length === 0) {
    return (
      <div className="py-12 text-center text-muted-foreground">
        No commands found
      </div>
    );
  }

  // Group commands by category
  const groupedCommands = filteredCommands.reduce((acc, command) => {
    const key = command.subcategory || command.category;
    if (!acc[key]) {
      acc[key] = [];
    }
    acc[key].push(command);
    return acc;
  }, {} as Record<string, typeof filteredCommands>);

  const categoryOrder = Object.keys(groupedCommands);

  // Simple rendering without virtualization for now
  // Virtualization can be added back when we have 75+ commands
  return (
    <div className="py-2 max-h-[400px] overflow-y-auto">
      {categoryOrder.map((category) => {
        const commandsInCategory = groupedCommands[category];
        if (!commandsInCategory || commandsInCategory.length === 0) return null;

        return (
          <div key={category}>
            {/* Category header */}
            <div className="px-4 py-1 text-xs font-semibold text-muted-foreground uppercase">
              {category}
            </div>

            {/* Commands in this category */}
            {commandsInCategory.map((command) => {
              const globalIndex = filteredCommands.indexOf(command);
              const Icon = command.icon
                ? CATEGORY_ICONS[command.icon]
                : CATEGORY_ICONS[command.category];

              return (
                <button
                  key={command.id}
                  onClick={() => useCommandStore.getState().executeCommand(command)}
                  className={cn(
                    'w-full flex items-center px-4 py-2 text-left hover:bg-accent hover:text-accent-foreground transition-colors',
                    globalIndex === selectedIndex &&
                      'bg-accent text-accent-foreground border-l-2 border-l-accent-foreground'
                  )}
                  role="option"
                  aria-selected={globalIndex === selectedIndex}
                >
                  {Icon && (
                    <Icon className="w-4 h-4 mr-3 text-muted-foreground" />
                  )}
                  <span className="flex-1">{command.label}</span>
                  {globalIndex === selectedIndex && (
                    <ChevronRight className="w-4 h-4 text-muted-foreground" />
                  )}
                </button>
              );
            })}
          </div>
        );
      })}
    </div>
  );
}
