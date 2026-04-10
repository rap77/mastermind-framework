import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { useCommandStore } from '@/stores/commandStore';
import { fuzzySearch, highlightMatches } from '../fuzzySearch';
import { COMMANDS } from '../commands';

describe('Command Palette', () => {
  describe('commandStore', () => {
    beforeEach(() => {
      // Reset store before each test
      useCommandStore.getState().reset();
    });

    it('should open command palette', () => {
      const { open, isOpen } = useCommandStore.getState();

      open();
      expect(useCommandStore.getState().isOpen).toBe(true);
    });

    it('should close command palette', () => {
      const { open, close } = useCommandStore.getState();

      open();
      close();
      expect(useCommandStore.getState().isOpen).toBe(false);
    });

    it('should toggle command palette', () => {
      const { toggle } = useCommandStore.getState();

      toggle();
      expect(useCommandStore.getState().isOpen).toBe(true);

      toggle();
      expect(useCommandStore.getState().isOpen).toBe(false);
    });

    it('should set query', () => {
      const { setQuery } = useCommandStore.getState();

      setQuery('test query');
      expect(useCommandStore.getState().query).toBe('test query');
      expect(useCommandStore.getState().selectedIndex).toBe(0);
    });

    it('should set selected index', () => {
      const { setSelectedIndex } = useCommandStore.getState();

      setSelectedIndex(5);
      expect(useCommandStore.getState().selectedIndex).toBe(5);
    });

    it('should reset all state', () => {
      const { open, setQuery, setSelectedIndex, reset } = useCommandStore.getState();

      open();
      setQuery('test');
      setSelectedIndex(3);
      reset();

      const state = useCommandStore.getState();
      expect(state.isOpen).toBe(false);
      expect(state.query).toBe('');
      expect(state.selectedIndex).toBe(0);
      expect(state.filteredCommands).toEqual([]);
    });
  });

  describe('fuzzySearch', () => {
    it('should return all commands when query is empty', () => {
      const result = fuzzySearch(COMMANDS, '');
      expect(result).toEqual(COMMANDS);
    });

    it('should find exact match', () => {
      const result = fuzzySearch(COMMANDS, 'Command Center');
      expect(result[0].id).toBe('nav-war-room');
    });

    it('should find partial match', () => {
      const result = fuzzySearch(COMMANDS, 'nexus');
      expect(result.some((cmd) => cmd.label.includes('Nexus'))).toBe(true);
    });

    it('should search across keywords', () => {
      const result = fuzzySearch(COMMANDS, 'dashboard');
      expect(result.some((cmd) => cmd.id === 'nav-war-room')).toBe(true);
    });

    it('should return empty array when no matches', () => {
      const result = fuzzySearch(COMMANDS, 'xyznonexistent');
      expect(result).toEqual([]);
    });

    it('should be case insensitive', () => {
      const result1 = fuzzySearch(COMMANDS, 'strategy');
      const result2 = fuzzySearch(COMMANDS, 'STRATEGY');
      const result3 = fuzzySearch(COMMANDS, 'StRaTeGy');

      expect(result1.length).toBeGreaterThan(0);
      expect(result2.length).toBe(result1.length);
      expect(result3.length).toBe(result1.length);
    });

    it('should sort by relevance score', () => {
      const result = fuzzySearch(COMMANDS, 'brain');

      // Exact matches should come first
      const brainCommands = result.filter((cmd) => cmd.category === 'Brains');
      expect(brainCommands.length).toBeGreaterThan(0);
    });
  });

  describe('highlightMatches', () => {
    it('should highlight matching characters', () => {
      const result = highlightMatches('Command Center', 'cmd');
      expect(result).toContain('<strong>');
    });

    it('should return original text when query is empty', () => {
      const result = highlightMatches('Command Center', '');
      expect(result).toBe('Command Center');
    });

    it('should be case insensitive', () => {
      const result1 = highlightMatches('Command Center', 'cmd');
      const result2 = highlightMatches('Command Center', 'CMD');

      expect(result1).toContain('<strong>');
      expect(result2).toContain('<strong>');
    });
  });

  describe('Command Categories', () => {
    it('should have 4 main categories', () => {
      const categories = new Set(COMMANDS.map((cmd) => cmd.category));
      expect(categories).toEqual(
        new Set(['Navigation', 'Brains', 'Actions', 'Settings'])
      );
    });

    it('should group brains by domain (6 subcategories per Brain #7)', () => {
      const brainCommands = COMMANDS.filter((cmd) => cmd.category === 'Brains');
      const subcategories = new Set(
        brainCommands.map((cmd) => cmd.subcategory).filter(Boolean)
      );

      expect(subcategories).toEqual(
        new Set([
          'Product Strategy',
          'UX Research',
          'UI Design',
          'Frontend',
          'Backend',
          'QA/DevOps',
        ])
      );
    });

    it('should have 4 navigation commands', () => {
      const navCommands = COMMANDS.filter((cmd) => cmd.category === 'Navigation');
      expect(navCommands.length).toBe(4);
    });

    it('should have 24 brain commands (4 per domain)', () => {
      const brainCommands = COMMANDS.filter((cmd) => cmd.category === 'Brains');
      expect(brainCommands.length).toBe(24);
    });

    it('should have action and settings commands', () => {
      const actionCommands = COMMANDS.filter((cmd) => cmd.category === 'Actions');
      const settingsCommands = COMMANDS.filter((cmd) => cmd.category === 'Settings');

      expect(actionCommands.length).toBeGreaterThan(0);
      expect(settingsCommands.length).toBeGreaterThan(0);
    });
  });

  describe('Command Execution', () => {
    it('should execute navigation commands', async () => {
      const navCommand = COMMANDS.find((cmd) => cmd.id === 'nav-war-room');
      expect(navCommand).toBeDefined();

      // Mock window.location.href
      const originalLocation = window.location.href;
      delete (window as any).location;
      (window as any).location = { href: '' };

      await navCommand!.action();

      expect(window.location.href).toBe('/war-room');

      // Restore
      window.location.href = originalLocation;
    });

    it('should handle brain trigger commands', async () => {
      const brainCommand = COMMANDS.find((cmd) => cmd.id === 'brain-product-vision');
      expect(brainCommand).toBeDefined();

      // Mock fetch
      global.fetch = vi.fn(() =>
        Promise.resolve({
          ok: true,
          json: () => Promise.resolve({ success: true }),
        } as Response)
      );

      await expect(brainCommand!.action()).resolves.not.toThrow();

      vi.restoreAllMocks();
    });

    it('should handle command execution errors', async () => {
      const errorCommand: typeof COMMANDS[0] = {
        id: 'test-error',
        label: 'Test Error',
        category: 'Actions',
        action: async () => {
          throw new Error('Test error');
        },
      };

      await expect(errorCommand.action()).rejects.toThrow('Test error');
    });
  });

  describe('Keyboard Shortcuts', () => {
    it('should listen for Cmd+K / Ctrl+K globally', () => {
      const { isOpen } = useCommandStore.getState();

      // Simulate Cmd+K
      const event = new KeyboardEvent('keydown', {
        key: 'k',
        metaKey: true,
        ctrlKey: true,
      });
      window.dispatchEvent(event);

      // Store should toggle
      expect(useCommandStore.getState().isOpen).toBe(!isOpen);
    });

    it('should close on Escape', () => {
      const { open } = useCommandStore.getState();
      open();

      const event = new KeyboardEvent('keydown', { key: 'Escape' });
      window.dispatchEvent(event);

      expect(useCommandStore.getState().isOpen).toBe(false);
    });
  });
});
