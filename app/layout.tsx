import type React from "react"
import type { Metadata } from "next"
import { Geist, Geist_Mono } from "next/font/google"
import { Analytics } from "@vercel/analytics/next"
<<<<<<< HEAD
import { ThemeProvider } from "@/components/theme-provider"
import PageTransition from "@/components/page-transition"
=======
>>>>>>> 812be5e7ce5ea23a600fb8e7ea086bc566a2ec02
import "./globals.css"

const _geist = Geist({ subsets: ["latin"] })
const _geistMono = Geist_Mono({ subsets: ["latin"] })

export const metadata: Metadata = {
  title: "Shobha Pujari | Chartered Accountant & Trading Educator",
<<<<<<< HEAD
  description:
    "Learn trading basics for beginners with India's trusted Chartered Accountant and trading educator",
=======
  description: "Learn trading basics for beginners with India's trusted Chartered Accountant and trading educator",
>>>>>>> 812be5e7ce5ea23a600fb8e7ea086bc566a2ec02
  generator: "v0.app",
  icons: {
    icon: [
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
    apple: "/apple-icon.png",
  },
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
<<<<<<< HEAD
    <html lang="en" suppressHydrationWarning>
      <body className="font-sans antialiased">
        <ThemeProvider>
          <PageTransition>
            {children}
          </PageTransition>
        </ThemeProvider>

=======
    <html lang="en">
      <body className={`font-sans antialiased`}>
        {children}
>>>>>>> 812be5e7ce5ea23a600fb8e7ea086bc566a2ec02
        <Analytics />
      </body>
    </html>
  )
}
