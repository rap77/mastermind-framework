import { ReactNode } from 'react'

interface MessagingLayoutProps {
  children: ReactNode
}

/**
 * Layout wrapper for messaging routes.
 * Provides consistent structure and SEO metadata for all messaging pages.
 */
export default function MessagingLayout({ children }: MessagingLayoutProps) {
  return (
    <div className="messaging-layout">
      {children}
    </div>
  )
}
