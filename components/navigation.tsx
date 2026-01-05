"use client"

import Link from "next/link"
import { useState } from "react"
import { Menu, X } from "lucide-react"
<<<<<<< HEAD
import { ThemeToggle } from "@/components/theme-toggle"
import { motion } from "framer-motion"
=======
>>>>>>> 812be5e7ce5ea23a600fb8e7ea086bc566a2ec02

export function Navigation() {
  const [isOpen, setIsOpen] = useState(false)

  const navItems = [
    { label: "Home", href: "/" },
    { label: "Courses", href: "/courses" },
    { label: "Webinars", href: "/webinars" },
    { label: "Community", href: "/community" },
    { label: "About", href: "/about" },
    { label: "Contact", href: "/contact" },
  ]

  return (
<<<<<<< HEAD
    <motion.nav
      initial={{ y: -20, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.4 }}
      className="sticky top-0 z-50 bg-background border-b border-border"
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          
=======
    <nav className="sticky top-0 z-50 bg-background border-b border-border">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
>>>>>>> 812be5e7ce5ea23a600fb8e7ea086bc566a2ec02
          {/* Logo */}
          <Link href="/" className="font-bold text-2xl text-primary">
            Shobha Pujari
          </Link>

          {/* Desktop Navigation */}
          <div className="hidden md:flex gap-8">
            {navItems.map((item) => (
              <Link
                key={item.href}
                href={item.href}
                className="text-foreground hover:text-primary transition-colors text-sm font-medium"
              >
                {item.label}
              </Link>
            ))}
          </div>

<<<<<<< HEAD
          {/* Right side (CTA + Dark Mode) */}
          <div className="hidden md:flex items-center gap-4">
            <ThemeToggle />

            <Link
              href="/courses"
              className="px-6 py-2 bg-primary text-primary-foreground rounded-lg
                         hover:opacity-90 transition-opacity text-sm font-medium"
            >
              Get Started
            </Link>
          </div>

          {/* Mobile Menu Button */}
          <button
            onClick={() => setIsOpen(!isOpen)}
            className="md:hidden p-2 text-foreground"
          >
=======
          {/* CTA Button */}
          <Link
            href="/courses"
            className="hidden md:block px-6 py-2 bg-primary text-primary-foreground rounded-lg hover:opacity-90 transition-opacity text-sm font-medium"
          >
            Get Started
          </Link>

          {/* Mobile Menu Button */}
          <button onClick={() => setIsOpen(!isOpen)} className="md:hidden p-2 text-foreground">
>>>>>>> 812be5e7ce5ea23a600fb8e7ea086bc566a2ec02
            {isOpen ? <X size={24} /> : <Menu size={24} />}
          </button>
        </div>

        {/* Mobile Menu */}
        {isOpen && (
<<<<<<< HEAD
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            transition={{ duration: 0.3 }}
            className="md:hidden pb-4 space-y-2"
          >
=======
          <div className="md:hidden pb-4 space-y-2">
>>>>>>> 812be5e7ce5ea23a600fb8e7ea086bc566a2ec02
            {navItems.map((item) => (
              <Link
                key={item.href}
                href={item.href}
                className="block px-4 py-2 text-foreground hover:bg-muted rounded-lg transition-colors"
                onClick={() => setIsOpen(false)}
              >
                {item.label}
              </Link>
            ))}
<<<<<<< HEAD

            <div className="flex items-center gap-4 px-4">
              <ThemeToggle />
              <Link
                href="/courses"
                className="flex-1 px-4 py-2 bg-primary text-primary-foreground
                           rounded-lg text-center font-medium"
              >
                Get Started
              </Link>
            </div>
          </motion.div>
        )}
      </div>
    </motion.nav>
=======
            <Link
              href="/courses"
              className="block px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:opacity-90 transition-opacity font-medium"
            >
              Get Started
            </Link>
          </div>
        )}
      </div>
    </nav>
>>>>>>> 812be5e7ce5ea23a600fb8e7ea086bc566a2ec02
  )
}
