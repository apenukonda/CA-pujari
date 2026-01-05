import { Navigation } from "@/components/navigation"
import { Footer } from "@/components/footer"
import { Award, BookOpen, Users, Lightbulb } from "lucide-react"

export default function AboutPage() {
  const credentials = [
    "Chartered Accountant (CA)",
    "Trading Certification",
    "Financial Analysis Expert",
    "15+ Years Experience",
  ]

  return (
    <>
      <Navigation />

      {/* Hero Section */}
      <section className="py-20 bg-gradient-to-r from-primary to-accent">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h1 className="text-4xl md:text-5xl font-bold text-primary-foreground mb-4">About Shobha Pujari</h1>
          <p className="text-xl text-primary-foreground/90 max-w-2xl mx-auto">
            Chartered Accountant & Trading Educator dedicated to demystifying financial markets for beginners
          </p>
        </div>
      </section>

      {/* Profile Section */}
      <section className="py-16 bg-background">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-12 items-center">
            <div>
              <h2 className="text-3xl font-bold text-foreground mb-6">Professional Journey</h2>
              <p className="text-muted-foreground mb-4 leading-relaxed">
                With over 15 years of experience as a Chartered Accountant, I've developed a deep understanding of
                financial markets and trading mechanics. My journey started as a financial professional, but I realized
                there was a massive gap in beginner-friendly trading education.
              </p>
              <p className="text-muted-foreground mb-4 leading-relaxed">
                This realization drove me to transition my career towards teaching. Today, I've trained over 5,000
                students across India, helping them transform from confused beginners to confident traders.
              </p>
              <p className="text-muted-foreground leading-relaxed">
                My teaching philosophy is simple: break down complex concepts into digestible lessons, provide
                real-world examples, and always prioritize practical knowledge over theory.
              </p>
            </div>
            <div className="relative h-96 bg-accent/20 rounded-2xl overflow-hidden">
              <img
                src="/professional-woman-chartered-accountant-trading-ed.jpg"
                alt="Shobha Pujari"
                className="w-full h-full object-cover"
              />
            </div>
          </div>
        </div>
      </section>

      {/* Credentials */}
      <section className="py-16 bg-muted">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <h2 className="text-3xl font-bold text-foreground mb-12 text-center">Qualifications & Achievements</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {credentials.map((credential, index) => (
              <div key={index} className="bg-background p-6 rounded-lg border border-border text-center">
                <Award className="text-accent mx-auto mb-3" size={32} />
                <p className="font-semibold text-foreground">{credential}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Teaching Philosophy */}
      <section className="py-16 bg-background">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <h2 className="text-3xl font-bold text-foreground mb-12 text-center">Teaching Philosophy</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            {[
              {
                icon: Lightbulb,
                title: "Simplicity First",
                description: "Complex concepts broken down into simple, actionable steps anyone can understand.",
              },
              {
                icon: BookOpen,
                title: "Practical Learning",
                description: "Real-world examples and live market analysis instead of theoretical knowledge.",
              },
              {
                icon: Users,
                title: "Community Support",
                description: "Learning is better together. Strong community for peer support and knowledge sharing.",
              },
              {
                icon: Award,
                title: "Accountability",
                description: "Transparent tracking of progress with regular feedback and personalized guidance.",
              },
            ].map((item, index) => {
              const Icon = item.icon
              return (
                <div key={index} className="bg-card p-8 rounded-lg border border-border">
                  <Icon className="text-accent mb-4" size={32} />
                  <h3 className="text-xl font-bold text-foreground mb-3">{item.title}</h3>
                  <p className="text-muted-foreground">{item.description}</p>
                </div>
              )
            })}
          </div>
        </div>
      </section>

      {/* Why Trust */}
      <section className="py-16 bg-muted">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <h2 className="text-3xl font-bold text-foreground mb-12 text-center">Why Beginners Trust Me</h2>
          <div className="space-y-6">
            {[
              "15+ years of professional experience in finance and trading",
              "Trained 5,000+ students with a 4.9/5 average rating",
              "CA qualification ensures deep understanding of financial regulations and accounting",
              "Beginner-focused approach - no jargon, only practical knowledge",
              "Live webinars and interactive Q&A sessions for real support",
              "Lifetime access to course materials and continuous updates",
            ].map((reason, index) => (
              <div key={index} className="flex gap-4 p-4 bg-background rounded-lg border border-border">
                <div className="text-primary text-2xl font-bold">✓</div>
                <p className="text-foreground leading-relaxed">{reason}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <Footer />
    </>
  )
}
