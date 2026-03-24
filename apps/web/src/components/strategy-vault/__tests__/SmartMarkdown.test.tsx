/**
 * SmartMarkdown Component Tests
 *
 * **Purpose:** Verify GFM markdown rendering with syntax highlighting
 * **Context:** Phase 08-02 - Task 2
 */

import { render, screen } from '@testing-library/react'
import { describe, it, expect, vi } from 'vitest'
import { SmartMarkdown } from '../SmartMarkdown'

// Mock react-syntax-highlighter to avoid heavy transformations in tests
vi.mock('react-syntax-highlighter', () => ({
  Prism: ({ children, language }: { children: string; language: string }) => (
    <pre data-testid="syntax-highlighter" data-language={language}>
      <code>{children}</code>
    </pre>
  ),
}))

vi.mock('react-syntax-highlighter/dist/cjs/styles/prism', () => ({
  atomDark: {},
}))

describe('SmartMarkdown', () => {
  it('renders plain text correctly', () => {
    render(<SmartMarkdown markdown="Hello world" />)
    expect(screen.getByText('Hello world')).toBeInTheDocument()
  })

  it('wraps content in smart-markdown testid div', () => {
    render(<SmartMarkdown markdown="Test" />)
    expect(screen.getByTestId('smart-markdown')).toBeInTheDocument()
  })

  it('renders fenced code block with syntax highlighting', () => {
    const md = '```python\nprint("hello")\n```'
    render(<SmartMarkdown markdown={md} />)
    const highlighter = screen.getByTestId('syntax-highlighter')
    expect(highlighter).toBeInTheDocument()
    expect(highlighter).toHaveAttribute('data-language', 'python')
    expect(highlighter.textContent).toContain('print("hello")')
  })

  it('renders GFM table as HTML table', () => {
    const md = '| Name | Value |\n|------|-------|\n| Alpha | 1 |\n| Beta | 2 |'
    render(<SmartMarkdown markdown={md} />)
    expect(screen.getByRole('table')).toBeInTheDocument()
    expect(screen.getByText('Name')).toBeInTheDocument()
    expect(screen.getByText('Alpha')).toBeInTheDocument()
  })

  it('renders links with target="_blank" and rel="noopener noreferrer"', () => {
    const md = '[Click here](https://example.com)'
    render(<SmartMarkdown markdown={md} />)
    const link = screen.getByRole('link', { name: 'Click here' })
    expect(link).toHaveAttribute('target', '_blank')
    expect(link).toHaveAttribute('rel', 'noopener noreferrer')
    expect(link).toHaveAttribute('href', 'https://example.com')
  })

  it('renders blockquote with styled element', () => {
    const md = '> This is a quote'
    const { container } = render(<SmartMarkdown markdown={md} />)
    const blockquote = container.querySelector('blockquote')
    expect(blockquote).toBeInTheDocument()
    expect(blockquote).toHaveClass('border-l-4')
    expect(blockquote).toHaveClass('italic')
  })

  it('renders inline code with bg-muted styling', () => {
    const md = 'Use `const x = 1` in your code'
    const { container } = render(<SmartMarkdown markdown={md} />)
    const inlineCode = container.querySelector('code.bg-muted')
    expect(inlineCode).toBeInTheDocument()
    expect(inlineCode?.textContent).toBe('const x = 1')
  })

  it('renders GFM strikethrough', () => {
    const md = '~~deleted text~~'
    const { container } = render(<SmartMarkdown markdown={md} />)
    const del = container.querySelector('del')
    expect(del).toBeInTheDocument()
    expect(del?.textContent).toBe('deleted text')
  })

  it('renders GFM task list checkboxes', () => {
    const md = '- [x] Done item\n- [ ] Pending item'
    const { container } = render(<SmartMarkdown markdown={md} />)
    const checkboxes = container.querySelectorAll('input[type="checkbox"]')
    expect(checkboxes.length).toBe(2)
    expect(checkboxes[0]).toBeChecked()
    expect(checkboxes[1]).not.toBeChecked()
  })

  it('handles 1000+ character markdown without errors', () => {
    const longMarkdown = 'Lorem ipsum dolor sit amet. '.repeat(40)
    expect(() => render(<SmartMarkdown markdown={longMarkdown} />)).not.toThrow()
    const el = screen.getByTestId('smart-markdown')
    expect(el).toBeInTheDocument()
  })

  it('does not execute MDX-style JSX (renders as plain text or code)', () => {
    // MDX-style code should render as code block, not execute
    const md = '```jsx\n<script>alert("xss")</script>\n```'
    render(<SmartMarkdown markdown={md} />)
    // Script should NOT be in the DOM as an element — it's inside a code block
    expect(document.querySelector('script')).toBeNull()
  })

  it('applies compact class when compact prop is true', () => {
    const { container } = render(<SmartMarkdown markdown="Test" compact />)
    const wrapper = container.firstChild as HTMLElement
    expect(wrapper?.className).toContain('prose-compact')
  })

  it('applies className prop to wrapper', () => {
    const { container } = render(<SmartMarkdown markdown="Test" className="custom-class" />)
    const wrapper = container.firstChild as HTMLElement
    expect(wrapper?.className).toContain('custom-class')
  })
})
