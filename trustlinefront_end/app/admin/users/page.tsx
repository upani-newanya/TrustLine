'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { AdminSidebar } from '@/components/admin-sidebar'
import { AdminTopbar } from '@/components/admin-topbar'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { getCurrentUserRole } from '@/lib/auth'
import { apiFetch } from '@/lib/api'
import { Search, Shield, Users } from 'lucide-react'

export default function AdminUsersPage() {
  const [users, setUsers] = useState<any[]>([])
  const [filteredUsers, setFilteredUsers] = useState<any[]>([])
  const [searchQuery, setSearchQuery] = useState('')
  const router = useRouter()

  useEffect(() => {
    const role = getCurrentUserRole()
    if (role !== 'admin') {
      router.push('/login')
      return
    }

    async function load() {
      try {
        const data = await apiFetch<any[]>('/users?role=user')
        setUsers(data)
        setFilteredUsers(data)
      } catch (err) {
        console.error('Failed to load users', err)
      }
    }
    load()
  }, [router])

  useEffect(() => {
    let filtered = users

    if (searchQuery) {
      filtered = filtered.filter(u =>
        (u.full_name || '').toLowerCase().includes(searchQuery.toLowerCase()) ||
        (u.email || '').toLowerCase().includes(searchQuery.toLowerCase())
      )
    }

    setFilteredUsers(filtered)
  }, [searchQuery, users])

  return (
    <div className="min-h-screen bg-slate-50">
      <AdminSidebar />
      <AdminTopbar />

      <main className="ml-64 pt-20 pb-12">
        <div className="max-w-7xl mx-auto px-8">
          {/* Header */}
          <div className="mb-8">
            <h1 className="text-4xl font-bold text-slate-900">User Management</h1>
            <p className="text-slate-600 mt-2">View and monitor registered users</p>
          </div>

          {/* Stats */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8">
            <Card className="bg-blue-50">
              <CardContent className="pt-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-blue-700 font-medium">Total Users</p>
                    <p className="text-3xl font-bold text-blue-900 mt-2">{users.length}</p>
                  </div>
                  <Users className="w-8 h-8 text-blue-300 opacity-50" />
                </div>
              </CardContent>
            </Card>

            <Card className="bg-cyan-50">
              <CardContent className="pt-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-cyan-700 font-medium">Active Users</p>
                    <p className="text-3xl font-bold text-cyan-900 mt-2">
                      {users.filter(u => u.is_active).length}
                    </p>
                  </div>
                  <Shield className="w-8 h-8 text-cyan-300 opacity-50" />
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Search */}
          <Card className="mb-8">
            <CardHeader>
              <CardTitle className="text-lg flex items-center gap-2">
                <Search className="w-5 h-5" />
                Search Users
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex gap-4">
                <div className="flex-1">
                  <Input
                    placeholder="Search by name or email..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                  />
                </div>
                <Button
                  variant="outline"
                  onClick={() => setSearchQuery('')}
                >
                  Clear
                </Button>
              </div>
            </CardContent>
          </Card>

          {/* Users Table */}
          <Card>
            <CardHeader>
              <CardDescription>
                {filteredUsers.length} user{filteredUsers.length !== 1 ? 's' : ''} found
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b border-slate-200">
                      <th className="text-left text-sm font-semibold text-slate-900 pb-3 px-4">Name</th>
                      <th className="text-left text-sm font-semibold text-slate-900 pb-3 px-4">Email</th>
                      <th className="text-left text-sm font-semibold text-slate-900 pb-3 px-4">Role</th>
                      <th className="text-left text-sm font-semibold text-slate-900 pb-3 px-4">Status</th>
                      <th className="text-left text-sm font-semibold text-slate-900 pb-3 px-4">Joined</th>
                    </tr>
                  </thead>
                  <tbody>
                    {filteredUsers.map((user) => (
                        <tr key={user.id} className="border-b border-slate-200 hover:bg-slate-50">
                          <td className="px-4 py-3 font-medium text-slate-900 text-sm">{user.full_name}</td>
                          <td className="px-4 py-3 text-sm text-slate-600">{user.email}</td>
                          <td className="px-4 py-3 text-sm">
                            <Badge className="bg-blue-100 text-blue-800">
                              {user.role}
                            </Badge>
                          </td>
                          <td className="px-4 py-3 text-sm">
                            <Badge className={user.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}>
                              {user.is_active ? 'Active' : 'Inactive'}
                            </Badge>
                          </td>
                          <td className="px-4 py-3 text-sm text-slate-600">
                            {new Date(user.created_at).toLocaleDateString()}
                          </td>
                        </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </CardContent>
          </Card>
        </div>
      </main>
    </div>
  )
}
