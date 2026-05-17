'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { 
  LayoutDashboard, 
  FileText, 
  Users, 
  Settings, 
  Shield,
  HardDrive,
  Bell,
  ChevronRight
} from 'lucide-react'
import { cn } from '@/lib/utils'

export function AdminSidebar() {
  const pathname = usePathname()

  const navItems = [
    {
      label: 'Dashboard',
      href: '/admin',
      icon: LayoutDashboard,
      exact: true,
    },
    {
      label: 'Reports Queue',
      href: '/admin/reports',
      icon: FileText,
    },
    {
      label: 'Evidence Management',
      href: '/admin/evidence',
      icon: HardDrive,
    },
    {
      label: 'Users',
      href: '/admin/users',
      icon: Users,
    },
    {
      label: 'Settings',
      href: '/admin/settings',
      icon: Settings,
    },
  ]

  const isActive = (href: string, exact?: boolean) => {
    if (exact) {
      return pathname === href
    }
    return pathname?.startsWith(href)
  }

  return (
    <aside className="w-64 bg-slate-900 text-white border-r border-slate-800 flex flex-col fixed left-0 top-0 h-screen">
      {/* Logo */}
      <div className="p-6 border-b border-slate-800 flex items-center gap-3">
        <Shield className="w-8 h-8 text-cyan-500" />
        <div>
          <h1 className="font-bold text-lg">TrustLine</h1>
          <p className="text-xs text-slate-400">Admin Portal</p>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 overflow-y-auto py-6 px-3 space-y-2">
        {navItems.map((item) => {
          const Icon = item.icon
          const active = isActive(item.href, item.exact)
          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                'flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium transition-colors relative group',
                active
                  ? 'bg-cyan-600 text-white'
                  : 'text-slate-300 hover:bg-slate-800'
              )}
            >
              <Icon className="w-5 h-5 flex-shrink-0" />
              <span className="flex-1">{item.label}</span>
              {active && (
                <ChevronRight className="w-4 h-4 absolute right-3" />
              )}
            </Link>
          )
        })}
      </nav>

      {/* Footer */}
      <div className="p-4 border-t border-slate-800 text-xs text-slate-400">
        <p>Admin Control Panel</p>
        <p className="mt-2">v2.0 • 2026</p>
      </div>
    </aside>
  )
}
