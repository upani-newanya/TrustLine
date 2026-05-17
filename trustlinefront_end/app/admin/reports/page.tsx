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
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Checkbox } from '@/components/ui/checkbox'
import { getCurrentUserRole } from '@/lib/auth'
import { apiFetch } from '@/lib/api'
import { Search, Filter, Eye, CheckCircle } from 'lucide-react'

export default function AdminReportsPage() {
  const [reports, setReports] = useState<any[]>([])
  const [filteredReports, setFilteredReports] = useState<any[]>([])
  const [selectedReports, setSelectedReports] = useState<Set<string>>(new Set())
  
  // Filters
  const [searchQuery, setSearchQuery] = useState('')
  const [statusFilter, setStatusFilter] = useState('all')
  const [priorityFilter, setPriorityFilter] = useState('all')
  const [incidentTypeFilter, setIncidentTypeFilter] = useState('all')
  
  const router = useRouter()

  const loadReports = async () => {
    try {
      const params = new URLSearchParams()
      if (statusFilter !== 'all') params.set('status', statusFilter)
      if (priorityFilter !== 'all') params.set('priority', priorityFilter)
      const qs = params.toString()
      const data = await apiFetch<any[]>(`/admin/complaints/queue${qs ? `?${qs}` : ''}`)
      setReports(data)
    } catch (err) {
      console.error('Failed to load reports', err)
    }
  }

  useEffect(() => {
    const role = getCurrentUserRole()
    if (role !== 'admin') {
      router.push('/login')
      return
    }
    loadReports()
  }, [router])

  useEffect(() => {
    loadReports()
  }, [statusFilter, priorityFilter])

  useEffect(() => {
    let filtered = reports

    if (incidentTypeFilter !== 'all') {
      filtered = filtered.filter(r => r.category === incidentTypeFilter)
    }

    if (searchQuery) {
      filtered = filtered.filter(r =>
        (r.case_id || '').toLowerCase().includes(searchQuery.toLowerCase()) ||
        (r.reporter_name || '').toLowerCase().includes(searchQuery.toLowerCase())
      )
    }

    setFilteredReports(filtered)
  }, [searchQuery, incidentTypeFilter, reports])

  const handleSelectReport = (reportId: string) => {
    const newSelected = new Set(selectedReports)
    if (newSelected.has(reportId)) {
      newSelected.delete(reportId)
    } else {
      newSelected.add(reportId)
    }
    setSelectedReports(newSelected)
  }

  const handleSelectAll = () => {
    if (selectedReports.size === filteredReports.length) {
      setSelectedReports(new Set())
    } else {
      setSelectedReports(new Set(filteredReports.map(r => r.id)))
    }
  }

  const handleBulkAction = async (action: string) => {
    if (selectedReports.size === 0) return

    try {
      const promises = Array.from(selectedReports).map(async (reportId) => {
        switch (action) {
          case 'assign':
            return apiFetch(`/admin/complaints/${reportId}/assign`, { method: 'PATCH' })
          case 'review':
            return apiFetch(`/admin/complaints/${reportId}/status`, {
              method: 'PATCH',
              body: JSON.stringify({ status: 'under_review' }),
            })
          case 'request-info':
            return apiFetch(`/admin/complaints/${reportId}/status`, {
              method: 'PATCH',
              body: JSON.stringify({ status: 'need_more_info' }),
            })
          case 'close':
            return apiFetch(`/admin/complaints/${reportId}/status`, {
              method: 'PATCH',
              body: JSON.stringify({ status: 'closed' }),
            })
        }
      })
      await Promise.all(promises)
    } catch (err) {
      console.error('Bulk action failed', err)
    }

    // Refresh reports
    await loadReports()
    setSelectedReports(new Set())
  }

  const incidentTypes = Array.from(new Set(reports.map(r => r.category).filter(Boolean)))

  return (
    <div className="min-h-screen bg-slate-50">
      <AdminSidebar />
      <AdminTopbar />

      <main className="ml-64 pt-20 pb-12">
        <div className="max-w-7xl mx-auto px-8">
          {/* Header */}
          <div className="mb-8">
            <h1 className="text-4xl font-bold text-slate-900">Reports Queue</h1>
            <p className="text-slate-600 mt-2">Manage and review all submitted reports</p>
          </div>

          {/* Filters */}
          <Card className="mb-8">
            <CardHeader>
              <CardTitle className="text-lg flex items-center gap-2">
                <Filter className="w-5 h-5" />
                Filters & Search
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="search">Search</Label>
                  <div className="relative">
                    <Search className="absolute left-3 top-3 w-4 h-4 text-slate-400" />
                    <Input
                      id="search"
                      placeholder="Case ID or name"
                      value={searchQuery}
                      onChange={(e) => setSearchQuery(e.target.value)}
                      className="pl-10"
                    />
                  </div>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="status">Status</Label>
                  <Select value={statusFilter} onValueChange={setStatusFilter}>
                    <SelectTrigger id="status">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">All Status</SelectItem>
                      <SelectItem value="pending">Pending</SelectItem>
                      <SelectItem value="under_review">Under Review</SelectItem>
                      <SelectItem value="need_more_info">Need More Info</SelectItem>
                      <SelectItem value="escalated">Escalated</SelectItem>
                      <SelectItem value="closed">Closed</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="priority">Priority</Label>
                  <Select value={priorityFilter} onValueChange={setPriorityFilter}>
                    <SelectTrigger id="priority">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">All Priorities</SelectItem>
                      <SelectItem value="high">High</SelectItem>
                      <SelectItem value="medium">Medium</SelectItem>
                      <SelectItem value="low">Low</SelectItem>
                      <SelectItem value="urgent">Urgent</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="incident">Incident Type</Label>
                  <Select value={incidentTypeFilter} onValueChange={setIncidentTypeFilter}>
                    <SelectTrigger id="incident">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">All Types</SelectItem>
                      {incidentTypes.map(type => (
                        <SelectItem key={type} value={type}>{type}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div className="flex items-end">
                  <Button
                    variant="outline"
                    onClick={() => {
                      setSearchQuery('')
                      setStatusFilter('all')
                      setPriorityFilter('all')
                      setIncidentTypeFilter('all')
                    }}
                    className="w-full"
                  >
                    Clear Filters
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Bulk Actions */}
          {selectedReports.size > 0 && (
            <Card className="mb-8 bg-cyan-50 border-cyan-200">
              <CardContent className="pt-6">
                <div className="flex items-center justify-between flex-wrap gap-4">
                  <p className="font-medium text-slate-900">
                    {selectedReports.size} report{selectedReports.size > 1 ? 's' : ''} selected
                  </p>
                  <div className="flex gap-2">
                    <Button size="sm" onClick={() => handleBulkAction('assign')}>
                      Assign Selected
                    </Button>
                    <Button size="sm" onClick={() => handleBulkAction('review')}>
                      Mark as Review
                    </Button>
                    <Button size="sm" onClick={() => handleBulkAction('request-info')}>
                      Request Info
                    </Button>
                    <Button size="sm" variant="destructive" onClick={() => handleBulkAction('close')}>
                      Close Selected
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Reports Table */}
          <Card>
            <CardHeader>
              <CardDescription>
                {filteredReports.length} report{filteredReports.length !== 1 ? 's' : ''} found
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b border-slate-200">
                      <th className="text-left pb-3 px-4 w-12">
                        <Checkbox
                          checked={selectedReports.size === filteredReports.length && filteredReports.length > 0}
                          onCheckedChange={handleSelectAll}
                        />
                      </th>
                      <th className="text-left text-sm font-semibold text-slate-900 pb-3 px-4">Case ID</th>
                      <th className="text-left text-sm font-semibold text-slate-900 pb-3 px-4">Reporter</th>
                      <th className="text-left text-sm font-semibold text-slate-900 pb-3 px-4">Incident</th>
                      <th className="text-left text-sm font-semibold text-slate-900 pb-3 px-4">Platform</th>
                      <th className="text-left text-sm font-semibold text-slate-900 pb-3 px-4">Priority</th>
                      <th className="text-left text-sm font-semibold text-slate-900 pb-3 px-4">Status</th>
                      <th className="text-left text-sm font-semibold text-slate-900 pb-3 px-4">Evidence</th>
                      <th className="text-left text-sm font-semibold text-slate-900 pb-3 px-4">Submitted</th>
                      <th className="text-left text-sm font-semibold text-slate-900 pb-3 px-4">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {filteredReports.map((report) => (
                      <tr key={report.id} className="border-b border-slate-200 hover:bg-slate-50">
                        <td className="px-4 py-3">
                          <Checkbox
                            checked={selectedReports.has(report.id)}
                            onCheckedChange={() => handleSelectReport(report.id)}
                          />
                        </td>
                        <td className="px-4 py-3 text-sm font-mono font-bold text-slate-900">{report.case_id}</td>
                        <td className="px-4 py-3 text-sm text-slate-600">{report.reporter_name || '—'}</td>
                        <td className="px-4 py-3 text-sm text-slate-600">{report.category}</td>
                        <td className="px-4 py-3 text-sm text-slate-600">{report.source_platform}</td>
                        <td className="px-4 py-3 text-sm">
                          <PriorityBadge priority={report.priority} />
                        </td>
                        <td className="px-4 py-3 text-sm">
                          <StatusBadge status={report.status} />
                        </td>
                        <td className="px-4 py-3 text-sm text-slate-600">{report.evidence_count ?? 0} file(s)</td>
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
