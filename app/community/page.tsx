import { Navigation } from "@/components/navigation"
import { Footer } from "@/components/footer"
import { Suspense } from "react"
import CommunityContent from "@/components/community-content"

export default function CommunityPage() {
  return (
    <>
      <Navigation />

      {/* Header Section */}
      <section className="py-16 bg-gradient-to-r from-primary to-accent">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h1 className="text-4xl md:text-5xl font-bold text-primary-foreground mb-4">Trading Community</h1>
          <p className="text-xl text-primary-foreground/90 max-w-2xl mx-auto">
            Learn, share, and grow with thousands of traders. Ask questions and share your experiences.
          </p>
        </div>
      </section>

      {/* Main Content */}
      <Suspense fallback={<div className="h-96" />}>
        <CommunityContent />
      </Suspense>

      <Footer />
    </>
  )
}
