'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { AdminSidebar } from '@/components/admin-sidebar'
import { AdminTopbar } from '@/components/admin-topbar'
import { StatusBadge } from '@/components/status-badge'
import { PriorityBadge } from '@/components/priority-badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { getCurrentUserRole } from '@/lib/auth'
import { apiFetch } from '@/lib/api'
import { AlertCircle, FileText, Clock, CheckCircle, Eye } from 'lucide-react'

export default function AdminPage() {
  const [reports, setReports] = useState<any[]>([])
  const [stats, setStats] = useState({
    newReports: 0,
    pendingReview: 0,
    highPriority: 0,
    needingInfo: 0,
    closedThisWeek: 0,
  })
  const router = useRouter()

  useEffect(() => {
    const role = getCurrentUserRole()
    if (role !== 'admin') {
      router.push('/login')
      return
    }

    async function load() {
      try {
        const [dashData, queue] = await Promise.all([
          apiFetch<any>('/admin/dashboard'),
          apiFetch<any[]>('/admin/complaints/queue'),
        ])
        setStats({
          newReports: dashData.new_reports_24h ?? 0,
          pendingReview: dashData.pending_review ?? 0,
          highPriority: dashData.high_priority ?? 0,
          needingInfo: dashData.needing_info ?? 0,
          closedThisWeek: dashData.closed_this_week ?? 0,
        })
        setReports(queue)
      } catch (err) {
        console.error('Failed to load admin dashboard', err)
      }
    }
    load()
  }, [router])

  return (
    <div className="min-h-screen bg-slate-50">
      <AdminSidebar />
      <AdminTopbar />

      <main className="ml-64 pt-20 pb-12">
        <div className="max-w-7xl mx-auto px-8">
          {/* Header */}
          <div className="mb-8">
            <h1 className="text-4xl font-bold text-slate-900">Welcome Back</h1>
            <p className="text-slate-600 mt-2">Here's what's happening with your reports today</p>
          </div>

          {/* Stats Cards */}
          <div className="grid grid-cols-1 md:grid-cols-5 gap-4 mb-8">
            {[
              { 
                label: 'New Reports (24h)', 
                value: stats.newReports, 
                icon: FileText, 
                color: 'bg-yellow-100',
                textColor: 'text-yellow-700'
              },
              { 
                label: 'Pending Review', 
                value: stats.pendingReview, 
                icon: Clock, 
                color: 'bg-blue-100',
                textColor: 'text-blue-700'
              },
              { 
                label: 'High Priority', 
                value: stats.highPriority, 
                icon: AlertCircle, 
                color: 'bg-red-100',
                textColor: 'text-red-700'
              },
              { 
                label: 'Awaiting Info', 
                value: stats.needingInfo, 
                icon: FileText, 
                color: 'bg-orange-100',
                textColor: 'text-orange-700'
              },
              { 
                label: 'Closed (Week)', 
                value: stats.closedThisWeek, 
                icon: CheckCircle, 
                color: 'bg-green-100',
                textColor: 'text-green-700'
              },
            ].map((stat, idx) => {
              const Icon = stat.icon
              return (
                <Card key={idx} className={stat.color}>
                  <CardContent className="pt-6">
                    <div className="flex items-start justify-between">
                      <div>
                        <p className={`text-sm font-medium ${stat.textColor}`}>{stat.label}</p>
                        <p className={`text-3xl font-bold ${stat.textColor} mt-2`}>{stat.value}</p>
                      </div>
                      <Icon className={`w-8 h-8 ${stat.textColor} opacity-40`} />
                    </div>
                  </CardContent>
                </Card>
              )
            })}
          </div>

          {/* Recent Reports Table */}
          <Card>
            <CardHeader>
              <div className="flex justify-between items-center">
                <div>
                  <CardTitle>Recent Reports</CardTitle>
                  <CardDescription>Latest 10 reports submitted to the system</CardDescription>
                </div>
                <Button asChild>
                  <Link href="/admin/reports">View All</Link>
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b border-slate-200">
                      <th className="text-left text-sm font-semibold text-slate-900 pb-3 px-4">Case ID</th>
                      <th className="text-left text-sm font-semibold text-slate-900 pb-3 px-4">Incident Type</th>
                      <th className="text-left text-sm font-semibold text-slate-900 pb-3 px-4">Platform</th>
                      <th className="text-left text-sm font-semibold text-slate-900 pb-3 px-4">Priority</th>
                      <th className="text-left text-sm font-semibold text-slate-900 pb-3 px-4">Status</th>
                      <th className="text-left text-sm font-semibold text-slate-900 pb-3 px-4">Submitted</th>
                      <th className="text-left text-sm font-semibold text-slate-900 pb-3 px-4">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {reports.slice(0, 10).map((report) => (
                      <tr key={report.id} className="border-b border-slate-200 hover:bg-slate-50">
                        <td className="px-4 py-3 text-sm font-medium text-slate-900">{report.case_id}</td>
                        <td className="px-4 py-3 text-sm text-slate-600">{report.category}</td>
                        <td className="px-4 py-3 text-sm text-slate-600">{report.source_platform}</td>
                        <td className="px-4 py-3 text-sm">
                          <PriorityBadge priority={report.priority} />
                        </td>
                        <td className="px-4 py-3 text-sm">
                          <StatusBadge status={report.status} />
                        </td>
                        <td className="px-4 py-3 text-sm text-slate-600">
                          {new Date(report.created_at).toLocaleDateString()}
                        </td>
                        <td className="px-4 py-3 text-sm">
                          <Button asChild variant="outline" size="sm">
                            <Link href={`/admin/reports/${report.id}`} className="flex items-center gap-2">
                              <Eye className="w-4 h-4" />
                              View
                            </Link>
                          </Button>
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
