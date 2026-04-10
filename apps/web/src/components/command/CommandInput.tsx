'use client';

import { useEffect, useRef } from 'react';
import { useCommandStore } from '@/stores/commandStore';
import { Search } from 'lucide-react';
import { cn } from '@/lib/utils';

export function CommandInput() {
  const { query, setQuery, isOpen } = useCommandStore();
  const inputRef = useRef<HTMLInputElement>(null);

  // Auto-focus input when palette opens
  useEffect(() => {
    if (isOpen) {
      inputRef.current?.focus();
    }
  }, [isOpen]);

  return (
    <div className="flex items-center flex-1 py-4">
      <Search className="w-5 h-5 mr-3 text-muted-foreground" />
      <input
        ref={inputRef}
        type="text"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="Search... ⌘K"
        className="flex-1 bg-transparent border-none outline-none text-foreground placeholder:text-muted-foreground"
        aria-label="Search commands"
        role="searchbox"
        id="command-palette-title"
      />
      {query && (
        <button
          onClick={() => setQuery('')}
          className="ml-2 text-muted-foreground hover:text-foreground"
          aria-label="Clear search"
        >
          ×
        </button>
      )}
    </div>
  );
}
