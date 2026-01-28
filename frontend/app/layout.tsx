import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'Consent-Aware AI Dashboard',
  description: 'Developer tool for debugging and evaluating AI systems with consent-aware data access',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}
