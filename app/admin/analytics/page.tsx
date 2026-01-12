"use client"

import { useEffect, useState } from "react"
import { Navigation } from "@/components/navigation"
import { Footer } from "@/components/footer"
import { db } from "@/lib/firebase"
import { collection, getDocs, query, orderBy, where } from "firebase/firestore"
import { format } from "date-fns"
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  Cell,
} from "recharts"

export default function AdminAnalyticsPage() {
  const [loading, setLoading] = useState(true)
  const [courses, setCourses] = useState<any[]>([])
  const [webinars, setWebinars] = useState<any[]>([])
  const [registrations, setRegistrations] = useState<any[]>([])

  useEffect(() => {
    async function loadAll() {
      setLoading(true)
      try {
        const [cSnap, wSnap, rSnap] = await Promise.all([
          getDocs(query(collection(db, "courses"), orderBy("createdAt", "desc"))),
          getDocs(query(collection(db, "webinars"), orderBy("createdAt", "desc"))),
          getDocs(collection(db, "registrations")),
        ])

        const c = cSnap.docs.map((d) => ({ id: d.id, ...d.data() }))
        const w = wSnap.docs.map((d) => ({ id: d.id, ...d.data() }))
        const r = rSnap.docs.map((d) => ({ id: d.id, ...d.data() }))

        setCourses(c)
        setWebinars(w)
        setRegistrations(r)
      } finally {
        setLoading(false)
      }
    }
    loadAll()
  }, [])

  // helpers to compute stats
  function computeCounts(type: "course" | "webinar") {
    const map = new Map<string, { count: number; last: number | null }>()
    registrations.forEach((reg) => {
      if (reg.type !== type) return
      const id = String(reg.itemId)
      const existing = map.get(id) || { count: 0, last: null }
      existing.count += 1
      const ts = reg.createdAt?.seconds ? reg.createdAt.seconds * 1000 : reg.createdAt ? new Date(reg.createdAt).getTime() : null
      if (ts && (!existing.last || ts > existing.last)) existing.last = ts
      map.set(id, existing)
    })
    return map
  }

  const courseCounts = computeCounts("course")
  const webinarCounts = computeCounts("webinar")

  const maxCourse = Math.max(1, ...Array.from(courseCounts.values()).map((v) => v.count))
  const maxWebinar = Math.max(1, ...Array.from(webinarCounts.values()).map((v) => v.count))

    const [useDummy, setUseDummy] = useState(false)

    // prepare chart data
    const courseData = (useDummy
      ? [
          { name: "Trading Fundamentals", count: 40 },
          { name: "Technical Analysis", count: 28 },
          { name: "Risk Management", count: 20 },
          { name: "Market Psychology", count: 12 },
        ]
      : courses.map((c) => ({ name: c.title, count: (courseCounts.get(c.id)?.count) || 0 })))

    const webinarData = (useDummy
      ? [
          { name: "Jan 15", count: 120 },
          { name: "Jan 22", count: 85 },
          { name: "Feb 05", count: 60 },
        ]
      : webinars.map((w) => ({ name: w.title, count: (webinarCounts.get(w.id)?.count) || 0 })))

  if (loading) {
    return (
      <>
        <Navigation />
        <div className="max-w-4xl mx-auto px-6 py-24">Loading analytics…</div>
        <Footer />
      </>
    )
  }

  return (
    <>
      <Navigation />

      <div className="max-w-7xl mx-auto px-6 py-12">
        <h1 className="text-3xl font-bold mb-6">Admin Analytics</h1>

        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-semibold">Overview — registrations</h2>
          <div className="flex items-center gap-3">
            <label className="text-sm text-muted-foreground">Use dummy data</label>
            <input type="checkbox" checked={useDummy} onChange={(e) => setUseDummy(e.target.checked)} />
          </div>
        </div>

        <section className="mb-8 grid md:grid-cols-2 gap-6">
          <div className="p-4 bg-card rounded-lg border">
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={courseData} margin={{ top: 10, right: 12, left: 12, bottom: 20 }}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" tick={{ fontSize: 12 }} interval={0} angle={-30} textAnchor="end" height={60} />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="count" fill="#2563EB" animationDuration={800}>
                    {courseData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={index % 2 === 0 ? "#2563EB" : "#1E40AF"} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="p-4 bg-card rounded-lg border">
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={webinarData} margin={{ top: 10, right: 12, left: 12, bottom: 20 }}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" tick={{ fontSize: 12 }} interval={0} angle={-30} textAnchor="end" height={60} />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="count" fill="#0EA5A4" animationDuration={800}>
                    {webinarData.map((entry, index) => (
                      <Cell key={`cell-w-${index}`} fill={index % 2 === 0 ? "#0EA5A4" : "#059669"} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </section>

        <section className="mb-8">
          <h2 className="text-xl font-semibold mb-4">Courses — registrations</h2>
          <h2 className="text-xl font-semibold mb-4">Courses — registrations</h2>
          <div className="space-y-4">
            {courses.length === 0 && <div className="text-sm text-muted-foreground">No courses found.</div>}
            {courses.map((c) => {
              const stat = courseCounts.get(c.id) || { count: 0, last: null }
              const pct = Math.round((stat.count / maxCourse) * 100)
              return (
                <div key={c.id} className="p-4 bg-card rounded-lg border flex flex-col md:flex-row md:items-center md:justify-between">
                  <div>
                    <div className="font-semibold">{c.title}</div>
                    <div className="text-sm text-muted-foreground">{c.duration} • {c.modules} modules • {c.price}</div>
                  </div>

                  <div className="mt-3 md:mt-0 md:w-1/2">
                    <div className="flex items-center justify-between mb-2">
                      <div className="text-sm text-muted-foreground">Registrations: <span className="font-semibold">{stat.count}</span></div>
                      <div className="text-xs text-muted-foreground">Last: {stat.last ? format(new Date(stat.last), 'PP p') : '—'}</div>
                    </div>
                    <div className="w-full h-3 bg-background rounded overflow-hidden">
                      <div className="h-3 bg-primary" style={{ width: `${pct}%` }} />
                    </div>
                  </div>
                </div>
              )
            })}
          </div>
        </section>

        <section>
          <h2 className="text-xl font-semibold mb-4">Webinars — registrations</h2>
          <div className="space-y-4">
            {webinars.length === 0 && <div className="text-sm text-muted-foreground">No webinars found.</div>}
            {webinars.map((w) => {
              const stat = webinarCounts.get(w.id) || { count: 0, last: null }
              const pct = Math.round((stat.count / maxWebinar) * 100)
              return (
                <div key={w.id} className="p-4 bg-card rounded-lg border flex flex-col md:flex-row md:items-center md:justify-between">
                  <div>
                    <div className="font-semibold">{w.title}</div>
                    <div className="text-sm text-muted-foreground">{w.date} • {w.time} • {w.platform}</div>
                  </div>

                  <div className="mt-3 md:mt-0 md:w-1/2">
                    <div className="flex items-center justify-between mb-2">
                      <div className="text-sm text-muted-foreground">Registrations: <span className="font-semibold">{stat.count}</span></div>
                      <div className="text-xs text-muted-foreground">Last: {stat.last ? format(new Date(stat.last), 'PP p') : '—'}</div>
                    </div>
                    <div className="w-full h-3 bg-background rounded overflow-hidden">
                      <div className="h-3 bg-accent" style={{ width: `${pct}%` }} />
                    </div>
                  </div>
                </div>
              )
            })}
          </div>
        </section>

      </div>

      <Footer />
    </>
  )
}
