import { Navigation } from "@/components/navigation"
import { Footer } from "@/components/footer"
import Link from "next/link"
import { Clock, Users, ArrowRight, Book } from "lucide-react"

export default function CoursesPage() {
  const courses = [
    {
      id: 1,
      title: "Trading Fundamentals",
      description:
        "Learn the basics of stock market trading, different order types, and fundamental analysis techniques.",
      duration: "4 weeks",
      students: "2,500+",
      price: "₹4,999",
      level: "Beginner",
      modules: 12,
    },
    {
      id: 2,
      title: "Technical Analysis Mastery",
      description: "Deep dive into candlestick patterns, support & resistance levels, and chart analysis strategies.",
      duration: "6 weeks",
      students: "1,800+",
      price: "₹7,999",
      level: "Beginner",
      modules: 18,
    },
    {
      id: 3,
      title: "Risk Management & Position Sizing",
      description: "Master the art of protecting your capital with proper position sizing and stop-loss strategies.",
      duration: "3 weeks",
      students: "1,200+",
      price: "₹3,999",
      level: "Beginner",
      modules: 8,
    },
    {
      id: 4,
      title: "Market Psychology",
      description:
        "Understand the psychological aspects of trading and overcome fear, greed, and other emotional pitfalls.",
      duration: "4 weeks",
      students: "950+",
      price: "₹5,999",
      level: "Beginner",
      modules: 10,
    },
    {
      id: 5,
      title: "Day Trading Strategies",
      description: "Learn proven day trading techniques, intraday patterns, and real-time decision-making frameworks.",
      duration: "5 weeks",
      students: "1,400+",
      price: "₹6,999",
      level: "Beginner",
      modules: 15,
    },
    {
      id: 6,
      title: "Option Trading Basics",
      description: "Introduction to options trading, understanding calls and puts, and basic option strategies.",
      duration: "6 weeks",
      students: "850+",
      price: "₹8,999",
      level: "Beginner",
      modules: 16,
    },
  ]

  return (
    <>
      <Navigation />

      {/* Header Section */}
      <section className="py-16 bg-gradient-to-r from-primary to-accent">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h1 className="text-4xl md:text-5xl font-bold text-primary-foreground mb-4">Trading Courses</h1>
          <p className="text-xl text-primary-foreground/90 max-w-2xl mx-auto">
            Comprehensive, beginner-friendly courses designed to make you a confident trader
          </p>
        </div>
      </section>

      {/* Courses Grid */}
      <section className="py-16 bg-background">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {courses.map((course) => (
              <div
                key={course.id}
                className="bg-card rounded-xl border border-border overflow-hidden hover:shadow-lg transition-shadow"
              >
                <div className="p-6">
                  <div className="inline-block px-3 py-1 bg-accent/10 text-accent text-xs font-semibold rounded-full mb-4">
                    {course.level}
                  </div>
                  <h3 className="text-xl font-bold text-foreground mb-3">{course.title}</h3>
                  <p className="text-muted-foreground mb-6 text-sm leading-relaxed">{course.description}</p>

                  <div className="space-y-3 mb-6">
                    <div className="flex items-center gap-2 text-sm text-muted-foreground">
                      <Clock size={16} />
                      <span>{course.duration}</span>
                    </div>
                    <div className="flex items-center gap-2 text-sm text-muted-foreground">
                      <Book size={16} />
                      <span>{course.modules} modules</span>
                    </div>
                    <div className="flex items-center gap-2 text-sm text-muted-foreground">
                      <Users size={16} />
                      <span>{course.students} enrolled</span>
                    </div>
                  </div>

                  <div className="border-t border-border pt-6 flex items-center justify-between">
                    <div>
                      <p className="text-xs text-muted-foreground mb-1">Price</p>
                      <p className="text-2xl font-bold text-primary">{course.price}</p>
                    </div>
                    <Link
                      href={`/courses/${course.id}`}
                      className="px-6 py-2 bg-primary text-primary-foreground rounded-lg hover:opacity-90 transition-opacity font-semibold inline-flex items-center gap-2"
                    >
                      Enroll <ArrowRight size={16} />
                    </Link>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* FAQ Section */}
      <section className="py-16 bg-muted">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <h2 className="text-3xl font-bold text-foreground mb-12 text-center">Frequently Asked Questions</h2>
          <div className="space-y-4">
            {[
              {
                q: "Are these courses suitable for complete beginners?",
                a: "All our courses are designed specifically for beginners with no prior trading experience.",
              },
              {
                q: "What is the refund policy?",
                a: "We offer a 30-day money-back guarantee if you're not satisfied with the course content.",
              },
              {
                q: "Do I get lifetime access?",
                a: "Yes, once enrolled, you have lifetime access to all course materials and future updates.",
              },
              {
                q: "Can I access the courses on mobile?",
                a: "Yes, all courses are fully responsive and can be accessed on smartphones, tablets, and desktops.",
              },
            ].map((faq, index) => (
              <details key={index} className="bg-background rounded-lg border border-border p-6">
                <summary className="font-semibold text-foreground cursor-pointer">{faq.q}</summary>
                <p className="text-muted-foreground mt-4">{faq.a}</p>
              </details>
            ))}
          </div>
        </div>
      </section>

      <Footer />
    </>
  )
}
