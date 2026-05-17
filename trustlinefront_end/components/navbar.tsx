'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { Button } from '@/components/ui/button'
import { isAuthenticated, getStoredRole, logout } from '@/lib/auth'
import { Shield, LogOut, Menu, X } from 'lucide-react'

export function Navbar() {
  const [isLoggedIn, setIsLoggedIn] = useState(false)
  const [role, setRole] = useState<'user' | 'admin' | null>(null)
  const [isOpen, setIsOpen] = useState(false)
  const router = useRouter()

  useEffect(() => {
    if (isAuthenticated()) {
      setIsLoggedIn(true)
      setRole(getStoredRole())
    }
  }, [])

  const handleLogout = () => {
    logout()
    setIsLoggedIn(false)
    setRole(null)
    setIsOpen(false)
    router.push('/')
  }

  return (
    <nav className="bg-slate-900 text-white border-b border-slate-800">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <Link href={isLoggedIn && role === 'admin' ? '/admin' : isLoggedIn ? '/dashboard' : '/'} className="flex items-center gap-2">
            <Shield className="w-6 h-6 text-cyan-500" />
            <span className="font-bold text-lg">TrustLine</span>
          </Link>

          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center gap-6">
            {!isLoggedIn && (
              <>
                <Link href="/" className="hover:text-cyan-400 transition-colors">
                  Home
                </Link>
                <Link href="/chatbot" className="hover:text-cyan-400 transition-colors">
                  Report Now
                </Link>
                <Link href="/resources" className="hover:text-cyan-400 transition-colors">
                  Resources
                </Link>
                <Button asChild variant="outline" size="sm">
                  <Link href="/login">Login</Link>
                </Button>
              </>
            )}

            {isLoggedIn && role === 'user' && (
              <>
                <Link href="/dashboard" className="hover:text-cyan-400 transition-colors">
                  Dashboard
                </Link>
                <Link href="/reports" className="hover:text-cyan-400 transition-colors">
                  My Reports
                </Link>
                <Link href="/chatbot" className="hover:text-cyan-400 transition-colors">
                  Report Issue
                </Link>
                <Link href="/reports/new" className="hover:text-cyan-400 transition-colors">
                  Manual Report
                </Link>
                <Link href="/resources" className="hover:text-cyan-400 transition-colors">
                  Resources
                </Link>
                <Button variant="ghost" size="sm" onClick={handleLogout} className="flex items-center gap-2">
                  <LogOut className="w-4 h-4" />
                  Logout
                </Button>
              </>
            )}

            {isLoggedIn && role === 'admin' && (
              <>
                <Link href="/admin" className="hover:text-cyan-400 transition-colors">
                  Dashboard
                </Link>
                <Link href="/admin/reports" className="hover:text-cyan-400 transition-colors">
                  Reports Queue
                </Link>
                <Link href="/admin/users" className="hover:text-cyan-400 transition-colors">
                  Users
                </Link>
                <Button variant="ghost" size="sm" onClick={handleLogout} className="flex items-center gap-2">
                  <LogOut className="w-4 h-4" />
                  Logout
                </Button>
              </>
            )}
          </div>

          {/* Mobile Menu Button */}
          <button
            className="md:hidden p-2"
            onClick={() => setIsOpen(!isOpen)}
          >
            {isOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
          </button>
        </div>

        {/* Mobile Navigation */}
        {isOpen && (
          <div className="md:hidden pb-4 space-y-2 border-t border-slate-800 pt-4">
            {!isLoggedIn && (
              <>
                <Link href="/" className="block px-3 py-2 hover:bg-slate-800 rounded">
                  Home
                </Link>
                <Link href="/chatbot" className="block px-3 py-2 hover:bg-slate-800 rounded">
                  Report Now
                </Link>
                <Link href="/resources" className="block px-3 py-2 hover:bg-slate-800 rounded">
                  Resources
                </Link>
                <Button asChild variant="outline" size="sm" className="w-full">
                  <Link href="/login">Login</Link>
                </Button>
              </>
            )}

            {isLoggedIn && role === 'user' && (
              <>
                <Link href="/dashboard" className="block px-3 py-2 hover:bg-slate-800 rounded">
                  Dashboard
                </Link>
                <Link href="/reports" className="block px-3 py-2 hover:bg-slate-800 rounded">
                  My Reports
                </Link>
                <Link href="/chatbot" className="block px-3 py-2 hover:bg-slate-800 rounded">
                  Report Issue
                </Link>
                <Link href="/reports/new" className="block px-3 py-2 hover:bg-slate-800 rounded">
                  Manual Report
                </Link>
                <Link href="/resources" className="block px-3 py-2 hover:bg-slate-800 rounded">
                  Resources
                </Link>
                <Button variant="ghost" size="sm" onClick={handleLogout} className="w-full flex items-center justify-center gap-2">
                  <LogOut className="w-4 h-4" />
                  Logout
                </Button>
              </>
            )}

            {isLoggedIn && role === 'admin' && (
              <>
                <Link href="/admin" className="block px-3 py-2 hover:bg-slate-800 rounded">
                  Dashboard
                </Link>
                <Link href="/admin/reports" className="block px-3 py-2 hover:bg-slate-800 rounded">
                  Reports Queue
                </Link>
                <Link href="/admin/users" className="block px-3 py-2 hover:bg-slate-800 rounded">
                  Users
                </Link>
                <Button variant="ghost" size="sm" onClick={handleLogout} className="w-full flex items-center justify-center gap-2">
                  <LogOut className="w-4 h-4" />
                  Logout
                </Button>
              </>
            )}
          </div>
        )}
      </div>
    </nav>
  )
}
