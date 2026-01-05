"use client"

import { Search, MessageSquare, Heart, Share2 } from "lucide-react"

export default function CommunityContent() {
  const categories = ["Trading Basics", "Market Psychology", "Q&A", "Success Stories", "Technical Analysis"]

  const posts = [
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
    {
      id: 4,
      title: "Understanding Support and Resistance Levels",
      excerpt:
        "A comprehensive guide to identifying and using support and resistance levels in your technical analysis.",
      category: "Technical Analysis",
      author: "Shobha Pujari",
      date: "January 2, 2026",
      views: 1890,
      likes: 145,
      comments: 54,
    },
    {
      id: 5,
      title: "My First Trading Win: A Student Success Story",
      excerpt: "How Rajesh transformed from a skeptical beginner to a confident trader in just 3 months.",
      category: "Success Stories",
      author: "Guest Contributor",
      date: "December 28, 2025",
      views: 2560,
      likes: 198,
      comments: 89,
    },
    {
      id: 6,
      title: "Q&A: What's the Best Time to Trade?",
      excerpt: "Answers to the most common questions about market hours, session timings, and optimal trading times.",
      category: "Q&A",
      author: "Shobha Pujari",
      date: "December 25, 2025",
      views: 1450,
      likes: 102,
      comments: 78,
    },
  ]

  return (
    <section className="py-16 bg-background">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
          {/* Sidebar */}
          <div className="lg:col-span-1">
            {/* Search */}
            <div className="mb-8">
              <div className="relative">
                <input
                  type="text"
                  placeholder="Search posts..."
                  className="w-full px-4 py-3 rounded-lg border border-border bg-card text-foreground placeholder-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary"
                />
                <Search className="absolute right-3 top-3.5 text-muted-foreground" size={20} />
              </div>
            </div>

            {/* Categories */}
            <div className="bg-card rounded-lg border border-border p-6">
              <h3 className="font-bold text-foreground mb-4">Categories</h3>
              <div className="space-y-2">
                {categories.map((category) => (
                  <button
                    key={category}
                    className="w-full text-left px-4 py-2 rounded-lg hover:bg-muted transition-colors text-muted-foreground hover:text-foreground"
                  >
                    {category}
                  </button>
                ))}
              </div>
            </div>

            {/* CTA */}
            <div className="mt-8 bg-gradient-to-br from-primary to-accent p-6 rounded-lg text-primary-foreground">
              <h3 className="font-bold mb-3">Join Our Community</h3>
              <p className="text-sm mb-4 opacity-90">
                Connect with traders, ask questions, and share your success stories.
              </p>
              <button className="w-full px-4 py-2 bg-primary-foreground text-primary rounded-lg hover:opacity-90 transition-opacity font-semibold text-sm">
                Join Now
              </button>
            </div>
          </div>

          {/* Posts */}
          <div className="lg:col-span-3">
            <div className="space-y-6">
              {posts.map((post) => (
                <article
                  key={post.id}
                  className="bg-card rounded-xl border border-border p-6 hover:shadow-lg transition-shadow"
                >
                  <div className="flex items-start justify-between mb-4">
                    <div>
                      <div className="inline-block px-3 py-1 bg-accent/10 text-accent text-xs font-semibold rounded-full mb-3">
                        {post.category}
                      </div>
                      <h2 className="text-2xl font-bold text-foreground mb-3">{post.title}</h2>
                    </div>
                  </div>

                  <p className="text-muted-foreground mb-4 leading-relaxed">{post.excerpt}</p>

                  <div className="flex items-center justify-between text-sm text-muted-foreground mb-4">
                    <div className="flex gap-4">
                      <span>By {post.author}</span>
                      <span>{post.date}</span>
                    </div>
                    <span>{post.views} views</span>
                  </div>

                  <div className="border-t border-border pt-4 flex items-center justify-between">
                    <div className="flex gap-6">
                      <button className="flex items-center gap-2 text-muted-foreground hover:text-primary transition-colors">
                        <Heart size={18} />
                        <span className="text-sm">{post.likes}</span>
                      </button>
                      <button className="flex items-center gap-2 text-muted-foreground hover:text-primary transition-colors">
                        <MessageSquare size={18} />
                        <span className="text-sm">{post.comments}</span>
                      </button>
                      <button className="flex items-center gap-2 text-muted-foreground hover:text-primary transition-colors">
                        <Share2 size={18} />
                      </button>
                    </div>
                    <button className="px-6 py-2 text-primary font-semibold hover:bg-primary/5 rounded-lg transition-colors">
                      Read More
                    </button>
                  </div>
                </article>
              ))}
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
