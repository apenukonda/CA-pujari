import { Navigation } from "@/components/navigation"
import { Footer } from "@/components/footer"
import { Mail, Linkedin, Youtube, Phone, MapPin } from "lucide-react"

export default function ContactPage() {
  return (
    <>
      <Navigation />

      {/* Header Section */}
      <section className="py-16 bg-gradient-to-r from-primary to-accent">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h1 className="text-4xl md:text-5xl font-bold text-primary-foreground mb-4">Get in Touch</h1>
          <p className="text-xl text-primary-foreground/90 max-w-2xl mx-auto">
            Have questions? Want to collaborate? Reach out and let's connect.
          </p>
        </div>
      </section>

      {/* Contact Content */}
      <section className="py-16 bg-background">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-16">
            {/* Contact Info Cards */}
            <div className="bg-card p-8 rounded-xl border border-border text-center">
              <Mail className="text-accent mx-auto mb-4" size={32} />
              <h3 className="font-bold text-foreground mb-2">Email</h3>
              <p className="text-muted-foreground">shobha@tradingacademy.com</p>
            </div>
            <div className="bg-card p-8 rounded-xl border border-border text-center">
              <Phone className="text-accent mx-auto mb-4" size={32} />
              <h3 className="font-bold text-foreground mb-2">Phone</h3>
              <p className="text-muted-foreground">+91 98765 43210</p>
            </div>
            <div className="bg-card p-8 rounded-xl border border-border text-center">
              <MapPin className="text-accent mx-auto mb-4" size={32} />
              <h3 className="font-bold text-foreground mb-2">Location</h3>
              <p className="text-muted-foreground">Mumbai, India</p>
            </div>
          </div>

          {/* Contact Form */}
          <div className="max-w-2xl mx-auto bg-card p-8 rounded-xl border border-border">
            <h2 className="text-2xl font-bold text-foreground mb-6">Send me a Message</h2>
            <form className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-semibold text-foreground mb-2">Full Name</label>
                  <input
                    type="text"
                    placeholder="Your name"
                    className="w-full px-4 py-3 rounded-lg border border-border bg-background text-foreground placeholder-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary"
                  />
                </div>
                <div>
                  <label className="block text-sm font-semibold text-foreground mb-2">Email</label>
                  <input
                    type="email"
                    placeholder="your@email.com"
                    className="w-full px-4 py-3 rounded-lg border border-border bg-background text-foreground placeholder-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary"
                  />
                </div>
              </div>
              <div>
                <label className="block text-sm font-semibold text-foreground mb-2">Subject</label>
                <input
                  type="text"
                  placeholder="What is this about?"
                  className="w-full px-4 py-3 rounded-lg border border-border bg-background text-foreground placeholder-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary"
                />
              </div>
              <div>
                <label className="block text-sm font-semibold text-foreground mb-2">Message</label>
                <textarea
                  placeholder="Your message here..."
                  rows={6}
                  className="w-full px-4 py-3 rounded-lg border border-border bg-background text-foreground placeholder-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary resize-none"
                ></textarea>
              </div>
              <button
                type="submit"
                className="w-full px-6 py-3 bg-primary text-primary-foreground rounded-lg hover:opacity-90 transition-opacity font-semibold text-lg"
              >
                Send Message
              </button>
            </form>
          </div>
        </div>
      </section>

      {/* Newsletter Section */}
      <section className="py-16 bg-muted">
        <div className="max-w-2xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-3xl font-bold text-foreground mb-4">Subscribe to Newsletter</h2>
          <p className="text-muted-foreground mb-8">
            Get weekly tips, market insights, and exclusive trading strategies delivered to your inbox.
          </p>
          <div className="flex gap-3">
            <input
              type="email"
              placeholder="Enter your email"
              className="flex-1 px-4 py-3 rounded-lg border border-border bg-background text-foreground placeholder-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary"
            />
            <button className="px-8 py-3 bg-primary text-primary-foreground rounded-lg hover:opacity-90 transition-opacity font-semibold">
              Subscribe
            </button>
          </div>
        </div>
      </section>

      {/* Social Media Section */}
      <section className="py-16 bg-background">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-2xl font-bold text-foreground mb-8">Follow Me</h2>
          <div className="flex justify-center gap-6">
            <a
              href="https://linkedin.com"
              className="w-12 h-12 bg-primary text-primary-foreground rounded-full flex items-center justify-center hover:opacity-90 transition-opacity"
            >
              <Linkedin size={24} />
            </a>
            <a
              href="https://youtube.com"
              className="w-12 h-12 bg-primary text-primary-foreground rounded-full flex items-center justify-center hover:opacity-90 transition-opacity"
            >
              <Youtube size={24} />
            </a>
            <a
              href="mailto:shobha@tradingacademy.com"
              className="w-12 h-12 bg-primary text-primary-foreground rounded-full flex items-center justify-center hover:opacity-90 transition-opacity"
            >
              <Mail size={24} />
            </a>
          </div>
        </div>
      </section>

      <Footer />
    </>
  )
}
