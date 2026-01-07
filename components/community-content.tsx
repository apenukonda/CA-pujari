"use client"

import { MessageSquare, Heart, Share2, Eye } from "lucide-react"
import { useRouter } from "next/navigation"
import { useEffect, useState } from "react"
import { auth } from "@/lib/firebase"

export default function CommunityContent() {
  const router = useRouter()
  const categories = ["Trading Basics", "Market Psychology", "Q&A", "Success Stories", "Technical Analysis"]

  const initialPosts = [
    {
      id: 1,
      title: "How to Read Candlestick Charts Like a Pro",
      excerpt: "Master the art of reading candlestick patterns and identify trading opportunities with confidence.",
      category: "Technical Analysis",
      author: "Shobha Pujari",
      date: "January 10, 2026",
      views: 1240,
      likes: 89,
      comments: 23,
    },
    {
      id: 2,
      title: "Overcoming Trading Fear: A Beginner's Guide",
      excerpt: "Fear is natural in trading. Learn practical strategies to manage emotions and make rational decisions.",
      category: "Market Psychology",
      author: "Shobha Pujari",
      date: "January 8, 2026",
      views: 2100,
      likes: 156,
      comments: 67,
    },
    {
      id: 3,
      title: "Why Most Beginners Fail in Trading",
      excerpt: "Common mistakes that prevent beginners from succeeding and how to avoid them in your trading journey.",
      category: "Trading Basics",
      author: "Shobha Pujari",
      date: "January 5, 2026",
      views: 3400,
      likes: 234,
      comments: 112,
    },
  ]

  const [posts, setPosts] = useState(initialPosts)
  const [showForm, setShowForm] = useState(false)
  const [title, setTitle] = useState("")
  const [category, setCategory] = useState(categories[0])
  const [excerpt, setExcerpt] = useState("")

  useEffect(() => {
    auth.currentUser
  }, [])

  function requireAuthRedirect() {
    if (!auth.currentUser) {
      router.push(`/signup?redirect=/community`)
      return false
    }
    return true
  }

  const handleNewPost = (e: React.FormEvent) => {
    e.preventDefault()
    if (!requireAuthRedirect()) return

    const newPost = {
      id: Date.now(),
      title,
      excerpt,
      category,
      author: auth.currentUser?.displayName || auth.currentUser?.email || "Member",
      date: new Date().toLocaleDateString(),
      views: 0,
      likes: 0,
      comments: 0,
    }

    setPosts((p) => [newPost, ...p])
    setShowForm(false)
    setTitle("")
    setExcerpt("")
    setCategory(categories[0])
  }

  return (
    <section className="py-12 bg-background">
      <div className="max-w-4xl mx-auto px-4">

        {/* Header */}
        <div className="mb-10 text-center">
          <h1 className="text-3xl font-bold text-foreground">Community Hub</h1>
          <p className="text-muted-foreground mt-2 max-w-xl mx-auto">
            Learn, share strategies, and grow together with traders worldwide.
          </p>
        </div>

        {/* Create Post CTA */}
        <div className="mb-8 flex justify-center">
          <button
            onClick={() => {
              if (!requireAuthRedirect()) return
              setShowForm((s) => !s)
            }}
            className="px-6 py-2.5 rounded-full bg-primary text-primary-foreground font-semibold shadow-sm hover:opacity-95 transition"
          >
            {showForm ? "Cancel" : "Create New Post"}
          </button>
        </div>

        {/* Post Form */}
        {showForm && (
          <form
            onSubmit={handleNewPost}
            className="mb-10 bg-card border border-border rounded-xl p-6 space-y-4"
          >
            <input
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              required
              placeholder="Post title"
              className="w-full px-4 py-2 rounded-md border border-border bg-background"
            />

            <select
              value={category}
              onChange={(e) => setCategory(e.target.value)}
              className="w-full px-4 py-2 rounded-md border border-border bg-background"
            >
              {categories.map((c) => (
                <option key={c} value={c}>{c}</option>
              ))}
            </select>

            <textarea
              value={excerpt}
              onChange={(e) => setExcerpt(e.target.value)}
              required
              rows={4}
              placeholder="Share your insight, question, or experience..."
              className="w-full px-4 py-2 rounded-md border border-border bg-background resize-none"
            />

            <div className="text-right">
              <button
                type="submit"
                className="px-5 py-2 rounded-md bg-primary text-primary-foreground font-semibold"
              >
                Publish
              </button>
            </div>
          </form>
        )}

        {/* Feed */}
        <div className="space-y-6">
          {posts.map((post) => (
            <article
              key={post.id}
              className="bg-card border border-border rounded-xl p-6 hover:shadow-md transition"
            >
              {/* Category */}
              <span className="inline-block mb-3 text-xs font-semibold tracking-wide text-accent">
                {post.category}
              </span>

              {/* Title */}
              <h2 className="text-xl font-bold text-foreground mb-2">
                {post.title}
              </h2>

              {/* Excerpt */}
              <p className="text-muted-foreground mb-5 leading-relaxed">
                {post.excerpt}
              </p>

              {/* Meta */}
              <div className="flex items-center justify-between text-sm text-muted-foreground">
                <div>
                  <span className="font-medium">{post.author}</span>
                  <span className="mx-2">•</span>
                  <span>{post.date}</span>
                </div>

                {/* Metrics */}
                <div className="flex items-center gap-5">
                  <div className="flex items-center gap-1">
                    <Eye size={16} />
                    <span>{post.views}</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <Heart size={16} />
                    <span>{post.likes}</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <MessageSquare size={16} />
                    <span>{post.comments}</span>
                  </div>
                  <button className="font-semibold hover:text-primary transition">
                    Read →
                  </button>
                </div>
              </div>
            </article>
          ))}
        </div>
      </div>
    </section>
  )
}
