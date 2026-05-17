'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { Navbar } from '@/components/navbar'
import { Footer } from '@/components/footer'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { isAuthenticated, getStoredRole } from '@/lib/auth'
import apiFetch from '@/lib/api'
import { FileText, Plus, Clock, CheckCircle, AlertCircle, MessageSquare, PenLine } from 'lucide-react'

export default function DashboardPage() {
  const [reports, setReports] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [stats, setStats] = useState({
    total: 0,
    pending: 0,
    inReview: 0,
    needsInfo: 0,
    closed: 0,
  })
  const router = useRouter()

  useEffect(() => {
    if (!isAuthenticated() || getStoredRole() !== 'user') {
      router.push('/login')
      return
    }

    loadComplaints()
  }, [router])

  const loadComplaints = async () => {
    try {
      const data = await apiFetch<any[]>('/complaints')
      setReports(data)
      setStats({
        total: data.length,
        pending: data.filter((r: any) => r.status === 'pending').length,
        inReview: data.filter((r: any) => r.status === 'under_review').length,
        needsInfo: data.filter((r: any) => r.status === 'need_more_info').length,
        closed: data.filter((r: any) => r.status === 'closed').length,
      })
    } catch (err) {
      console.error('Failed to load complaints:', err)
    } finally {
      setLoading(false)
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'pending':
        return 'bg-yellow-100 text-yellow-800'
      case 'under_review':
        return 'bg-blue-100 text-blue-800'
      case 'need_more_info':
        return 'bg-orange-100 text-orange-800'
      case 'closed':
        return 'bg-green-100 text-green-800'
      default:
        return 'bg-slate-100 text-slate-800'
    }
  }

  const getStatusLabel = (status: string) => {
    switch (status) {
      case 'pending':
        return 'Pending Review'
      case 'under_review':
        return 'Under Review'
      case 'need_more_info':
        return 'Needs More Info'
      case 'closed':
        return 'Closed'
      default:
        return status
    }
  }

  if (loading) {
    return (
      <>
        <Navbar />
        <main className="min-h-screen bg-gradient-to-b from-slate-50 to-slate-100 py-12">
          <div className="max-w-7xl mx-auto px-4">Loading...</div>
        </main>
        <Footer />
      </>
    )
  }

  return (
    <>
      <Navbar />
      <main className="min-h-screen bg-gradient-to-b from-slate-50 to-slate-100 py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          {/* Header */}
          <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 mb-8">
            <div>
              <h1 className="text-4xl font-bold text-slate-900">Dashboard</h1>
              <p className="text-slate-600 mt-2">Manage and track your reports</p>
            </div>
            <div className="flex gap-3">
              <Button asChild className="bg-cyan-600 hover:bg-cyan-700">
                <Link href="/chatbot" className="flex items-center gap-2">
                  <MessageSquare className="w-4 h-4" />
                  Report via Chatbot
                </Link>
              </Button>
              <Button asChild variant="outline" className="border-cyan-600 text-cyan-700 hover:bg-cyan-50">
                <Link href="/reports/new" className="flex items-center gap-2">
                  <PenLine className="w-4 h-4" />
                  Manual Report
                </Link>
              </Button>
            </div>
          </div>

          {/* Stats Grid */}
          <div className="grid grid-cols-1 md:grid-cols-5 gap-4 mb-8">
            {[
              { label: 'Total Reports', value: stats.total, icon: FileText, color: 'bg-slate-100' },
              { label: 'Pending', value: stats.pending, icon: AlertCircle, color: 'bg-yellow-100' },
              { label: 'In Review', value: stats.inReview, icon: Clock, color: 'bg-blue-100' },
              { label: 'Awaiting Info', value: stats.needsInfo, icon: MessageSquare, color: 'bg-orange-100' },
              { label: 'Closed', value: stats.closed, icon: CheckCircle, color: 'bg-green-100' },
            ].map((stat, index) => {
              const Icon = stat.icon
              return (
                <Card key={index} className={`${stat.color}`}>
                  <CardContent className="pt-6">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm text-slate-600">{stat.label}</p>
                        <p className="text-3xl font-bold text-slate-900 mt-2">{stat.value}</p>
                      </div>
                      <Icon className="w-8 h-8 text-slate-400 opacity-50" />
                    </div>
                  </CardContent>
                </Card>
              )
            })}
          </div>

          {/* Reports List */}
          <div className="space-y-6">
            <div>
              <h2 className="text-2xl font-bold text-slate-900 mb-4">Your Reports</h2>
              
              {reports.length === 0 ? (
                <Card className="border-dashed border-slate-300">
                  <CardContent className="pt-12 pb-12 text-center">
                    <FileText className="w-12 h-12 text-slate-300 mx-auto mb-4" />
                    <h3 className="text-lg font-semibold text-slate-900 mb-2">No Reports Yet</h3>
                    <p className="text-slate-600 mb-6">
                      You haven't created any reports yet. Use the chatbot for guided help, or fill in a form manually.
                    </p>
                    <div className="flex gap-3 justify-center">
                      <Button asChild className="bg-cyan-600 hover:bg-cyan-700">
                        <Link href="/chatbot">Report via Chatbot</Link>
                      </Button>
                      <Button asChild variant="outline">
                        <Link href="/reports/new">Fill Manual Form</Link>
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              ) : (
                <div className="space-y-4">
                  {reports.map((report) => (
                    <Link key={report.id} href={`/reports/${report.id}`}>
                      <Card className="hover:border-cyan-300 hover:shadow-md transition-all cursor-pointer">
                        <CardContent className="pt-6">
                          <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
                            <div className="flex-1">
                              <div className="flex items-center gap-4 mb-2">
                                <h3 className="font-semibold text-slate-900 text-lg">{report.case_id}</h3>
                                <Badge className={getStatusColor(report.status)}>
                                  {getStatusLabel(report.status)}
                                </Badge>
                                {report.priority === 'high' && (
                                  <Badge className="bg-red-100 text-red-800">High Priority</Badge>
                                )}
                                {report.priority === 'urgent' && (
                                  <Badge className="bg-red-100 text-red-800">Urgent</Badge>
                                )}
                              </div>
                              <p className="text-slate-600 mb-2">{report.category} {report.source_platform ? `• ${report.source_platform}` : ''}</p>
                              <p className="text-sm text-slate-500">
                                Submitted: {new Date(report.created_at).toLocaleDateString()}
                              </p>
                            </div>
                          </div>
                        </CardContent>
                      </Card>
                    </Link>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Quick Actions */}
          <Card className="mt-8 bg-cyan-50 border-cyan-200">
            <CardHeader>
              <CardTitle>Need Help?</CardTitle>
              <CardDescription>Quick links to resources and support</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <Button asChild variant="outline">
                  <Link href="/resources">Safety Resources</Link>
                </Button>
                <Button asChild variant="outline">
                  <Link href="/chatbot">Chat with Support</Link>
                </Button>
                <Button asChild variant="outline">
                  <Link href="/login">View Account Settings</Link>
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </main>
      <Footer />
    </>
  )
}
