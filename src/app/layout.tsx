import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import { Providers } from '@/providers'
import Sidebar from '@/components/sidebar'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'Rental Properties',
  description: 'A simple rental properties management system',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={`${inter.className} bg-[hsl(224,71%,4%)] text-white`}>
        <Providers>
          <div className="h-full relative">
            <div className="hidden h-full md:flex md:w-72 md:flex-col md:fixed md:inset-y-0 z-[80]">
              <Sidebar />
            </div>
            <main className="md:pl-72">
              {children}
            </main>
          </div>
        </Providers>
      </body>
    </html>
  )
}
