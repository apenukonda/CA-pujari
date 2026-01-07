"use client"

import { Navigation } from "@/components/navigation"
import { Footer } from "@/components/footer"
import { Mail, Linkedin, Youtube, Phone, MapPin } from "lucide-react"
import { motion } from "framer-motion"
import { fadeUp, stagger } from "@/lib/animations"

export default function ContactPage() {
  return (
    <>
      <Navigation />

      {/* HERO — HUMAN INVITE */}
      <section className="relative py-28 bg-gradient-to-br from-primary to-accent overflow-hidden">
        <motion.div
          initial={{ opacity: 0, y: 40 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          className="relative max-w-5xl mx-auto px-6 text-center"
        >
          <p className="uppercase tracking-widest text-primary-foreground/70 mb-4">
            Let’s Talk
          </p>
          <h1 className="text-5xl md:text-6xl font-extrabold text-primary-foreground mb-6">
            Get in Touch
          </h1>
          <p className="text-xl text-primary-foreground/85 max-w-2xl mx-auto">
            Questions, collaborations, or learning guidance — I’d love to hear from you.
          </p>
        </motion.div>
      </section>

      {/* CONTACT INFO — FLOATING TRUST */}
      <section className="py-24 bg-background">
        <motion.div
          variants={stagger}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true }}
          className="max-w-7xl mx-auto px-6 grid md:grid-cols-3 gap-10"
        >
          {[
            {
              icon: Mail,
              title: "Email",
              value: "shobha@tradingacademy.com",
            },
            {
              icon: Phone,
              title: "Phone",
              value: "+91 98765 43210",
            },
            {
              icon: MapPin,
              title: "Location",
              value: "Mumbai, India",
            },
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
                <h3 className="font-bold text-lg mb-2">{item.title}</h3>
                <p className="text-muted-foreground">{item.value}</p>
              </motion.div>
            )
          })}
        </motion.div>
      </section>

      {/* MESSAGE FORM — PERSONAL FEEL */}
      <section className="py-28 bg-muted">
        <motion.div
          initial={{ opacity: 0, y: 40 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.7 }}
          className="max-w-2xl mx-auto px-6"
        >
          <div className="rounded-3xl bg-background p-10 shadow-lg">
            <h2 className="text-3xl font-extrabold mb-4">
              Send a Message
            </h2>
            <p className="text-muted-foreground mb-10">
              I personally read every message and reply as soon as possible.
            </p>

            <form className="space-y-8">
              <div className="grid md:grid-cols-2 gap-6">
                <div>
                  <label className="text-sm font-semibold mb-2 block">
                    Full Name
                  </label>
                  <input
                    type="text"
                    placeholder="Your name"
                    className="w-full px-5 py-4 rounded-xl border border-border bg-background
                    focus:outline-none focus:ring-2 focus:ring-primary"
                  />
                </div>

                <div>
                  <label className="text-sm font-semibold mb-2 block">
                    Email
                  </label>
                  <input
                    type="email"
                    placeholder="you@example.com"
                    className="w-full px-5 py-4 rounded-xl border border-border bg-background
                    focus:outline-none focus:ring-2 focus:ring-primary"
                  />
                </div>
              </div>

              <div>
                <label className="text-sm font-semibold mb-2 block">
                  Subject
                </label>
                <input
                  type="text"
                  placeholder="What would you like to talk about?"
                  className="w-full px-5 py-4 rounded-xl border border-border bg-background
                  focus:outline-none focus:ring-2 focus:ring-primary"
                />
              </div>

              <div>
                <label className="text-sm font-semibold mb-2 block">
                  Message
                </label>
                <textarea
                  rows={6}
                  placeholder="Write your message here..."
                  className="w-full px-5 py-4 rounded-xl border border-border bg-background
                  resize-none focus:outline-none focus:ring-2 focus:ring-primary"
                />
              </div>

              <button
                type="submit"
                className="w-full py-4 bg-primary text-primary-foreground
                rounded-2xl font-semibold text-lg hover:shadow-2xl transition"
              >
                Send Message
              </button>
            </form>
          </div>
        </motion.div>
      </section>

      {/* NEWSLETTER — VALUE LED */}
      <section className="py-24 bg-background">
        <motion.div
          initial={{ opacity: 0, y: 40 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.7 }}
          className="max-w-2xl mx-auto px-6 text-center"
        >
          <h2 className="text-3xl font-extrabold mb-4">
            Weekly Market Insights
          </h2>
          <p className="text-muted-foreground mb-10">
            No spam. Just clarity, discipline, and real trading knowledge.
          </p>

          <div className="flex gap-4">
            <input
              type="email"
              placeholder="Enter your email"
              className="flex-1 px-5 py-4 rounded-xl border border-border
              focus:outline-none focus:ring-2 focus:ring-primary"
            />
            <button className="px-8 py-4 bg-primary text-primary-foreground
              rounded-xl font-semibold hover:shadow-xl transition">
              Subscribe
            </button>
          </div>
        </motion.div>
      </section>

      {/* SOCIAL — CREATOR PRESENCE */}
      <section className="py-20 bg-muted">
        <motion.div
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          className="max-w-4xl mx-auto px-6 text-center"
        >
          <h2 className="text-2xl font-bold mb-10">
            Connect With Me
          </h2>

          <div className="flex justify-center gap-8">
            {[
              { icon: Linkedin, link: "https://linkedin.com" },
              { icon: Youtube, link: "https://youtube.com" },
              { icon: Mail, link: "mailto:shobha@tradingacademy.com" },
            ].map((item, i) => {
              const Icon = item.icon
              return (
                <motion.a
                  key={i}
                  href={item.link}
                  whileHover={{ scale: 1.15 }}
                  className="w-14 h-14 bg-primary text-primary-foreground
                  rounded-full flex items-center justify-center shadow-lg"
                >
                  <Icon size={24} />
                </motion.a>
              )
            })}
          </div>
        </motion.div>
      </section>

      <Footer />
    </>
  )
}
