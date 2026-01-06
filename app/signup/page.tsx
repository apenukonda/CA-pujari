"use client"

import { useState } from "react"
import Link from "next/link"
import { useRouter, useSearchParams } from "next/navigation"
import { createUserWithEmailAndPassword, updateProfile } from "firebase/auth"
import { auth } from "@/lib/firebase"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardAction } from "@/components/ui/card"
import { Checkbox } from "@/components/ui/checkbox"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"

export default function SignupPage() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const course = searchParams.get("course")
   const redirectParam = searchParams.get("redirect")

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

        // 3️⃣ Redirect back (redirect param has priority)
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
    <div className="min-h-screen flex items-center justify-center px-4">
      <Card className="w-full max-w-md">
        <CardHeader>
          <CardTitle>Create Account</CardTitle>
          <CardDescription className="text-center">Start learning with an account</CardDescription>
          <CardAction>
            <Button variant="ghost" size="sm" onClick={() => router.back()}>
              Back
            </Button>
          </CardAction>
        </CardHeader>

        <CardContent>
          <form onSubmit={handleSignup} className="flex flex-col gap-3">
            {error && <p className="text-sm text-red-500 text-center">{error}</p>}

            <div className="flex items-center gap-3">
              <Avatar>
                <AvatarFallback>{name ? name.charAt(0).toUpperCase() : 'U'}</AvatarFallback>
              </Avatar>
              <div>
                <p className="text-sm font-semibold">Create your account</p>
                <p className="text-xs text-muted-foreground">Join 5000+ students and start learning</p>
              </div>
            </div>

            <Input
              type="text"
              placeholder="Full name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
            />

            <Input
              type="email"
              placeholder="Email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />

            <div className="flex gap-2">
              <Input
                type={showPassword ? 'text' : 'password'}
                placeholder="Password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                className="flex-1"
              />
              <Button type="button" variant="ghost" size="sm" onClick={() => setShowPassword((s) => !s)}>
                {showPassword ? 'Hide' : 'Show'}
              </Button>
            </div>

            <label className="flex items-center gap-2">
              <Checkbox checked={agree} onCheckedChange={(v) => setAgree(Boolean(v))} />
              <span className="text-sm">I agree to the Terms of Service</span>
            </label>

            <Button type="submit" disabled={loading || !agree} className="w-full">
              {loading ? "Creating account..." : "Sign Up"}
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
              Already have an account?{' '}
              <button
                type="button"
                onClick={() => router.push(course ? `/login?course=${course}` : "/login")}
                className="text-primary font-medium underline"
              >
                Login
              </button>
            </p>
          </form>
        </CardContent>
      </Card>
    </div>
  )
}
