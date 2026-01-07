"use client"

import { useState } from "react"
import { useRouter, useSearchParams } from "next/navigation"
import { createUserWithEmailAndPassword, updateProfile } from "firebase/auth"
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

export default function SignupClient() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const course = searchParams?.get("course")
  const redirectParam = searchParams?.get("redirect")

  const [name, setName] = useState("")
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [error, setError] = useState("")
  const [loading, setLoading] = useState(false)
  const [showPassword, setShowPassword] = useState(false)
  const [agree, setAgree] = useState(false)

  const handleSignup = async (e: React.FormEvent) => {
    e.preventDefault()
    setError("")
    setLoading(true)

    try {
      const userCredential = await createUserWithEmailAndPassword(
        auth,
        email,
        password
      )

      if (userCredential.user) {
        await updateProfile(userCredential.user, {
          displayName: name,
        })
      }

      if (redirectParam) {
        router.push(redirectParam)
      } else if (course) {
        router.push(`/courses/${course}`)
      } else {
        router.push("/")
      }
    } catch (err: any) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div
      className="min-h-screen flex items-center justify-center px-4
      bg-gradient-to-br from-background via-muted to-background"
    >
      <motion.div
        initial={{ opacity: 0, y: 30, scale: 0.98 }}
        animate={{ opacity: 1, y: 0, scale: 1 }}
        transition={{ duration: 0.6, ease: "easeOut" }}
        className="w-full max-w-md"
      >
        <Card className="relative overflow-hidden rounded-3xl shadow-2xl">
          {/* subtle glow */}
          <div className="absolute inset-0 bg-primary/5 pointer-events-none" />

          <CardHeader className="space-y-2">
            <CardTitle className="text-2xl font-extrabold">
              Create your account
            </CardTitle>
            <CardDescription className="text-center">
              Start learning with structure and confidence
            </CardDescription>
            <CardAction>
              <Button variant="ghost" size="sm" onClick={() => router.back()}>
                Back
              </Button>
            </CardAction>
          </CardHeader>

          <CardContent>
            <form onSubmit={handleSignup} className="flex flex-col gap-5">
              {error && (
                <p className="text-sm text-red-500 text-center">{error}</p>
              )}

              {/* PROFILE PREVIEW */}
              <div className="flex items-center gap-4 rounded-xl bg-muted/50 p-4">
                <Avatar>
                  <AvatarFallback className="font-bold">
                    {name ? name.charAt(0).toUpperCase() : "U"}
                  </AvatarFallback>
                </Avatar>
                <div>
                  <p className="text-sm font-semibold">
                    Create your account
                  </p>
                  <p className="text-xs text-muted-foreground">
                    Join 5,000+ learners and grow confidently
                  </p>
                </div>
              </div>

              {/* NAME */}
              <Input
                type="text"
                placeholder="Full name"
                value={name}
                onChange={(e) => setName(e.target.value)}
                required
              />

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

              {/* TERMS */}
              <label className="flex items-center gap-2 cursor-pointer">
                <Checkbox
                  checked={agree}
                  onCheckedChange={(v) => setAgree(Boolean(v))}
                />
                <span className="text-sm">
                  I agree to the Terms of Service
                </span>
              </label>

              {/* SUBMIT */}
              <Button
                type="submit"
                disabled={loading || !agree}
                className="w-full py-6 text-base"
              >
                {loading ? "Creating account..." : "Create Account"}
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

              {/* LOGIN LINK */}
              <p className="text-center text-sm text-muted-foreground">
                Already have an account?{" "}
                <button
                  type="button"
                  onClick={() =>
                    router.push(course ? `/login?course=${course}` : "/login")
                  }
                  className="text-primary font-medium underline"
                >
                  Login
                </button>
              </p>
            </form>
          </CardContent>
        </Card>
      </motion.div>
    </div>
  )
}
