'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { Button } from '@/components/ui/button'
import { logout, fetchCurrentUser } from '@/lib/auth'
import apiFetch from '@/lib/api'
import { Bell, LogOut, User } from 'lucide-react'

export function AdminTopbar() {
  const router = useRouter()
  const [userName, setUserName] = useState('Admin')
  const [initials, setInitials] = useState('A')
  const [notifCount, setNotifCount] = useState(0)

  useEffect(() => {
    loadProfile()
    loadNotifications()
  }, [])

  const loadProfile = async () => {
    const user = await fetchCurrentUser()
    if (user) {
      setUserName(user.full_name)
      const parts = user.full_name.split(' ')
      setInitials(parts.map(p => p[0]).join('').toUpperCase().slice(0, 2))
    }
  }

  const loadNotifications = async () => {
    try {
      const notifs = await apiFetch<any[]>('/notifications')
      setNotifCount(notifs.filter((n: any) => !n.is_read).length)
    } catch {}
  }

  const handleLogout = () => {
    logout()
    router.push('/')
  }

  return (
    <header className="bg-white border-b border-slate-200 sticky top-0 z-50 ml-64">
      <div className="flex items-center justify-between px-8 py-4">
        <h2 className="text-lg font-semibold text-slate-900">Admin Dashboard</h2>
        
        <div className="flex items-center gap-4">
          <Button variant="ghost" size="icon" className="relative">
            <Bell className="w-5 h-5 text-slate-600" />
            {notifCount > 0 && (
              <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full"></span>
            )}
          </Button>

          <div className="w-px h-6 bg-slate-200"></div>

          <Button variant="ghost" size="sm" className="flex items-center gap-2">
            <div className="w-8 h-8 bg-cyan-100 rounded-full flex items-center justify-center text-sm font-bold text-cyan-600">
              {initials}
            </div>
            <span className="hidden sm:block text-sm font-medium text-slate-900">{userName.split(' ')[0]}</span>
          </Button>

          <Button
            variant="ghost"
            size="sm"
            onClick={handleLogout}
            className="text-slate-600 hover:text-red-600"
          >
            <LogOut className="w-4 h-4" />
          </Button>
        </div>
      </div>
    </header>
  )
}
