import './globals.css'
import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import { Providers } from './providers'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'AI Chat, Build & Learn',
  description: 'Collaborative AI-powered learning environment with HRM-enhanced reasoning',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" style={{ height: '100%', margin: 0, padding: 0 }}>
      <body style={{ 
        height: '100vh', 
        width: '100vw', 
        margin: 0, 
        padding: 0, 
        overflow: 'hidden',
        backgroundColor: '#0a0a0a'
      }} className={`${inter.className}`}>
        <Providers>
          {children}
        </Providers>
      </body>
    </html>
  )
}
