"use client"

import { useEffect, useState } from "react"
import { Navigation } from "@/components/navigation"
import { Footer } from "@/components/footer"
import Link from "next/link"
import { Star, Users, TrendingUp, ArrowRight } from "lucide-react"
import { motion } from "framer-motion"
import { fadeUp, stagger } from "@/lib/animations"

export default function Home() {
  const words = ["Learn", "Practice", "Trade"]
  const [index, setIndex] = useState(0)

  useEffect(() => {
    const interval = setInterval(() => {
      setIndex((prev) => (prev + 1) % words.length)
    }, 1800)
    return () => clearInterval(interval)
  }, [])

  return (
    <>
      <Navigation />

      {/* HERO — CREATOR FIRST */}
      <section className="relative min-h-[95vh] flex items-center bg-gradient-to-br
        from-blue-50 via-background to-indigo-100
        dark:from-neutral-900 dark:via-neutral-950 dark:to-black overflow-hidden">

        <div className="absolute inset-0 dark:bg-[radial-gradient(circle_at_top,rgba(59,130,246,0.18),transparent_45%)]" />

        <div className="relative max-w-7xl mx-auto px-6 grid md:grid-cols-2 gap-20 items-center">

          {/* TEXT */}
          <motion.div
            variants={stagger}
            initial="hidden"
            animate="visible"
          >
            <motion.p
              variants={fadeUp}
              className="uppercase tracking-widest text-sm text-muted-foreground mb-4"
            >
              Chartered Accountant • Trading Educator
            </motion.p>

            <motion.h1
              variants={fadeUp}
              className="text-6xl md:text-7xl font-extrabold leading-tight mb-8"
            >
              <span className="text-primary">
                {words[index]}
              </span>{" "}
              the Markets
              <br />
              with Confidence
            </motion.h1>

            <motion.p
              variants={fadeUp}
              className="text-xl text-muted-foreground max-w-xl mb-10"
            >
              Structured trading education designed for beginners —
              no noise, no hype, just clarity and confidence.
            </motion.p>

            <motion.div variants={fadeUp} className="flex gap-5 flex-wrap">
              <Link
                href="/courses"
                className="group px-8 py-4 bg-primary text-primary-foreground rounded-xl
                font-semibold flex items-center gap-2
                hover:shadow-2xl transition"
              >
                Start Learning
                <ArrowRight className="group-hover:translate-x-1 transition" />
              </Link>

              <Link
                href="/webinars"
                className="px-8 py-4 rounded-xl border border-primary
                text-primary font-semibold hover:bg-primary hover:text-primary-foreground transition"
              >
                Free Webinars
              </Link>
            </motion.div>
          </motion.div>

          {/* IMAGE + FLOATING TRUST */}
          <motion.div
            initial={{ opacity: 0, y: 40 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.9 }}
            className="relative"
          >
            <div className="absolute -inset-6 bg-primary/20 blur-3xl rounded-full" />

            <img
              src="/professional-woman-chartered-accountant-trading-ed.jpg"
              alt="Shobha Pujari"
              className="relative h-[460px] w-full object-cover rounded-3xl shadow-2xl"
            />

            <motion.div
              animate={{ y: [0, -12, 0] }}
              transition={{ repeat: Infinity, duration: 3 }}
              className="absolute top-6 left-6 bg-background/80 backdrop-blur
              px-5 py-3 rounded-xl shadow-lg text-sm font-semibold"
            >
              ⭐ 4.9 Rating
            </motion.div>

            <motion.div
              animate={{ y: [0, 12, 0] }}
              transition={{ repeat: Infinity, duration: 4 }}
              className="absolute bottom-6 right-6 bg-background/80 backdrop-blur
              px-5 py-3 rounded-xl shadow-lg text-sm font-semibold"
            >
              👥 5000+ Students
            </motion.div>
          </motion.div>
        </div>
      </section>

      {/* TRUST SIGNALS */}
      <section className="py-24 bg-background">
        <motion.div
          variants={stagger}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true }}
          className="max-w-6xl mx-auto px-6 grid md:grid-cols-3 gap-10"
        >
          {[
            { icon: Users, stat: "5000+", label: "Students Trained" },
            { icon: TrendingUp, stat: "15+", label: "Years Experience" },
            { icon: Star, stat: "4.9/5", label: "Avg Student Rating" },
          ].map((item, i) => {
            const Icon = item.icon
            return (
              <motion.div
                key={i}
                variants={fadeUp}
                whileHover={{ y: -10 }}
                className="rounded-3xl bg-card p-10 text-center shadow-md hover:shadow-2xl transition"
              >
                <Icon className="mx-auto mb-6 text-accent" size={36} />
                <div className="text-5xl font-extrabold text-primary mb-3">
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

      {/* TESTIMONIALS — SOCIAL PROOF */}
      <section className="py-28 bg-muted">
        <motion.div
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true }}
          variants={stagger}
          className="max-w-7xl mx-auto px-6"
        >
          <motion.h2
            variants={fadeUp}
            className="text-4xl font-bold text-center mb-6"
          >
            Learners, Not Just Students
          </motion.h2>

          <motion.p
            variants={fadeUp}
            className="text-center text-muted-foreground mb-16"
          >
            Real people. Real progress. Real confidence.
          </motion.p>

          <div className="grid md:grid-cols-3 gap-10">
            {[
              {
                name: "Rajesh Kumar",
                role: "Investment Professional",
                text: "Clear frameworks and honest teaching. This changed how I see markets.",
                initials: "RK",
              },
              {
                name: "Priya Sharma",
                role: "Beginner Trader",
                text: "No fear anymore. I finally understand what I’m doing.",
                initials: "PS",
              },
              {
                name: "Amit Patel",
                role: "Business Owner",
                text: "Structured, practical, and grounded in reality.",
                initials: "AP",
              },
            ].map((t, i) => (
              <motion.div
                key={i}
                variants={fadeUp}
                className="rounded-3xl bg-background p-10 shadow-lg"
              >
                <div className="flex gap-1 mb-5">
                  {[...Array(5)].map((_, i) => (
                    <Star key={i} size={16} className="fill-accent text-accent" />
                  ))}
                </div>

                <p className="text-muted-foreground mb-8 leading-relaxed">
                  “{t.text}”
                </p>

                <div className="flex items-center gap-4">
                  <div className="w-12 h-12 rounded-full bg-accent text-accent-foreground
                  flex items-center justify-center font-bold">
                    {t.initials}
                  </div>
                  <div>
                    <p className="font-semibold">{t.name}</p>
                    <p className="text-sm text-muted-foreground">{t.role}</p>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        </motion.div>
      </section>

      {/* CTA — PERSONAL INVITE */}
      <section className="py-24 bg-background">
        <motion.div
          initial={{ opacity: 0, y: 40 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.7 }}
          className="max-w-4xl mx-auto px-6 text-center"
        >
          <h2 className="text-4xl font-extrabold mb-6">
            Start Your Trading Journey the Right Way
          </h2>
          <p className="text-lg text-muted-foreground mb-10">
            Learn with structure, discipline, and clarity — not shortcuts.
          </p>

          <Link
            href="/courses"
            className="inline-block px-10 py-4 bg-primary text-primary-foreground
            rounded-2xl font-semibold text-lg hover:shadow-2xl transition"
          >
            Explore Courses
          </Link>
        </motion.div>
      </section>

      <Footer />
    </>
  )
}
