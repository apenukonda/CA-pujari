"use client"

import { useState } from "react"
import Link from "next/link"
import { useRouter } from "next/navigation"
import { signInWithEmailAndPassword } from "firebase/auth"
import { auth } from "@/lib/firebase"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
  CardAction,
} from "@/components/ui/card"
import { Checkbox } from "@/components/ui/checkbox"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { motion } from "framer-motion"

export default function LoginPage() {
  const router = useRouter()
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [loading, setLoading] = useState(false)
  const [showPassword, setShowPassword] = useState(false)
  const [remember, setRemember] = useState(false)

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)

    try {
      await signInWithEmailAndPassword(auth, email, password)
      const params = new URLSearchParams(window.location.search)
      const redirect = params.get("redirect") || "/"
      router.push(redirect)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center px-4
      bg-gradient-to-br from-background via-muted to-background">

      <motion.div
        initial={{ opacity: 0, y: 30, scale: 0.98 }}
        animate={{ opacity: 1, y: 0, scale: 1 }}
        transition={{ duration: 0.6, ease: "easeOut" }}
        className="w-full max-w-md"
      >
        <Card className="relative overflow-hidden shadow-2xl rounded-3xl">
          {/* subtle glow */}
          <div className="absolute inset-0 bg-primary/5 pointer-events-none" />

          <CardHeader className="space-y-2">
            <CardTitle className="text-2xl font-extrabold">
              Welcome back
            </CardTitle>
            <CardDescription>
              Login to continue your learning journey
            </CardDescription>
            <CardAction>
              <Button variant="ghost" size="sm" onClick={() => router.back()}>
                Back
              </Button>
            </CardAction>
          </CardHeader>

          <CardContent>
            <form onSubmit={handleLogin} className="flex flex-col gap-5">
              {/* ACCOUNT PREVIEW */}
              <div className="flex items-center gap-4 rounded-xl bg-muted/50 p-4">
                <Avatar>
                  <AvatarFallback className="font-bold">N</AvatarFallback>
                </Avatar>
                <div>
                  <p className="text-sm font-semibold">
                    Sign in to your account
                  </p>
                  <p className="text-xs text-muted-foreground">
                    Access courses & saved progress
                  </p>
                </div>
              </div>

              {/* EMAIL */}
              <Input
                type="email"
                placeholder="Email address"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
              />

              {/* PASSWORD */}
              <div className="flex gap-2">
                <Input
                  type={showPassword ? "text" : "password"}
                  placeholder="Password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  className="flex-1"
                />
                <Button
                  type="button"
                  variant="ghost"
                  size="sm"
                  onClick={() => setShowPassword((s) => !s)}
                >
                  {showPassword ? "Hide" : "Show"}
                </Button>
              </div>

              {/* REMEMBER / FORGOT */}
              <div className="flex items-center justify-between">
                <label className="flex items-center gap-2 cursor-pointer">
                  <Checkbox
                    checked={remember}
                    onCheckedChange={(v) => setRemember(Boolean(v))}
                  />
                  <span className="text-sm">Remember me</span>
                </label>
                <Link href="/forgot" className="text-sm text-primary underline">
                  Forgot password?
                </Link>
              </div>

              {/* SUBMIT */}
              <Button type="submit" disabled={loading} className="w-full py-6 text-base">
                {loading ? "Signing in..." : "Login & Continue"}
              </Button>

              {/* DIVIDER */}
              <div className="flex items-center gap-3">
                <div className="h-px flex-1 bg-border" />
                <span className="text-xs text-muted-foreground">
                  Or continue with
                </span>
                <div className="h-px flex-1 bg-border" />
              </div>

              {/* OAUTH */}
              <div className="flex gap-3">
                <Button variant="outline" className="flex-1">
                  Google
                </Button>
                <Button variant="outline" className="flex-1">
                  GitHub
                </Button>
              </div>

              {/* SIGNUP */}
              <p className="text-center text-sm text-muted-foreground">
                Don’t have an account?{" "}
                <Link href="/signup" className="text-primary font-medium underline">
                  Create one
                </Link>
              </p>
            </form>
          </CardContent>
        </Card>
      </motion.div>
    </div>
  )
}
