"use client"

import { Navigation } from "@/components/navigation"
import { Footer } from "@/components/footer"
import Link from "next/link"
import { Clock, Users, ArrowRight, Book } from "lucide-react"
import { motion } from "framer-motion"
import { fadeUp, stagger } from "@/lib/animations"

export default function CoursesPage() {
  const courses = [
    {
      id: 1,
      title: "Trading Fundamentals",
      description:
        "Learn the foundations of stock market trading with clarity and confidence.",
      duration: "4 weeks",
      students: "2,500+",
      price: "₹4,999",
      level: "Beginner",
      modules: 12,
    },
    {
      id: 2,
      title: "Technical Analysis Mastery",
      description:
        "Read charts like a professional using proven technical frameworks.",
      duration: "6 weeks",
      students: "1,800+",
      price: "₹7,999",
      level: "Beginner",
      modules: 18,
    },
    {
      id: 3,
      title: "Risk Management & Position Sizing",
      description:
        "Protect your capital and trade with discipline, not emotion.",
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
        "Understand fear, greed, and mindset — the real edge in trading.",
      duration: "4 weeks",
      students: "950+",
      price: "₹5,999",
      level: "Beginner",
      modules: 10,
    },
    {
      id: 5,
      title: "Day Trading Strategies",
      description:
        "Intraday frameworks designed for real-time market conditions.",
      duration: "5 weeks",
      students: "1,400+",
      price: "₹6,999",
      level: "Beginner",
      modules: 15,
    },
    {
      id: 6,
      title: "Option Trading Basics",
      description:
        "Understand options without confusion — calls, puts, and basics.",
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

      {/* HERO — LEARNING PATH INTRO */}
      <section className="relative py-28 bg-gradient-to-br from-primary to-accent overflow-hidden">
        <motion.div
          initial={{ opacity: 0, y: 40 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          className="relative max-w-5xl mx-auto px-6 text-center"
        >
          <p className="uppercase tracking-widest text-primary-foreground/70 mb-4">
            Structured • Beginner-First • Practical
          </p>
          <h1 className="text-5xl md:text-6xl font-extrabold text-primary-foreground mb-6">
            Trading Courses
          </h1>
          <p className="text-xl text-primary-foreground/85 max-w-2xl mx-auto">
            Learn trading step-by-step with discipline, clarity, and confidence.
          </p>
        </motion.div>
      </section>

      {/* COURSES GRID */}
      <section className="py-28 bg-background">
        <motion.div
          variants={stagger}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true }}
          className="max-w-7xl mx-auto px-6"
        >
          <motion.h2
            variants={fadeUp}
            className="text-4xl font-bold mb-16"
          >
            Choose Your Learning Path
          </motion.h2>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-10">
            {courses.map((course) => (
              <motion.div
                key={course.id}
                variants={fadeUp}
                whileHover={{ y: -10 }}
                className="rounded-3xl bg-card shadow-md hover:shadow-2xl transition overflow-hidden"
              >
                <div className="p-8 flex flex-col h-full">
                  {/* LEVEL TAG */}
                  <span className="inline-block px-4 py-1 mb-6 text-xs font-semibold
                    rounded-full bg-accent/10 text-accent w-fit">
                    {course.level}
                  </span>

                  {/* TITLE */}
                  <h3 className="text-2xl font-bold mb-4 leading-snug">
                    {course.title}
                  </h3>

                  {/* DESCRIPTION */}
                  <p className="text-muted-foreground mb-8">
                    {course.description}
                  </p>

                  {/* META */}
                  <div className="space-y-4 text-sm text-muted-foreground mb-10">
                    <div className="flex items-center gap-3">
                      <Clock size={16} /> {course.duration}
                    </div>
                    <div className="flex items-center gap-3">
                      <Book size={16} /> {course.modules} modules
                    </div>
                    <div className="flex items-center gap-3">
                      <Users size={16} /> {course.students} learners
                    </div>
                  </div>

                  {/* FOOTER */}
                  <div className="mt-auto pt-6 border-t flex items-center justify-between">
                    <div>
                      <p className="text-xs text-muted-foreground">Price</p>
                      <p className="text-3xl font-extrabold text-primary">
                        {course.price}
                      </p>
                    </div>

                    {/* ✅ SAME ENROLL LOGIC */}
                    <Link
                      href={`/signup?course=${course.id}`}
                      className="group px-6 py-3 bg-primary text-primary-foreground
                      rounded-xl font-semibold flex items-center gap-2
                      hover:shadow-xl transition"
                    >
                      Enroll
                      <ArrowRight
                        size={16}
                        className="group-hover:translate-x-1 transition"
                      />
                    </Link>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        </motion.div>
      </section>

      {/* CTA — GUIDED DECISION */}
      <section className="py-24 bg-muted">
        <motion.div
          initial={{ opacity: 0, y: 40 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.7 }}
          className="max-w-4xl mx-auto px-6 text-center"
        >
          <h2 className="text-4xl font-extrabold mb-6">
            Not Sure Where to Start?
          </h2>
          <p className="text-lg text-muted-foreground mb-10">
            Start with fundamentals and build your skills the right way — no shortcuts.
          </p>

          <Link
            href="/webinars"
            className="inline-block px-10 py-4 bg-primary text-primary-foreground
            rounded-2xl font-semibold text-lg hover:shadow-2xl transition"
          >
            Join a Free Webinar
          </Link>
        </motion.div>
      </section>

      <Footer />
    </>
  )
}
