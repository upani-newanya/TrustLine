'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { AdminSidebar } from '@/components/admin-sidebar'
import { AdminTopbar } from '@/components/admin-topbar'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Badge } from '@/components/ui/badge'
import { Checkbox } from '@/components/ui/checkbox'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Switch } from '@/components/ui/switch'
import { fetchCurrentUser, logout as authLogout, getCurrentUserRole, type CurrentUser } from '@/lib/auth'
import { Shield, Bell, Lock, LogOut, AlertTriangle } from 'lucide-react'

export default function AdminSettingsPage() {
  const [notificationsEnabled, setNotificationsEnabled] = useState(true)
  const [isSaving, setIsSaving] = useState(false)
  const [user, setUser] = useState<CurrentUser | null>(null)
  const router = useRouter()

  useEffect(() => {
    const role = getCurrentUserRole()
    if (role !== 'admin') {
      router.push('/login')
      return
    }

    async function load() {
      try {
        const me = await fetchCurrentUser()
        setUser(me)
      } catch {}
    }
    load()
  }, [router])

  const handleSaveSettings = async () => {
    setIsSaving(true)
    await new Promise(resolve => setTimeout(resolve, 500))
    setIsSaving(false)
  }

  const handleLogout = () => {
    authLogout()
    router.push('/')
  }

  return (
    <div className="min-h-screen bg-slate-50">
      <AdminSidebar />
      <AdminTopbar />

      <main className="ml-64 pt-20 pb-12">
        <div className="max-w-4xl mx-auto px-8">
          {/* Header */}
          <div className="mb-8">
            <h1 className="text-4xl font-bold text-slate-900">Settings</h1>
            <p className="text-slate-600 mt-2">Manage your admin account and system preferences</p>
          </div>

          {/* Profile Section */}
          <Card className="mb-6">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Shield className="w-5 h-5" />
                Admin Profile
              </CardTitle>
              <CardDescription>Your account information</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="name">Full Name</Label>
                  <Input id="name" value={user?.full_name || ''} disabled />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="email">Email Address</Label>
                  <Input id="email" type="email" value={user?.email || ''} disabled />
                </div>
              </div>
              <div className="space-y-2">
                <Label htmlFor="role">Role</Label>
                <Input id="role" value={user?.role || ''} disabled />
              </div>
              <div className="border-t border-slate-200 pt-4">
                <Button variant="outline">Change Password</Button>
              </div>
            </CardContent>
          </Card>

          {/* Notification Preferences */}
          <Card className="mb-6">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Bell className="w-5 h-5" />
                Notification Preferences
              </CardTitle>
              <CardDescription>Control how you receive alerts and updates</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="space-y-4">
                {[
                  { id: 'new-reports', label: 'New Reports', description: 'Alert when a new report is submitted' },
                  { id: 'high-priority', label: 'High Priority Cases', description: 'Alert for high priority incidents' },
                  { id: 'response-needed', label: 'Response Needed', description: 'Alert when user response is required' },
                  { id: 'case-updates', label: 'Case Updates', description: 'Notify of any case status changes' },
                ].map(item => (
                  <div key={item.id} className="flex items-center justify-between">
                    <div>
                      <p className="font-medium text-slate-900">{item.label}</p>
                      <p className="text-sm text-slate-600">{item.description}</p>
                    </div>
                    <Switch defaultChecked />
                  </div>
                ))}
              </div>

              <div className="border-t border-slate-200 pt-4">
                <div className="space-y-2">
                  <Label htmlFor="workHours">Notification Hours</Label>
                  <p className="text-sm text-slate-600">When should we send you notifications?</p>
                  <Input id="workHours" value="24/7 (Always)" disabled />
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Security Settings */}
          <Card className="mb-6">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Lock className="w-5 h-5" />
                Security
              </CardTitle>
              <CardDescription>Protect your account and manage access</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="font-medium text-slate-900">Two-Factor Authentication</p>
                  <p className="text-sm text-slate-600">Add an extra layer of security to your account</p>
                </div>
                <Button variant="outline">Enable</Button>
              </div>

              <div className="border-t border-slate-200 pt-4">
                <p className="font-medium text-slate-900 mb-4">Active Sessions</p>
                <div className="space-y-3">
                  <div className="flex items-center justify-between p-3 border border-slate-200 rounded">
                    <div>
                      <p className="font-medium text-slate-900 text-sm">Current Session</p>
                      <p className="text-xs text-slate-600">Last active: Just now</p>
                    </div>
                    <Badge className="bg-green-100 text-green-800">Active</Badge>
                  </div>
                </div>
              </div>

              <div className="border-t border-slate-200 pt-4">
                <Button variant="outline" className="w-full">
                  View All Sessions
                </Button>
              </div>
            </CardContent>
          </Card>

          {/* System Status */}
          <Card className="mb-6">
            <CardHeader>
              <CardTitle>System Status</CardTitle>
              <CardDescription>Current system health and information</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="border border-slate-200 rounded p-4">
                  <p className="text-sm text-slate-600 mb-2">System Status</p>
                  <div className="flex items-center gap-2">
                    <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                    <p className="font-medium text-slate-900">All Systems Operational</p>
                  </div>
                </div>
                <div className="border border-slate-200 rounded p-4">
                  <p className="text-sm text-slate-600 mb-2">Database Status</p>
                  <div className="flex items-center gap-2">
                    <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                    <p className="font-medium text-slate-900">Connected & Healthy</p>
                  </div>
                </div>
                <div className="border border-slate-200 rounded p-4">
                  <p className="text-sm text-slate-600 mb-2">API Status</p>
                  <div className="flex items-center gap-2">
                    <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                    <p className="font-medium text-slate-900">Operational</p>
                  </div>
                </div>
                <div className="border border-slate-200 rounded p-4">
                  <p className="text-sm text-slate-600 mb-2">Uptime</p>
                  <p className="font-medium text-slate-900">99.9%</p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Danger Zone */}
          <Card className="border-red-200 bg-red-50">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-red-900">
                <AlertTriangle className="w-5 h-5" />
                Danger Zone
              </CardTitle>
              <CardDescription className="text-red-800">
                Irreversible actions. Please proceed with caution.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <Alert className="bg-red-100 border-red-300">
                <AlertTriangle className="h-4 w-4 text-red-600" />
                <AlertDescription className="text-red-900">
                  Logging out will end your current session. You can log back in at any time.
                </AlertDescription>
              </Alert>

              <Button
                onClick={handleLogout}
                variant="destructive"
                className="w-full"
              >
                <LogOut className="w-4 h-4 mr-2" />
                Logout
              </Button>
            </CardContent>
          </Card>

          {/* Save Button */}
          <div className="mt-8 flex justify-end gap-4">
            <Button variant="outline">Cancel</Button>
            <Button onClick={handleSaveSettings} disabled={isSaving}>
              {isSaving ? 'Saving...' : 'Save Settings'}
            </Button>
          </div>
        </div>
      </main>
    </div>
  )
}
