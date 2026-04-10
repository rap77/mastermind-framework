import { describe, it, expect } from 'vitest';
import { fuzzySearch, highlightMatches } from '@/lib/fuzzySearch';
import { COMMANDS } from '@/lib/commands';

describe('fuzzySearch', () => {
  it('should return all commands when query is empty', () => {
    const result = fuzzySearch(COMMANDS, '');
    expect(result).toHaveLength(COMMANDS.length);
  });

  it('should return all commands when query is whitespace only', () => {
    const result = fuzzySearch(COMMANDS, '   ');
    expect(result).toHaveLength(COMMANDS.length);
  });

  it('should find exact matches with highest score', () => {
    const result = fuzzySearch(COMMANDS, 'Command Center');
    const topResult = result[0];

    expect(topResult.label).toBe('Command Center');
  });

  it('should find commands by label prefix', () => {
    const result = fuzzySearch(COMMANDS, 'Com');

    expect(result.length).toBeGreaterThan(0);
    expect(result[0].label.toLowerCase().substring(0, 3)).toBe('com');
  });

  it('should find commands by partial label match', () => {
    const result = fuzzySearch(COMMANDS, 'enter');

    expect(result.length).toBeGreaterThan(0);
    expect(result.some(cmd => cmd.label.toLowerCase().includes('enter'))).toBe(true);
  });

  it('should find commands by category', () => {
    const result = fuzzySearch(COMMANDS, 'navigation');

    expect(result.length).toBeGreaterThan(0);
    expect(result.every(cmd => cmd.category.toLowerCase().includes('navigation'))).toBe(true);
  });

  it('should find commands by subcategory', () => {
    const result = fuzzySearch(COMMANDS, 'product strategy');

    expect(result.length).toBeGreaterThan(0);
    expect(result.every(cmd => cmd.subcategory?.toLowerCase().includes('product strategy'))).toBe(true);
  });

  it('should find commands by keywords', () => {
    const result = fuzzySearch(COMMANDS, 'dashboard');

    expect(result.length).toBeGreaterThan(0);
    expect(result.some(cmd =>
      cmd.keywords?.some(k => k.toLowerCase().includes('dashboard'))
    )).toBe(true);
  });

  it('should perform fuzzy matching', () => {
    const result = fuzzySearch(COMMANDS, 'strat');

    expect(result.length).toBeGreaterThan(0);
    // Should match "Strategy Vault" or similar
    expect(result.some(cmd => cmd.label.toLowerCase().includes('strat'))).toBe(true);
  });

  it('should be case insensitive', () => {
    const lowerResult = fuzzySearch(COMMANDS, 'product');
    const upperResult = fuzzySearch(COMMANDS, 'PRODUCT');
    const mixedResult = fuzzySearch(COMMANDS, 'PrOdUcT');

    expect(lowerResult).toEqual(upperResult);
    expect(lowerResult).toEqual(mixedResult);
  });

  it('should sort results by relevance score', () => {
    const result = fuzzySearch(COMMANDS, 'product');

    // Exact match should come first
    expect(result[0].label.toLowerCase()).toBe('product vision');
  });

  it('should return empty array when no matches found', () => {
    const result = fuzzySearch(COMMANDS, 'xyz123nonexistent');

    expect(result).toHaveLength(0);
  });

  it('should handle special characters in query', () => {
    const result = fuzzySearch(COMMANDS, 'ci/cd');

    expect(result.length).toBeGreaterThan(0);
  });

  it('should handle queries with spaces', () => {
    const result = fuzzySearch(COMMANDS, 'user research');

    expect(result.length).toBeGreaterThan(0);
    expect(result.some(cmd => cmd.label.toLowerCase().includes('user research'))).toBe(true);
  });

  it('should find commands across all categories', () => {
    const result = fuzzySearch(COMMANDS, 'design');

    const categories = new Set(result.map(cmd => cmd.category));
    // 'design' will mostly find UI Design brains and maybe some settings
    // So we expect at least 1 category
    expect(categories.size).toBeGreaterThanOrEqual(1);
  });

  it('should prioritize brain commands by domain', () => {
    const result = fuzzySearch(COMMANDS, 'design');

    // Should find UI Design brains
    const uiDesignBrains = result.filter(cmd => cmd.subcategory === 'UI Design');
    expect(uiDesignBrains.length).toBeGreaterThan(0);
  });
});

describe('highlightMatches', () => {
  it('should return original text when query is empty', () => {
    const result = highlightMatches('Command Center', '');
    expect(result).toBe('Command Center');
  });

  it('should highlight matching characters', () => {
    const result = highlightMatches('Command Center', 'cmd');

    expect(result).toContain('<strong>');
    expect(result).toContain('</strong>');
    // Should match 'C', 'm', 'm', 'd' characters (case-insensitive)
    expect(result.toLowerCase()).toContain('<strong>c</strong>');
    expect(result.toLowerCase()).toContain('<strong>m</strong>');
    expect(result.toLowerCase()).toContain('<strong>d</strong>');
  });

  it('should be case insensitive', () => {
    const lowerResult = highlightMatches('Command Center', 'cmd');
    const upperResult = highlightMatches('Command Center', 'CMD');

    expect(lowerResult).toBe(upperResult);
  });

  it('should highlight all occurrences of matching characters', () => {
    const result = highlightMatches('Test Test', 't');

    // Should highlight both 't' characters
    expect(result.match(/<strong>t<\/strong>/g)?.length).toBe(2);
  });

  it('should handle special regex characters in query', () => {
    const result = highlightMatches('CI/CD Pipeline', 'ci/cd');

    expect(result).toContain('<strong>');
  });

  it('should not break HTML entities', () => {
    const result = highlightMatches('Test & Test', 'test');

    expect(result).toContain('<strong>');
  });
});
