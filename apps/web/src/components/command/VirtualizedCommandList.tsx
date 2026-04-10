'use client';

import { useMemo } from 'react';
import { FixedSizeList as List } from 'react-window';
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

const ITEM_HEIGHT = 44; // Height of each command item in pixels
const CATEGORY_HEADER_HEIGHT = 28; // Height of category header

interface ItemData {
  groupedCommands: Record<string, typeof COMMANDS>;
  filteredCommands: typeof COMMANDS;
  selectedIndex: number;
  categoryOrder: string[];
  categoryOffsets: Record<string, number>;
}

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

  // Calculate category order and offsets for virtualization
  const categoryOrder = Object.keys(groupedCommands);
  const categoryOffsets: Record<string, number> = {};
  let currentOffset = 0;

  categoryOrder.forEach((category) => {
    categoryOffsets[category] = currentOffset;
    currentOffset += CATEGORY_HEADER_HEIGHT; // Category header
    currentOffset += groupedCommands[category].length * ITEM_HEIGHT; // Commands
  });

  const totalHeight = currentOffset;

  // Render function for each virtualized item
  const Row = ({ index, style, data }: { index: number; style: React.CSSProperties; data: ItemData }) => {
    // Find which category this index belongs to
    let currentOffset = 0;
    let targetCategory = '';
    let itemIndexInCategory = 0;

    for (const category of data.categoryOrder) {
      const categoryHeight = CATEGORY_HEADER_HEIGHT + data.groupedCommands[category].length * ITEM_HEIGHT;
      if (currentOffset + categoryHeight > index * ITEM_HEIGHT) {
        targetCategory = category;
        const offsetWithinCategory = index * ITEM_HEIGHT - currentOffset;
        if (offsetWithinCategory < CATEGORY_HEADER_HEIGHT) {
          // This is a category header
          return (
            <div style={style} className="px-4 py-1 text-xs font-semibold text-muted-foreground uppercase">
              {category}
            </div>
          );
        } else {
          // This is a command item
          itemIndexInCategory = Math.floor((offsetWithinCategory - CATEGORY_HEADER_HEIGHT) / ITEM_HEIGHT);
          break;
        }
      }
      currentOffset += categoryHeight;
    }

    if (!targetCategory) return null;

    const command = data.groupedCommands[targetCategory][itemIndexInCategory];
    if (!command) return null;

    const globalIndex = data.filteredCommands.indexOf(command);
    const Icon = command.icon
      ? CATEGORY_ICONS[command.icon]
      : CATEGORY_ICONS[command.category];

    return (
      <div style={style}>
        <button
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
      </div>
    );
  };

  const itemData: ItemData = {
    groupedCommands,
    filteredCommands,
    selectedIndex,
    categoryOrder,
    categoryOffsets,
  };

  return (
    <div className="py-2">
      <List
        height={400} // Max height from command palette
        itemCount={Math.ceil(totalHeight / ITEM_HEIGHT)}
        itemSize={ITEM_HEIGHT}
        width="100%"
        itemData={itemData}
      >
        {Row}
      </List>
    </div>
  );
}
