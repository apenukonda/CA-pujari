"use client"

import { useState } from "react"
import Link from "next/link"
import { useRouter } from "next/navigation"
import { signInWithEmailAndPassword } from "firebase/auth"
import { auth } from "@/lib/firebase"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardAction } from "@/components/ui/card"
import { Checkbox } from "@/components/ui/checkbox"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"

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
    <div className="min-h-screen flex items-center justify-center px-4">
      <Card className="w-full max-w-md">
        <CardHeader>
          <CardTitle>Welcome back</CardTitle>
          <CardDescription>Login to continue to your account</CardDescription>
          <CardAction>
            <Button variant="ghost" size="sm" onClick={() => router.back()}>
              Back
            </Button>
          </CardAction>
        </CardHeader>

        <CardContent>
          <form onSubmit={handleLogin} className="flex flex-col gap-3">
            <div className="flex items-center gap-3">
              <Avatar>
                <AvatarFallback>N</AvatarFallback>
              </Avatar>
              <div>
                <p className="text-sm font-semibold">Sign in to your account</p>
                <p className="text-xs text-muted-foreground">Access your courses and saved progress</p>
              </div>
            </div>

            <Input
              type="email"
              placeholder="Email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />

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

            <div className="flex items-center justify-between">
              <label className="flex items-center gap-2">
                <Checkbox checked={remember} onCheckedChange={(v) => setRemember(Boolean(v))} />
                <span className="text-sm">Remember me</span>
              </label>
              <Link href="/forgot" className="text-sm text-primary underline">
                Forgot password?
              </Link>
            </div>

            <Button type="submit" disabled={loading} className="w-full">
              {loading ? "Signing in..." : "Login & Continue"}
            </Button>

            <div className="flex items-center gap-3">
              <div className="h-px flex-1 bg-border" />
              <span className="text-xs text-muted-foreground">Or continue with</span>
              <div className="h-px flex-1 bg-border" />
            </div>

            <div className="flex gap-2">
              <Button variant="outline" className="flex-1">Google</Button>
              <Button variant="outline" className="flex-1">GitHub</Button>
            </div>

            <p className="text-center text-sm text-muted-foreground">
              Don’t have an account?{' '}
              <Link href="/signup" className="text-primary font-medium underline">
                Create one
              </Link>
            </p>
          </form>
        </CardContent>
      </Card>
    </div>
  )
}
