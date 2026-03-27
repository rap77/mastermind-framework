/**
 * smart-gfm.ts — Custom component mapping for SmartMarkdown
 *
 * **Purpose:** Map react-markdown elements to styled React components
 * **Context:** Phase 08-02 - Strategy Vault SmartMarkdown
 *
 * **Scope:**
 * - Code blocks → react-syntax-highlighter (atomOneDark theme)
 * - Tables → overflow-x scrollable with border
 * - Links → target="_blank" rel="noopener noreferrer"
 * - Blockquotes → left-border styled
 * - Charts (:::chart syntax) → deferred to v2.2, render as code block
 *
 * **Security:** allowDangerousHtml is false by default in react-markdown.
 * DOMPurify sanitization available via sanitizeHtml() export.
 */

import React from 'react'
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter'
import { atomDark } from 'react-syntax-highlighter/dist/cjs/styles/prism'
import type { Components } from 'react-markdown'

// ─── Component Definitions ────────────────────────────────────────────────────

/**
 * Code block component — inline or fenced with syntax highlighting
 */
const CodeComponent: Components['code'] = ({ className, children, ...props }) => {
  // Check if it's a fenced code block via className (language-xxx)
  const isBlock = Boolean(className)
  const lang = className?.replace(/language-/, '') || 'text'

  if (!isBlock) {
    return (
      <code className="bg-muted px-1 py-0.5 rounded text-sm font-mono" {...props}>
        {children}
      </code>
    )
  }

  return (
    <SyntaxHighlighter
      language={lang}
      style={atomDark}
      PreTag="div"
      className="rounded-md my-3 text-sm"
    >
      {String(children).replace(/\n$/, '')}
    </SyntaxHighlighter>
  )
}

/**
 * Table component — horizontally scrollable with border
 */
const TableComponent: Components['table'] = ({ children, ...props }) => (
  <div className="overflow-x-auto border border-border rounded my-3">
    <table className="min-w-full divide-y divide-border text-sm" {...props}>
      {children}
    </table>
  </div>
)

/**
 * Table header cell — with background
 */
const ThComponent: Components['th'] = ({ children, ...props }) => (
  <th
    className="px-3 py-2 text-left font-medium bg-muted text-muted-foreground"
    {...props}
  >
    {children}
  </th>
)

/**
 * Table data cell
 */
const TdComponent: Components['td'] = ({ children, ...props }) => (
  <td className="px-3 py-2 border-t border-border" {...props}>
    {children}
  </td>
)

/**
 * Link component — opens in new tab with security attributes
 */
const LinkComponent: Components['a'] = ({ href, children, ...props }) => (
  <a
    href={href}
    target="_blank"
    rel="noopener noreferrer"
    className="text-primary underline underline-offset-2 hover:opacity-80 transition-opacity"
    {...props}
  >
    {children}
  </a>
)

/**
 * Blockquote component — left-border styling
 */
const BlockquoteComponent: Components['blockquote'] = ({ children, ...props }) => (
  <blockquote
    className="border-l-4 border-primary/30 pl-4 italic text-muted-foreground my-3"
    {...props}
  >
    {children}
  </blockquote>
)

/**
 * Heading components — scoped styles within SmartMarkdown
 */
const H1Component: Components['h1'] = ({ children, ...props }) => (
  <h1 className="text-2xl font-bold mt-6 mb-3" {...props}>{children}</h1>
)

const H2Component: Components['h2'] = ({ children, ...props }) => (
  <h2 className="text-xl font-semibold mt-5 mb-2" {...props}>{children}</h2>
)

const H3Component: Components['h3'] = ({ children, ...props }) => (
  <h3 className="text-lg font-medium mt-4 mb-2" {...props}>{children}</h3>
)

// ─── Exported Component Map ───────────────────────────────────────────────────

/**
 * SMART_GFM_COMPONENTS — component mapping for react-markdown
 *
 * Pass directly as the `components` prop on <ReactMarkdown>.
 */
export const SMART_GFM_COMPONENTS: Components = {
  code: CodeComponent,
  table: TableComponent,
  th: ThComponent,
  td: TdComponent,
  a: LinkComponent,
  blockquote: BlockquoteComponent,
  h1: H1Component,
  h2: H2Component,
  h3: H3Component,
}

// ─── Sanitization helper ──────────────────────────────────────────────────────

/**
 * sanitizeHtml — Optional DOMPurify sanitization for brain outputs with inline HTML.
 *
 * Only needed if brain outputs include raw HTML (e.g., <img src="...">).
 * react-markdown's allowDangerousHtml is false by default (safe default).
 *
 * Usage:
 * ```tsx
 * import { sanitizeHtml } from '@/lib/smart-gfm'
 * const cleanMarkdown = sanitizeHtml(rawMarkdown)
 * <SmartMarkdown markdown={cleanMarkdown} />
 * ```
 */
export function sanitizeHtml(html: string): string {
  // Only run in browser environment
  if (typeof window === 'undefined') return html

  // DOMPurify is available (installed in package.json)
  try {
    // Dynamic require to avoid SSR import — .default for CJS interop
    const { default: DOMPurify } = require('dompurify') as typeof import('dompurify')
    return DOMPurify.sanitize(html, { USE_PROFILES: { html: true } })
  } catch {
    // DOMPurify unavailable in test environment — return as-is
    return html
  }
}

// Re-export React for consumers
export { React }
