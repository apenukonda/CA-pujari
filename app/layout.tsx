import type React from "react"
import type { Metadata } from "next"
import { Geist, Geist_Mono } from "next/font/google"
import { Analytics } from "@vercel/analytics/next"

import { ThemeProvider } from "@/components/theme-provider"
import PageTransition from "@/components/page-transition"
import { AuthProvider } from "@/context/AuthContext"   // ✅ IMPORT THIS
import "./globals.css"

const geist = Geist({ subsets: ["latin"] })
const geistMono = Geist_Mono({ subsets: ["latin"] })

export const metadata: Metadata = {
  title: "Shobha Pujari | Chartered Accountant & Trading Educator",
  description:
    "Learn trading basics for beginners with India's trusted Chartered Accountant and trading educator",
  generator: "v0.app",
  icons: {
    icon: [
      {
        url: "/faviconSP.png",
      },
      {
        url: "/icon-light-32x32.png",
        media: "(prefers-color-scheme: light)",
      },
      {
        url: "/icon-dark-32x32.png",
        media: "(prefers-color-scheme: dark)",
      },
      {
        url: "/icon.svg",
        type: "image/svg+xml",
      },
    ],
    shortcut: "/faviconSP.png",
    apple: "/apple-icon.png",
  },
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className="font-sans antialiased">
        {/* 🔐 AUTH PROVIDER SHOULD BE OUTERMOST */}
        <AuthProvider>
          <ThemeProvider>
            <PageTransition>
              {children}
            </PageTransition>
          </ThemeProvider>
        </AuthProvider>

        <Analytics />
      </body>
    </html>
  )
}
