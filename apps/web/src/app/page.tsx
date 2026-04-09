import { redirect } from 'next/navigation'

export default function RootPage() {
  // Redirect to login by default
  redirect('/login')
}
