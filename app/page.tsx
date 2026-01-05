"use client"

import { useEffect, useState } from "react"
import { Navigation } from "@/components/navigation"
import { Footer } from "@/components/footer"
import Link from "next/link"
import { Star, Users, TrendingUp, ArrowRight } from "lucide-react"
import { motion } from "framer-motion"
import { fadeUp, stagger } from "@/lib/animations"

export default function Home() {
  const words = ["Learn", "Practice", "Trade Confidently"]
  const [index, setIndex] = useState(0)

  useEffect(() => {
    const interval = setInterval(() => {
      setIndex((prev) => (prev + 1) % words.length)
    }, 2000)
    return () => clearInterval(interval)
  }, [])

  const highlights = [
    { icon: Users, stat: "5000+", label: "Students Trained" },
    { icon: TrendingUp, stat: "15+", label: "Years Experience" },
    { icon: Star, stat: "4.9/5", label: "Average Rating" },
  ]

  return (
    <>
      <Navigation />

      {/* HERO */}
      <section className="relative overflow-hidden py-20 md:py-32
        bg-gradient-to-br from-blue-50 via-background to-indigo-100
        dark:from-neutral-900 dark:via-neutral-950 dark:to-black">

        <div className="absolute inset-0
          dark:bg-[radial-gradient(circle_at_top,rgba(59,130,246,0.15),transparent_40%)]" />

        <div className="relative max-w-7xl mx-auto px-4 grid grid-cols-1 md:grid-cols-2 gap-12 items-center">

          {/* TEXT */}
          <motion.div initial="hidden" animate="visible" variants={stagger}>
            <motion.h1
              variants={fadeUp}
              className="text-5xl md:text-6xl font-extrabold mb-6 leading-tight"
            >
              <span className="text-primary">{words[index]}</span>
              <br />
              Trading with Confidence
            </motion.h1>

            <motion.p
              variants={fadeUp}
              className="text-xl text-muted-foreground mb-8"
            >
              Learn trading from a Chartered Accountant who simplifies
              the market for absolute beginners across India.
            </motion.p>

            <motion.div
              variants={fadeUp}
              className="flex gap-4 flex-wrap"
            >
              <Link
                href="/courses"
                className="px-8 py-3 bg-primary text-primary-foreground rounded-lg
                shadow-lg hover:shadow-xl hover:scale-105
                transition-all duration-300 font-semibold flex items-center gap-2"
              >
                View Courses <ArrowRight size={18} />
              </Link>

              <Link
                href="/webinars"
                className="px-8 py-3 border-2 border-primary text-primary rounded-lg
                hover:bg-primary hover:text-primary-foreground transition-all duration-300 font-semibold"
              >
                Upcoming Webinars
              </Link>
            </motion.div>
          </motion.div>

          {/* IMAGE */}
          <motion.div
            initial={{ scale: 1.1, opacity: 0 }}
            whileInView={{ scale: 1, opacity: 1 }}
            viewport={{ once: true }}
            transition={{ duration: 1 }}
            className="relative h-96 rounded-2xl overflow-hidden shadow-2xl border"
          >
            <img
              src="/professional-woman-chartered-accountant-trading-ed.jpg"
              alt="Shobha Pujari"
              className="w-full h-full object-cover"
            />

            {/* FLOATING METRICS */}
            <motion.div
              animate={{ y: [0, -10, 0] }}
              transition={{ repeat: Infinity, duration: 3 }}
              className="absolute top-6 left-6 bg-background/80 backdrop-blur
              px-4 py-2 rounded-lg shadow text-sm font-semibold"
            >
              ⭐ 4.9 Rating
            </motion.div>

            <motion.div
              animate={{ y: [0, 10, 0] }}
              transition={{ repeat: Infinity, duration: 4 }}
              className="absolute bottom-6 right-6 bg-background/80 backdrop-blur
              px-4 py-2 rounded-lg shadow text-sm font-semibold"
            >
              👥 5000+ Students
            </motion.div>
          </motion.div>
        </div>
      </section>

      {/* HIGHLIGHTS */}
      <section className="py-20 bg-background">
        <motion.div
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true }}
          variants={stagger}
          className="max-w-7xl mx-auto px-4 grid grid-cols-1 md:grid-cols-3 gap-8"
        >
          {highlights.map((item, i) => {
            const Icon = item.icon
            return (
              <motion.div
                key={i}
                variants={fadeUp}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className="text-center p-8 rounded-xl bg-card border shadow-md"
              >
                <div className="flex justify-center mb-4">
                  <Icon size={32} className="text-accent" />
                </div>
                <div className="text-4xl font-bold text-primary mb-2">
                  {item.stat}
                </div>
                <div className="text-muted-foreground font-medium">
                  {item.label}
                </div>
              </motion.div>
            )
          })}
        </motion.div>
      </section>

      {/* WHY I TEACH */}
      <section className="py-20 bg-background">
        <motion.div
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true }}
          variants={fadeUp}
          className="max-w-3xl mx-auto text-center"
        >
          <h2 className="text-3xl font-bold mb-6">
            Why I Teach Trading
          </h2>
          <p className="text-lg text-muted-foreground leading-relaxed">
            I’ve seen beginners lose money not because trading is difficult,
            but because the basics were never explained properly.
            My goal is to simplify learning, remove fear,
            and help you trade with confidence.
          </p>
        </motion.div>
      </section>

      {/* CTA */}
      <motion.section
        initial={{ opacity: 0 }}
        whileInView={{ opacity: 1 }}
        viewport={{ once: true }}
        className="py-20 bg-gradient-to-r from-primary to-accent text-white text-center"
      >
        <h2 className="text-4xl font-bold mb-6">
          Let’s Build Your Trading Confidence
        </h2>
        <p className="text-lg opacity-90 mb-8">
          Start learning today with structured, beginner-friendly guidance.
        </p>
        <Link
          href="/courses"
          className="inline-block px-10 py-4 bg-white text-primary rounded-xl
          font-bold text-lg hover:scale-105 transition-transform"
        >
          Explore Courses →
        </Link>
      </motion.section>

      <Footer />
    </>
  )
}
