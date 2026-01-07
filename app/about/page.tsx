"use client"

import { Navigation } from "@/components/navigation"
import { Footer } from "@/components/footer"
import { Award, BookOpen, Users, Lightbulb } from "lucide-react"
import { motion } from "framer-motion"

const fadeUp = {
  hidden: { opacity: 0, y: 40 },
  visible: { opacity: 1, y: 0 },
}

const stagger = {
  visible: {
    transition: {
      staggerChildren: 0.15,
    },
  },
}

export default function AboutPage() {
  return (
    <>
      <Navigation />

      {/* HERO – PERSONAL BRAND INTRO */}
      <section className="relative min-h-[90vh] flex items-center justify-center bg-gradient-to-br from-primary to-accent overflow-hidden">
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.8, ease: "easeOut" }}
          className="text-center px-6"
        >
          <p className="uppercase tracking-widest text-primary-foreground/70 mb-4">
            Educator • CA • Trader
          </p>
          <h1 className="text-6xl md:text-7xl font-extrabold tracking-tight text-primary-foreground">
            Shobha Pujari
          </h1>
          <p className="mt-6 text-xl max-w-xl mx-auto text-primary-foreground/85">
            Making trading understandable, practical, and human for beginners.
          </p>
        </motion.div>
      </section>

      {/* STORY SECTION – NOT A BORING BIO */}
      <section className="py-28 bg-background">
        <motion.div
          variants={stagger}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true }}
          className="max-w-5xl mx-auto px-6 grid md:grid-cols-2 gap-16 items-center"
        >
          <motion.div variants={fadeUp}>
            <h2 className="text-4xl font-bold mb-6">
              I Didn’t Start as a Teacher.
            </h2>
            <p className="text-muted-foreground leading-relaxed mb-5">
              I started deep inside finance — audits, numbers, risk, regulations.
              Fifteen years as a Chartered Accountant taught me how markets truly work.
            </p>
            <p className="text-muted-foreground leading-relaxed">
              But beginners were struggling. So I shifted focus — not to predict markets,
              but to **teach people how to think inside them**.
            </p>
          </motion.div>

          <motion.div
            variants={fadeUp}
            whileHover={{ scale: 1.03 }}
            className="relative"
          >
            <div className="absolute inset-0 bg-accent/20 blur-2xl rounded-3xl" />
            <img
              src="/professional-woman-chartered-accountant-trading-ed.jpg"
              alt="Shobha Pujari"
              className="relative rounded-3xl object-cover h-[420px] w-full"
            />
          </motion.div>
        </motion.div>
      </section>

      {/* CREDENTIALS – FLOATING CARDS */}
      <section className="py-24 bg-muted">
        <motion.div
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true }}
          variants={stagger}
          className="max-w-6xl mx-auto px-6"
        >
          <motion.h2
            variants={fadeUp}
            className="text-4xl font-bold text-center mb-16"
          >
            Built on Real Credibility
          </motion.h2>

          <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-8">
            {[
              "Chartered Accountant (CA)",
              "Trading Certification",
              "15+ Years Experience",
              "5,000+ Students Trained",
            ].map((item, i) => (
              <motion.div
                key={i}
                variants={fadeUp}
                whileHover={{ y: -10 }}
                className="rounded-2xl bg-background p-8 text-center shadow-sm hover:shadow-xl transition"
              >
                <Award className="mx-auto mb-5 text-accent" size={34} />
                <p className="font-semibold">{item}</p>
              </motion.div>
            ))}
          </div>
        </motion.div>
      </section>

      {/* TEACHING STYLE – GEN Z FRIENDLY */}
      <section className="py-28 bg-background">
        <motion.div
          variants={stagger}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true }}
          className="max-w-6xl mx-auto px-6"
        >
          <motion.h2
            variants={fadeUp}
            className="text-4xl font-bold text-center mb-20"
          >
            How I Teach Differently
          </motion.h2>

          <div className="grid md:grid-cols-2 gap-10">
            {[
              {
                icon: Lightbulb,
                title: "No Overcomplication",
                text: "Clear frameworks instead of confusing indicators.",
              },
              {
                icon: BookOpen,
                title: "Market Reality",
                text: "Live charts, real mistakes, real learning.",
              },
              {
                icon: Users,
                title: "Community First",
                text: "Trading feels lonely. Learning shouldn’t.",
              },
              {
                icon: Award,
                title: "Progress Tracking",
                text: "You always know where you stand.",
              },
            ].map((item, i) => {
              const Icon = item.icon
              return (
                <motion.div
                  key={i}
                  variants={fadeUp}
                  whileHover={{ scale: 1.04 }}
                  className="rounded-3xl bg-card p-10 shadow-md hover:shadow-2xl transition"
                >
                  <Icon className="text-accent mb-6" size={36} />
                  <h3 className="text-2xl font-semibold mb-4">
                    {item.title}
                  </h3>
                  <p className="text-muted-foreground">{item.text}</p>
                </motion.div>
              )
            })}
          </div>
        </motion.div>
      </section>

      {/* TRUST – SOCIAL PROOF FEEL */}
      <section className="py-24 bg-muted">
        <motion.div
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true }}
          variants={stagger}
          className="max-w-4xl mx-auto px-6"
        >
          <motion.h2
            variants={fadeUp}
            className="text-4xl font-bold text-center mb-14"
          >
            Why Beginners Stay
          </motion.h2>

          <div className="space-y-6">
            {[
              "Beginner-first explanations",
              "Live doubt clearing, not just videos",
              "No fake profit screenshots",
              "CA-backed financial discipline",
              "Lifetime access & updates",
            ].map((item, i) => (
              <motion.div
                key={i}
                variants={fadeUp}
                className="bg-background rounded-xl p-6 shadow-sm"
              >
                ✓ {item}
              </motion.div>
            ))}
          </div>
        </motion.div>
      </section>

      <Footer />
    </>
  )
}
