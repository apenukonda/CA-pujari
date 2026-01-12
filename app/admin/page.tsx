"use client"

import { useEffect, useState } from "react"
import { Navigation } from "@/components/navigation"
import { Footer } from "@/components/footer"
import { db } from "@/lib/firebase"
import {
  collection,
  addDoc,
  getDocs,
  query,
  where,
  serverTimestamp,
  orderBy,
} from "firebase/firestore"
export default function AdminPage() {
  const [courses, setCourses] = useState<any[]>([])
  const [webinars, setWebinars] = useState<any[]>([])

  const [courseForm, setCourseForm] = useState({ title: "", description: "", duration: "", price: "", level: "", modules: "" })
  const [webinarForm, setWebinarForm] = useState({ title: "", date: "", time: "", duration: "", platform: "", price: "", seats: "", link: "" })

  const [loadingSave, setLoadingSave] = useState(false)

  useEffect(() => {
    // load existing courses and webinars
    async function load() {
      const cSnap = await getDocs(query(collection(db, "courses"), orderBy("createdAt", "desc")))
      setCourses(cSnap.docs.map((d) => ({ id: d.id, ...d.data() })))

      const wSnap = await getDocs(query(collection(db, "webinars"), orderBy("createdAt", "desc")))
      setWebinars(wSnap.docs.map((d) => ({ id: d.id, ...d.data() })))
    }
    load()
  }, [])

  async function saveCourse(e: React.FormEvent) {
    e.preventDefault()
    setLoadingSave(true)
    try {
      const doc = await addDoc(collection(db, "courses"), {
        ...courseForm,
        modules: Number(courseForm.modules) || 0,
        createdAt: serverTimestamp(),
      })
      setCourses((s) => [{ id: doc.id, ...courseForm }, ...s])
      setCourseForm({ title: "", description: "", duration: "", price: "", level: "", modules: "" })
    } finally {
      setLoadingSave(false)
    }
  }

  async function saveWebinar(e: React.FormEvent) {
    e.preventDefault()
    setLoadingSave(true)
    try {
      const doc = await addDoc(collection(db, "webinars"), {
        ...webinarForm,
        createdAt: serverTimestamp(),
      })
      setWebinars((s) => [{ id: doc.id, ...webinarForm }, ...s])
      setWebinarForm({ title: "", date: "", time: "", duration: "", platform: "", price: "", seats: "", link: "" })
    } finally {
      setLoadingSave(false)
    }
  }

  async function getRegistrationsCount(type: "course" | "webinar", itemId: string) {
    const q = query(collection(db, "registrations"), where("type", "==", type), where("itemId", "==", itemId))
    const snap = await getDocs(q)
    return snap.size
  }

  // NOTE: Admin security is temporarily disabled — page is public for testing.
  // Remove this warning when you re-enable admin authentication.

  return (
    <>
      <Navigation />

      <div className="max-w-7xl mx-auto px-6 py-12">
        <h1 className="text-3xl font-bold mb-6">Admin — Manage Content</h1>

        <section className="grid md:grid-cols-2 gap-8 mb-12">
          <form onSubmit={saveCourse} className="p-6 rounded-2xl bg-card border">
            <h3 className="font-semibold mb-4">Add Course</h3>
            <input className="w-full mb-2 p-2 rounded" placeholder="Title" value={courseForm.title} onChange={(e) => setCourseForm({ ...courseForm, title: e.target.value })} required />
            <textarea className="w-full mb-2 p-2 rounded" placeholder="Description" value={courseForm.description} onChange={(e) => setCourseForm({ ...courseForm, description: e.target.value })} required />
            <div className="flex gap-2 mb-2">
              <input className="flex-1 p-2 rounded" placeholder="Duration" value={courseForm.duration} onChange={(e) => setCourseForm({ ...courseForm, duration: e.target.value })} />
              <input className="w-28 p-2 rounded" placeholder="Modules" value={courseForm.modules} onChange={(e) => setCourseForm({ ...courseForm, modules: e.target.value })} />
            </div>
            <div className="flex gap-2 mb-4">
              <input className="flex-1 p-2 rounded" placeholder="Price" value={courseForm.price} onChange={(e) => setCourseForm({ ...courseForm, price: e.target.value })} />
              <input className="w-28 p-2 rounded" placeholder="Level" value={courseForm.level} onChange={(e) => setCourseForm({ ...courseForm, level: e.target.value })} />
            </div>
            <button type="submit" disabled={loadingSave} className="px-4 py-2 bg-primary text-primary-foreground rounded">{loadingSave ? "Saving..." : "Save Course"}</button>
          </form>

          <form onSubmit={saveWebinar} className="p-6 rounded-2xl bg-card border">
            <h3 className="font-semibold mb-4">Add Webinar</h3>
            <input className="w-full mb-2 p-2 rounded" placeholder="Title" value={webinarForm.title} onChange={(e) => setWebinarForm({ ...webinarForm, title: e.target.value })} required />
            <div className="grid grid-cols-2 gap-2 mb-2">
              <input className="p-2 rounded" placeholder="Date" value={webinarForm.date} onChange={(e) => setWebinarForm({ ...webinarForm, date: e.target.value })} />
              <input className="p-2 rounded" placeholder="Time" value={webinarForm.time} onChange={(e) => setWebinarForm({ ...webinarForm, time: e.target.value })} />
            </div>
            <div className="grid grid-cols-2 gap-2 mb-4">
              <input className="p-2 rounded" placeholder="Duration" value={webinarForm.duration} onChange={(e) => setWebinarForm({ ...webinarForm, duration: e.target.value })} />
              <input className="p-2 rounded" placeholder="Platform" value={webinarForm.platform} onChange={(e) => setWebinarForm({ ...webinarForm, platform: e.target.value })} />
            </div>
            <div className="flex gap-2 mb-4">
              <input className="flex-1 p-2 rounded" placeholder="Price" value={webinarForm.price} onChange={(e) => setWebinarForm({ ...webinarForm, price: e.target.value })} />
                <input className="w-full mb-4 p-2 rounded" placeholder="Join link (https://...)" value={webinarForm.link} onChange={(e) => setWebinarForm({ ...webinarForm, link: e.target.value })} />
            </div>
            <button type="submit" disabled={loadingSave} className="px-4 py-2 bg-primary text-primary-foreground rounded">{loadingSave ? "Saving..." : "Save Webinar"}</button>
          </form>
        </section>

        <section className="grid md:grid-cols-2 gap-8">
          <div className="p-6 rounded-2xl bg-card border">
            <h3 className="font-semibold mb-4">Courses</h3>
            <div className="space-y-4">
              {courses.map((c) => (
                <div key={c.id} className="p-3 rounded bg-background/50 flex justify-between items-center">
                  <div>
                    <div className="font-semibold">{c.title}</div>
                    <div className="text-sm text-muted-foreground">{c.duration} • {c.modules} modules</div>
                  </div>
                  <div className="text-sm">
                    <button
                      onClick={async () => {
                        const count = await getRegistrationsCount("course", c.id)
                        alert(`${count} registrations for ${c.title}`)
                      }}
                      className="px-3 py-1 bg-primary text-primary-foreground rounded"
                    >
                      Analytics
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="p-6 rounded-2xl bg-card border">
            <h3 className="font-semibold mb-4">Webinars</h3>
            <div className="space-y-4">
              {webinars.map((w) => (
                <div key={w.id} className="p-3 rounded bg-background/50 flex justify-between items-center">
                  <div>
                    <div className="font-semibold">{w.title}</div>
                    <div className="text-sm text-muted-foreground">{w.date} • {w.time}</div>
                  </div>
                  <div className="text-sm">
                    <button
                      onClick={async () => {
                        const count = await getRegistrationsCount("webinar", w.id)
                        alert(`${count} registrations for ${w.title}`)
                      }}
                      className="px-3 py-1 bg-primary text-primary-foreground rounded"
                    >
                      Analytics
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </section>
      </div>

      <Footer />
    </>
  )
}
