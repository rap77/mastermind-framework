import { Metadata } from 'next'
import UnifiedInboxPage from '@/components/messaging/UnifiedInboxPage'

export const metadata: Metadata = {
  title: 'Messaging - MasterMind',
  description: 'Unified inbox for WhatsApp, Instagram, and Email',
}

/**
 * Unified inbox page for multi-channel messaging.
 * Displays 3-pane layout: ChannelRail (60px), ThreadList (300px), ThreadDetail (remaining).
 * Supports real-time updates via WebSocket, keyboard navigation (J/K), and thread merging.
 */
export default function MessagingPage() {
  return <UnifiedInboxPage />
}
