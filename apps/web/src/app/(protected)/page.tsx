import { redirect } from 'next/navigation'

/**
 * Protected root page — redirects to Command Center
 *
 * **Note:** This was the WS Pipeline Test page during development.
 * Now redirects to the actual Command Center (Phase 06).
 */
export default function ProtectedRootPage() {
  redirect('/command-center')
}
