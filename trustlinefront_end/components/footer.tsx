import Link from 'next/link'

export function Footer() {
  return (
    <footer className="bg-slate-900 text-slate-300 border-t border-slate-800 mt-12">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-8">
          {/* About */}
          <div>
            <h3 className="text-white font-semibold mb-4">About TrustLine</h3>
            <p className="text-sm">
              TrustLine is a secure platform dedicated to helping victims of cyberbullying, online harassment, and privacy violations report incidents safely and anonymously.
            </p>
          </div>

          {/* Links */}
          <div>
            <h3 className="text-white font-semibold mb-4">Quick Links</h3>
            <ul className="text-sm space-y-2">
              <li>
                <Link href="/" className="hover:text-cyan-400 transition-colors">
                  Home
                </Link>
              </li>
              <li>
                <Link href="/chatbot" className="hover:text-cyan-400 transition-colors">
                  Report Issue
                </Link>
              </li>
              <li>
                <Link href="/resources" className="hover:text-cyan-400 transition-colors">
                  Resources
                </Link>
              </li>
              <li>
                <Link href="/login" className="hover:text-cyan-400 transition-colors">
                  Login
                </Link>
              </li>
            </ul>
          </div>

          {/* Contact */}
          <div>
            <h3 className="text-white font-semibold mb-4">Contact</h3>
            <ul className="text-sm space-y-2">
              <li>
                <a href="tel:1-800-TRUSTLINE" className="hover:text-cyan-400 transition-colors">
                  1-800-TRUSTLINE
                </a>
              </li>
              <li>
                <a href="mailto:help@trustline.gov.lk" className="hover:text-cyan-400 transition-colors">
                  help@trustline.gov.lk
                </a>
              </li>
              <li>24/7 Support Available</li>
            </ul>
          </div>
        </div>

        <div className="border-t border-slate-800 pt-8">
          <div className="flex flex-col md:flex-row justify-between items-center text-sm text-slate-400">
            <p>&copy; 2026 TrustLine. All rights reserved.</p>
            <div className="flex gap-6 mt-4 md:mt-0">
              <Link href="#" className="hover:text-cyan-400 transition-colors">
                Privacy Policy
              </Link>
              <Link href="#" className="hover:text-cyan-400 transition-colors">
                Terms of Service
              </Link>
              <Link href="#" className="hover:text-cyan-400 transition-colors">
                Security
              </Link>
            </div>
          </div>
        </div>
      </div>
    </footer>
  )
}
