"use client"

import Link from "next/link"
import { CreditCard } from "lucide-react"
import { useAuth } from "@/context/AuthContext"

export default function WebinarBookButton({ id }: { id: number | string }) {
  const { user } = useAuth()

  const hrefIfLoggedIn = `/webinars/book/${id}`
  const redirectIfNot = `/login?redirect=${encodeURIComponent(`/webinars?book=${id}`)}`

  return user ? (
    <Link
      href={hrefIfLoggedIn}
      className="px-6 py-3 bg-primary text-primary-foreground rounded-lg hover:opacity-90 transition-opacity font-semibold flex items-center gap-2"
    >
      <CreditCard size={18} />
      Book Seat
    </Link>
  ) : (
    <Link
      href={redirectIfNot}
      className="px-6 py-3 bg-primary text-primary-foreground rounded-lg hover:opacity-90 transition-opacity font-semibold flex items-center gap-2"
    >
      <CreditCard size={18} />
      Book Seat
    </Link>
  )
}
