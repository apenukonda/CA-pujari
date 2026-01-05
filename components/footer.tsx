import Link from "next/link"
import { Linkedin, Youtube, Mail } from "lucide-react"

export function Footer() {
  return (
    <footer className="bg-primary text-primary-foreground py-12">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8 mb-8">
          <div>
            <h3 className="font-bold text-lg mb-4">Shobha Pujari</h3>
            <p className="text-sm opacity-90">Empowering beginners with trading knowledge</p>
          </div>
          <div>
            <h4 className="font-semibold mb-4">Quick Links</h4>
            <ul className="space-y-2 text-sm">
              <li>
                <Link href="/courses" className="hover:opacity-80 transition-opacity">
                  Courses
                </Link>
              </li>
              <li>
                <Link href="/webinars" className="hover:opacity-80 transition-opacity">
                  Webinars
                </Link>
              </li>
              <li>
                <Link href="/community" className="hover:opacity-80 transition-opacity">
                  Community
                </Link>
              </li>
              <li>
                <Link href="/about" className="hover:opacity-80 transition-opacity">
                  About
                </Link>
              </li>
            </ul>
          </div>
          <div>
            <h4 className="font-semibold mb-4">Resources</h4>
            <ul className="space-y-2 text-sm">
              <li>
                <a href="#" className="hover:opacity-80 transition-opacity">
                  Blog
                </a>
              </li>
              <li>
                <a href="#" className="hover:opacity-80 transition-opacity">
                  FAQ
                </a>
              </li>
              <li>
                <a href="#" className="hover:opacity-80 transition-opacity">
                  Terms
                </a>
              </li>
              <li>
                <a href="#" className="hover:opacity-80 transition-opacity">
                  Privacy
                </a>
              </li>
            </ul>
          </div>
          <div>
            <h4 className="font-semibold mb-4">Connect</h4>
            <div className="flex gap-4">
              <a href="https://linkedin.com" className="hover:opacity-80 transition-opacity">
                <Linkedin size={20} />
              </a>
              <a href="https://youtube.com" className="hover:opacity-80 transition-opacity">
                <Youtube size={20} />
              </a>
              <a href="mailto:info@example.com" className="hover:opacity-80 transition-opacity">
                <Mail size={20} />
              </a>
            </div>
          </div>
        </div>
        <div className="border-t border-primary-foreground/20 pt-8 text-center text-sm">
          <p>&copy; 2026 Shobha Pujari. All rights reserved.</p>
        </div>
      </div>
    </footer>
  )
}
