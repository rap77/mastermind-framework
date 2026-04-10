import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook, act } from '@testing-library/react';
import { useCommandStore } from '@/stores/commandStore';
import { COMMANDS } from '@/lib/commands';
import { fuzzySearch } from '@/lib/fuzzySearch';

describe('VirtualizedCommandList', () => {
  beforeEach(() => {
    useCommandStore.getState().reset();
  });

  it('should render all commands when no query is provided', () => {
    const { result } = renderHook(() => useCommandStore());

    act(() => {
      result.current.setQuery('');
      result.current.setFilteredCommands(COMMANDS);
    });

    expect(result.current.filteredCommands.length).toBe(COMMANDS.length);
  });

  it('should filter commands based on query', () => {
    const { result } = renderHook(() => useCommandStore());

    const filtered = fuzzySearch(COMMANDS, 'product');

    act(() => {
      result.current.setQuery('product');
      result.current.setFilteredCommands(filtered);
    });

    expect(result.current.filteredCommands.length).toBeGreaterThan(0);
    // Check that results are related to 'product' in some way
    expect(result.current.filteredCommands.some(cmd =>
      cmd.label.toLowerCase().includes('product') ||
      cmd.category.toLowerCase().includes('product') ||
      cmd.subcategory?.toLowerCase().includes('product') ||
      cmd.keywords?.some(k => k.toLowerCase().includes('product'))
    )).toBe(true);
  });

  it('should group commands by category', () => {
    const { result } = renderHook(() => useCommandStore());

    act(() => {
      result.current.setQuery('');
      result.current.setFilteredCommands(COMMANDS);
    });

    const categories = new Set(result.current.filteredCommands.map(cmd => cmd.subcategory || cmd.category));
    expect(categories.size).toBeGreaterThan(0);
  });

  it('should have domain grouping for brains', () => {
    const brainCommands = COMMANDS.filter(cmd => cmd.category === 'Brains');
    const domains = new Set(brainCommands.map(cmd => cmd.subcategory));

    // Should have 6 domains: Product Strategy, UX Research, UI Design, Frontend, Backend, QA/DevOps
    expect(domains.size).toBe(6);
    expect(domains.has('Product Strategy')).toBe(true);
    expect(domains.has('UX Research')).toBe(true);
    expect(domains.has('UI Design')).toBe(true);
    expect(domains.has('Frontend')).toBe(true);
    expect(domains.has('Backend')).toBe(true);
    expect(domains.has('QA/DevOps')).toBe(true);
  });

  it('should have 4 brains per domain', () => {
    const brainCommands = COMMANDS.filter(cmd => cmd.category === 'Brains');
    const domains: Record<string, number> = {};

    brainCommands.forEach(cmd => {
      const domain = cmd.subcategory || 'Unknown';
      domains[domain] = (domains[domain] || 0) + 1;
    });

    // Each domain should have exactly 4 brains
    Object.values(domains).forEach(count => {
      expect(count).toBe(4);
    });
  });

  it('should execute command when selected', async () => {
    const { result } = renderHook(() => useCommandStore());

    const mockAction = vi.fn().mockResolvedValue(undefined);
    const testCommand = {
      id: 'test-command',
      label: 'Test Command',
      category: 'Actions' as const,
      action: mockAction,
    };

    act(() => {
      result.current.setFilteredCommands([testCommand]);
      result.current.setSelectedIndex(0);
    });

    await act(async () => {
      await result.current.executeCommand(testCommand);
    });

    expect(mockAction).toHaveBeenCalled();
  });

  it('should prevent duplicate command execution within 1 second', async () => {
    const { result } = renderHook(() => useCommandStore());

    const mockAction = vi.fn().mockResolvedValue(undefined);
    const testCommand = {
      id: 'test-duplicate',
      label: 'Test Duplicate',
      category: 'Actions' as const,
      action: mockAction,
    };

    // First execution
    await act(async () => {
      await result.current.executeCommand(testCommand);
    });

    expect(mockAction).toHaveBeenCalledTimes(1);

    // Second execution within 1 second (should be blocked)
    await act(async () => {
      await result.current.executeCommand(testCommand);
    });

    expect(mockAction).toHaveBeenCalledTimes(1); // Should not be called again
  });

  it('should show loading state during async command execution', async () => {
    const { result } = renderHook(() => useCommandStore());

    let resolveAction: () => void;
    const mockAction = new Promise<void>((resolve) => {
      resolveAction = resolve;
    });

    const testCommand = {
      id: 'test-async',
      label: 'Test Async',
      category: 'Actions' as const,
      action: () => mockAction,
    };

    act(() => {
      result.current.executeCommand(testCommand);
    });

    expect(result.current.isExecuting).toBe(true);

    await act(async () => {
      resolveAction!();
      await mockAction;
    });

    expect(result.current.isExecuting).toBe(false);
  });
});
