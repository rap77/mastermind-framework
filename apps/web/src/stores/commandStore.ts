import { create } from 'zustand';
import { toastSuccess, toastError } from '@/lib/toast';

export interface Command {
  id: string;
  label: string;
  category: 'Navigation' | 'Brains' | 'Actions' | 'Settings';
  subcategory?: string;
  icon?: string;
  action: () => void | Promise<void>;
  keywords?: string[];
}

interface CommandState {
  isOpen: boolean;
  query: string;
  selectedIndex: number;
  filteredCommands: Command[];
  isExecuting: boolean; // Add loading state for async commands
  lastExecutedCommand: string | null; // For idempotency check
  lastExecutionTime: number | null; // For idempotency debounce
}

interface CommandActions {
  open: () => void;
  close: () => void;
  toggle: () => void;
  setQuery: (query: string) => void;
  setSelectedIndex: (index: number) => void;
  setFilteredCommands: (commands: Command[]) => void;
  executeCommand: (command: Command) => Promise<void>;
  reset: () => void;
}

export const useCommandStore = create<CommandState & CommandActions>((set, get) => ({
  isOpen: false,
  query: '',
  selectedIndex: 0,
  filteredCommands: [],
  isExecuting: false,
  lastExecutedCommand: null,
  lastExecutionTime: null,

  open: () => set({ isOpen: true, query: '', selectedIndex: 0 }),

  close: () => set({ isOpen: false, query: '', selectedIndex: 0, filteredCommands: [], isExecuting: false }),

  toggle: () => {
    const { isOpen } = get();
    if (isOpen) {
      get().close();
    } else {
      get().open();
    }
  },

  setQuery: (query: string) => set({ query, selectedIndex: 0 }),

  setSelectedIndex: (selectedIndex: number) => set({ selectedIndex }),

  setFilteredCommands: (filteredCommands: Command[]) =>
    set({ filteredCommands, selectedIndex: 0 }),

  executeCommand: async (command: Command) => {
    const { lastExecutedCommand, lastExecutionTime, isExecuting } = get();

    // Idempotency check per Brain #5 requirement
    const now = Date.now();
    const isDuplicate =
      lastExecutedCommand === command.id &&
      lastExecutionTime &&
      now - lastExecutionTime < 1000; // 1 second debounce

    if (isDuplicate) {
      toastError('Command already executing');
      return;
    }

    if (isExecuting) {
      toastError('Please wait for current command to finish');
      return;
    }

    set({ isExecuting: true, lastExecutedCommand: command.id, lastExecutionTime: now });

    try {
      await command.action();
      toastSuccess(`Executed: ${command.label}`);
      get().close();
    } catch (error) {
      console.error('Command execution failed:', error);
      toastError(`Failed: ${error instanceof Error ? error.message : 'Unknown error'}`);
    } finally {
      set({ isExecuting: false });
    }
  },

  reset: () =>
    set({
      isOpen: false,
      query: '',
      selectedIndex: 0,
      filteredCommands: [],
      isExecuting: false,
      lastExecutedCommand: null,
      lastExecutionTime: null,
    }),
}));

// Keyboard shortcut listener (Cmd+K / Ctrl+K)
if (typeof window !== 'undefined') {
  window.addEventListener('keydown', (e) => {
    // Check for Cmd+K (Mac) or Ctrl+K (Windows/Linux)
    if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
      e.preventDefault();
      useCommandStore.getState().toggle();
    }

    // Escape key closes the palette
    if (e.key === 'Escape') {
      const { isOpen } = useCommandStore.getState();
      if (isOpen) {
        useCommandStore.getState().close();
      }
    }
  });
}
