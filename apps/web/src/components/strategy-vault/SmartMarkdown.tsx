'use client'

import React, { memo } from 'react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { SMART_GFM_COMPONENTS } from '@/lib/smart-gfm'
import { cn } from '@/lib/utils'

// ─── Props ────────────────────────────────────────────────────────────────────

export interface SmartMarkdownProps {
  /** Markdown string to render (brain output format) */
  markdown: string
  /** Additional CSS classes for the wrapper */
  className?: string
  /** Reduce margins for compact display (e.g., inside accordion items) */
  compact?: boolean
}

// ─── Component ────────────────────────────────────────────────────────────────

/**
 * SmartMarkdown — react-markdown with GFM plugins + custom styled components.
 *
 * **Features:**
 * - GFM tables, strikethrough, checklists via remark-gfm
 * - Syntax highlighted code blocks (atomDark theme via react-syntax-highlighter)
 * - Links open in new tab with rel="noopener noreferrer"
 * - Styled blockquotes with left border
 * - No MDX execution (allowDangerousHtml=false by default)
 * - Memoized with React.memo (static once rendered from brain output)
 *
 * **Charts deferred to v2.2:**
 * - :::chart ... ::: syntax renders as code block fallback
 * - Post-v2.1 can add rehype plugin for chart parsing
 *
 * @example
 * ```tsx
 * <SmartMarkdown markdown={brainOutput} compact />
 * ```
 */
export const SmartMarkdown = memo(function SmartMarkdown({
  markdown,
  className,
  compact = false,
}: SmartMarkdownProps) {
  return (
    <div
      className={cn(
        'prose prose-sm max-w-none dark:prose-invert',
        compact ? 'prose-compact' : 'space-y-2',
        className
      )}
      data-testid="smart-markdown"
    >
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        components={SMART_GFM_COMPONENTS}
      >
        {markdown}
      </ReactMarkdown>
    </div>
  )
})

SmartMarkdown.displayName = 'SmartMarkdown'
