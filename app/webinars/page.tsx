import { Navigation } from "@/components/navigation"
import { Footer } from "@/components/footer"
import { Calendar, Clock, Users, Video, CreditCard } from "lucide-react"

export default function WebinarsPage() {
  const upcomingWebinars = [
    {
      id: 1,
      title: "Stock Market Basics for Beginners",
      date: "January 15, 2026",
      time: "7:00 PM IST",
      duration: "90 mins",
      platform: "Zoom",
      price: "Free",
      seats: "500",
      instructor: "Shobha Pujari",
    },
    {
      id: 2,
      title: "Candlestick Patterns That Actually Work",
      date: "January 22, 2026",
      time: "7:00 PM IST",
      duration: "120 mins",
      platform: "Google Meet",
      price: "₹299",
      seats: "300",
      instructor: "Shobha Pujari",
    },
    {
      id: 3,
      title: "Risk Management Strategies",
      date: "February 5, 2026",
      time: "6:30 PM IST",
      duration: "100 mins",
      platform: "Zoom",
      price: "₹499",
      seats: "400",
      instructor: "Shobha Pujari",
    },
    {
      id: 4,
      title: "Live Trading Session: Real Market Analysis",
      date: "February 12, 2026",
      time: "9:00 AM IST",
      duration: "150 mins",
      platform: "Zoom",
      price: "₹799",
      seats: "200",
      instructor: "Shobha Pujari",
    },
  ]

  const pastWebinars = [
    {
      id: 1,
      title: "Introduction to Options Trading",
      date: "January 8, 2026",
      instructor: "Shobha Pujari",
    },
    {
      id: 2,
      title: "Market Psychology 101",
      date: "December 28, 2025",
      instructor: "Shobha Pujari",
    },
    {
      id: 3,
      title: "Technical Analysis Deep Dive",
      date: "December 15, 2025",
      instructor: "Shobha Pujari",
    },
  ]

  return (
    <>
      <Navigation />

      {/* Header Section */}
      <section className="py-16 bg-gradient-to-r from-primary to-accent">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h1 className="text-4xl md:text-5xl font-bold text-primary-foreground mb-4">Live Webinars</h1>
          <p className="text-xl text-primary-foreground/90 max-w-2xl mx-auto">
            Join interactive sessions with expert traders and learn directly from Shobha Pujari
          </p>
        </div>
      </section>

      {/* Upcoming Webinars */}
      <section className="py-16 bg-background">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <h2 className="text-3xl font-bold text-foreground mb-12">Upcoming Webinars</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            {upcomingWebinars.map((webinar) => (
              <div key={webinar.id} className="bg-card rounded-xl border border-border overflow-hidden">
                <div className="p-6 space-y-4">
                  <h3 className="text-2xl font-bold text-foreground">{webinar.title}</h3>

                  <div className="space-y-3">
                    <div className="flex items-start gap-3">
                      <Calendar className="text-accent mt-1" size={20} />
                      <div>
                        <p className="text-sm text-muted-foreground">Date</p>
                        <p className="font-semibold text-foreground">{webinar.date}</p>
                      </div>
                    </div>

                    <div className="flex items-start gap-3">
                      <Clock className="text-accent mt-1" size={20} />
                      <div>
                        <p className="text-sm text-muted-foreground">Time & Duration</p>
                        <p className="font-semibold text-foreground">
                          {webinar.time} • {webinar.duration}
                        </p>
                      </div>
                    </div>

                    <div className="flex items-start gap-3">
                      <Video className="text-accent mt-1" size={20} />
                      <div>
                        <p className="text-sm text-muted-foreground">Platform</p>
                        <p className="font-semibold text-foreground">{webinar.platform}</p>
                      </div>
                    </div>

                    <div className="flex items-start gap-3">
                      <Users className="text-accent mt-1" size={20} />
                      <div>
                        <p className="text-sm text-muted-foreground">Available Seats</p>
                        <p className="font-semibold text-foreground">{webinar.seats}</p>
                      </div>
                    </div>
                  </div>

                  <div className="border-t border-border pt-4 flex items-center justify-between">
                    <div>
                      <p className="text-sm text-muted-foreground mb-1">Price</p>
                      <p className="text-2xl font-bold text-primary">{webinar.price}</p>
                    </div>
                    <button className="px-6 py-3 bg-primary text-primary-foreground rounded-lg hover:opacity-90 transition-opacity font-semibold flex items-center gap-2">
                      <CreditCard size={18} />
                      Book Seat
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Payment Methods */}
      <section className="py-16 bg-muted">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <h2 className="text-3xl font-bold text-foreground mb-12 text-center">Payment Methods</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
            {["UPI", "Razorpay", "Paytm", "Credit/Debit Card"].map((method) => (
              <div key={method} className="bg-background p-6 rounded-lg border border-border text-center">
                <p className="font-semibold text-foreground">{method}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Past Webinars */}
      <section className="py-16 bg-background">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <h2 className="text-3xl font-bold text-foreground mb-12">Recorded Sessions</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {pastWebinars.map((webinar) => (
              <div key={webinar.id} className="bg-card rounded-xl border border-border overflow-hidden">
                <div className="h-48 bg-gradient-to-br from-primary to-accent flex items-center justify-center">
                  <Video size={48} className="text-primary-foreground opacity-50" />
                </div>
                <div className="p-6">
                  <h3 className="text-lg font-bold text-foreground mb-3">{webinar.title}</h3>
                  <p className="text-sm text-muted-foreground mb-4">{webinar.date}</p>
                  <button className="w-full px-4 py-2 border-2 border-primary text-primary rounded-lg hover:bg-primary/5 transition-colors font-semibold">
                    Watch Recording
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      <Footer />
    </>
  )
}
