import { Command } from '@/stores/commandStore';

/**
 * Simple fuzzy search implementation with score-based matching
 * Searches across command label, category, subcategory, and keywords
 */
export function fuzzySearch(commands: Command[], query: string): Command[] {
  if (!query.trim()) {
    return commands;
  }

  const searchTerm = query.toLowerCase().trim();

  const scoredCommands = commands.map((command) => {
    let score = 0;
    const label = command.label.toLowerCase();
    const category = command.category.toLowerCase();
    const subcategory = command.subcategory?.toLowerCase() || '';
    const keywords = command.keywords?.map((k) => k.toLowerCase()) || [];

    // Exact match in label (highest score)
    if (label === searchTerm) {
      score += 100;
    }

    // Starts with search term (high score)
    if (label.startsWith(searchTerm)) {
      score += 50;
    }

    // Contains search term (medium score)
    if (label.includes(searchTerm)) {
      score += 25;
    }

    // Category match
    if (category.includes(searchTerm)) {
      score += 20;
    }

    // Subcategory match
    if (subcategory.includes(searchTerm)) {
      score += 15;
    }

    // Keyword match
    if (keywords.some((keyword) => keyword.includes(searchTerm))) {
      score += 10;
    }

    // Character-by-character fuzzy match (lowest score)
    const fuzzyScore = calculateFuzzyScore(label, searchTerm);
    score += fuzzyScore;

    return { ...command, score };
  });

  // Filter out commands with zero score and sort by score descending
  return scoredCommands
    .filter((cmd) => cmd.score > 0)
    .sort((a, b) => b.score - a.score)
    .map(({ score: _score, ...command }) => command);
}

/**
 * Calculate fuzzy match score based on character sequence
 */
function calculateFuzzyScore(text: string, query: string): number {
  if (!query) return 0;

  let textIndex = 0;
  let queryIndex = 0;
  let score = 0;
  let consecutiveMatches = 0;

  while (textIndex < text.length && queryIndex < query.length) {
    if (text[textIndex] === query[queryIndex]) {
      score += 1;
      consecutiveMatches += 1;

      // Bonus for consecutive matches
      if (consecutiveMatches > 1) {
        score += consecutiveMatches;
      }

      queryIndex += 1;
    } else {
      consecutiveMatches = 0;
    }

    textIndex += 1;
  }

  // Only return score if all query characters were matched
  return queryIndex === query.length ? score : 0;
}

/**
 * Highlight matching characters in text
 */
export function highlightMatches(text: string, query: string): string {
  if (!query) return text;

  const regex = new RegExp(`(${query.split('').join('|')})`, 'gi');
  return text.replace(regex, '<strong>$1</strong>');
}
