/**
 * Channel-specific message types
 *
 * Brain #7 Condition #3: Discriminated unions to prevent Schema Leak
 * (unified abstraction failure)
 *
 * Each channel has its own message structure with channel-specific fields.
 * Type guards ensure type-safe routing without if/else chains.
 */

export type ChannelType = 'whatsapp' | 'instagram' | 'email'
export type MessageStatus = 'sent' | 'delivered' | 'read' | 'failed'

// Base message interface
interface BaseMessage {
  id: string
  threadId: string
  timestamp: Date
  status: MessageStatus
}

// WhatsApp-specific message
export interface WhatsAppMessage extends BaseMessage {
  channel: 'whatsapp'
  messageType: 'text' | 'image' | 'video' | 'interactive' | 'location'
  content: string
  interactiveButtons?: Array<{ title: string; payload: string }>
  mediaUrl?: string
}

// Instagram-specific message
export interface InstagramMessage extends BaseMessage {
  channel: 'instagram'
  messageType: 'comment' | 'mention' | 'dm'
  content: string
  mediaType?: 'photo' | 'video' | 'carousel'
  mediaUrl?: string
  parentCommentId?: string // Threading
}

// Email-specific message
export interface EmailMessage extends BaseMessage {
  channel: 'email'
  messageType: 'plain' | 'html'
  subject: string
  from: { email: string; name: string }
  to: Array<{ email: string; name: string }>
  htmlContent?: string
  textContent?: string
  attachments?: Array<{ filename: string; url: string; size: number }>
  inReplyTo?: string // Threading
  references?: string[] // Threading
}

// Discriminated union
export type ChannelMessage = WhatsAppMessage | InstagramMessage | EmailMessage

// Type guards
export function isWhatsAppMessage(msg: ChannelMessage): msg is WhatsAppMessage {
  return msg.channel === 'whatsapp'
}

export function isInstagramMessage(msg: ChannelMessage): msg is InstagramMessage {
  return msg.channel === 'instagram'
}

export function isEmailMessage(msg: ChannelMessage): msg is EmailMessage {
  return msg.channel === 'email'
}

// Legacy MessageState for backward compatibility
export interface MessageState {
  id: string
  channel: ChannelType
  sender: string
  content: string
  media_url?: string
  status: MessageStatus
  timestamp: number
  thread_id: string
}

// Draft type
export interface MessageDraft {
  channel_id: string
  content: string
  media_attachments: string[]
}
