'use client'

import { useEffect, useState } from 'react'
import { useParams, useRouter } from 'next/navigation'
import Link from 'next/link'
import { Navbar } from '@/components/navbar'
import { Footer } from '@/components/footer'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { Label } from '@/components/ui/label'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { isAuthenticated, getStoredRole, fetchCurrentUser } from '@/lib/auth'
import apiFetch from '@/lib/api'
import { ArrowLeft, Download, Eye, FileText, MessageSquare, AlertCircle, CheckCircle, Lock } from 'lucide-react'

export default function ReportDetailPage() {
  const params = useParams()
  const router = useRouter()
  const complaintId = params.id as string

  const [report, setReport] = useState<any>(null)
  const [evidence, setEvidence] = useState<any[]>([])
  const [messages, setMessages] = useState<any[]>([])
  const [messageText, setMessageText] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [currentUserId, setCurrentUserId] = useState<number | null>(null)

  useEffect(() => {
    if (!isAuthenticated() || getStoredRole() !== 'user') {
      router.push('/login')
      return
    }
    loadData()
  }, [complaintId, router])

  const loadData = async () => {
    try {
      const [complaint, evidenceData, messagesData, user] = await Promise.all([
        apiFetch(`/complaints/${complaintId}`),
        apiFetch(`/evidence/${complaintId}`),
        apiFetch(`/messages/${complaintId}`),
        fetchCurrentUser(),
      ])
      setReport(complaint)
      setEvidence(evidenceData)
      setMessages(messagesData)
      if (user) setCurrentUserId(user.id)
    } catch (err) {
      console.error('Failed to load report:', err)
      router.push('/reports')
    }
  }

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!messageText.trim()) return

    setIsLoading(true)
    try {
      const newMsg = await apiFetch(`/messages/${complaintId}`, {
        method: 'POST',
        body: JSON.stringify({ body: messageText }),
      })
      setMessages(prev => [...prev, newMsg])
      setMessageText('')
    } catch (err) {
      console.error('Failed to send message:', err)
    } finally {
      setIsLoading(false)
    }
  }

  const handleEvidenceUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.currentTarget.files
    if (!files || files.length === 0) return

    setIsLoading(true)
    try {
      const formData = new FormData()
      formData.append('file', files[0])
      const newEvidence = await apiFetch(`/evidence/${complaintId}`, {
        method: 'POST',
        body: formData,
      })
      setEvidence(prev => [...prev, newEvidence])
    } catch (err) {
      console.error('Failed to upload evidence:', err)
    } finally {
      setIsLoading(false)
      e.currentTarget.value = ''
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

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
  }

  if (!report) {
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
          <Button asChild variant="ghost" className="mb-6">
            <Link href="/reports" className="flex items-center gap-2">
              <ArrowLeft className="w-4 h-4" />
              Back to Reports
            </Link>
          </Button>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Left Column - Main Content */}
            <div className="lg:col-span-2 space-y-6">
              {/* Case Details */}
              <Card>
                <CardHeader>
                  <div className="flex justify-between items-start">
                    <div>
                      <CardTitle className="text-2xl">{report.case_id}</CardTitle>
                      <CardDescription>{report.category}</CardDescription>
                    </div>
                    <Badge className={getStatusColor(report.status)}>
                      {getStatusLabel(report.status)}
                    </Badge>
                  </div>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <p className="text-sm text-slate-600">Platform</p>
                      <p className="font-semibold text-slate-900">{report.source_platform || 'N/A'}</p>
                    </div>
                    <div>
                      <p className="text-sm text-slate-600">Priority</p>
                      <Badge className={report.priority === 'high' || report.priority === 'urgent' ? 'bg-red-100 text-red-800' : report.priority === 'medium' ? 'bg-orange-100 text-orange-800' : 'bg-green-100 text-green-800'}>
                        {report.priority.charAt(0).toUpperCase() + report.priority.slice(1)}
                      </Badge>
                    </div>
                    <div>
                      <p className="text-sm text-slate-600">Submitted</p>
                      <p className="font-semibold text-slate-900">
                        {new Date(report.created_at).toLocaleDateString()}
                      </p>
                    </div>
                    <div>
                      <p className="text-sm text-slate-600">Assigned To</p>
                      <p className="font-semibold text-slate-900">
                        {report.assigned_admin_id ? 'Reviewer Assigned' : 'Not Yet Assigned'}
                      </p>
                    </div>
                  </div>

                  <div className="border-t border-slate-200 pt-4">
                    <p className="text-sm text-slate-600 mb-2">Description</p>
                    <p className="text-slate-900">{report.incident_description}</p>
                  </div>
                </CardContent>
              </Card>

              {/* Status Timeline */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <AlertCircle className="w-5 h-5" />
                    Case Timeline
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div className="flex gap-4">
                      <div className="text-center">
                        <div className="w-8 h-8 rounded-full bg-green-100 flex items-center justify-center">
                          <CheckCircle className="w-5 h-5 text-green-600" />
                        </div>
                      </div>
                      <div className="flex-1 pb-4 border-l-2 border-slate-300 pl-4">
                        <p className="font-semibold text-slate-900">Report Submitted</p>
                        <p className="text-sm text-slate-600">
                          {new Date(report.created_at).toLocaleDateString()} at{' '}
                          {new Date(report.created_at).toLocaleTimeString()}
                        </p>
                      </div>
                    </div>
                    {report.assigned_admin_id && (
                      <div className="flex gap-4">
                        <div className="text-center">
                          <div className="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center">
                            <CheckCircle className="w-5 h-5 text-blue-600" />
                          </div>
                        </div>
                        <div className="flex-1 pb-4 border-l-2 border-slate-300 pl-4">
                          <p className="font-semibold text-slate-900">Review Started</p>
                          <p className="text-sm text-slate-600">Case assigned to reviewer</p>
                        </div>
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>

              {/* Evidence */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <FileText className="w-5 h-5" />
                    Evidence ({evidence.length})
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  {evidence.length === 0 ? (
                    <p className="text-slate-600 text-sm">No evidence uploaded yet</p>
                  ) : (
                    <div className="space-y-3">
                      {evidence.map((file) => (
                        <div key={file.id} className="border border-slate-200 rounded p-3 flex items-center justify-between hover:bg-slate-50">
                          <div className="flex-1">
                            <p className="font-medium text-slate-900">{file.original_file_name}</p>
                            <p className="text-xs text-slate-600 mt-1">
                              {formatFileSize(file.file_size)} • {new Date(file.created_at).toLocaleDateString()}
                            </p>
                          </div>
                          <div className="flex gap-2">
                            <Button size="sm" variant="ghost" className="h-8">
                              <Eye className="w-4 h-4" />
                            </Button>
                            <Button size="sm" variant="ghost" className="h-8">
                              <Download className="w-4 h-4" />
                            </Button>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}

                  <div className="border-t border-slate-200 pt-4">
                    <Label htmlFor="evidence" className="block mb-2 font-medium">
                      Upload More Evidence
                    </Label>
                    <Input
                      id="evidence"
                      type="file"
                      onChange={handleEvidenceUpload}
                      disabled={isLoading}
                      className="cursor-pointer"
                    />
                    <p className="text-xs text-slate-600 mt-2">Max 50MB per file</p>
                  </div>
                </CardContent>
              </Card>

              {/* Messages */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <MessageSquare className="w-5 h-5" />
                    Secure Inbox
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <Alert className="mb-4 bg-cyan-50 border-cyan-200">
                    <Lock className="h-4 w-4" />
                    <AlertDescription className="text-cyan-900">
                      All messages are encrypted and secure. Only you and assigned reviewers can see these messages.
                    </AlertDescription>
                  </Alert>

                  <div className="space-y-4 mb-6 max-h-96 overflow-y-auto">
                    {messages.filter((m: any) => !m.is_internal).map((msg: any) => {
                      const isMe = msg.sender_id === currentUserId
                      return (
                        <div key={msg.id} className={`flex gap-3 ${isMe ? 'flex-row-reverse' : ''}`}>
                          <div className={`w-8 h-8 rounded-full flex items-center justify-center text-white text-xs font-bold ${isMe ? 'bg-cyan-600' : 'bg-slate-600'}`}>
                            {isMe ? 'Y' : 'A'}
                          </div>
                          <div className={isMe ? 'items-end' : 'items-start'}>
                            <p className="text-xs text-slate-600 mb-1">{isMe ? 'You' : 'Reviewer'}</p>
                            <div className={`rounded-lg px-4 py-2 ${isMe ? 'bg-cyan-100 text-cyan-900' : 'bg-slate-100 text-slate-900'}`}>
                              <p className="text-sm">{msg.body}</p>
                            </div>
                            <p className="text-xs text-slate-500 mt-1">
                              {new Date(msg.created_at).toLocaleDateString()} {new Date(msg.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                            </p>
                          </div>
                        </div>
                      )
                    })}
                  </div>

                  <form onSubmit={handleSendMessage} className="space-y-3 border-t border-slate-200 pt-4">
                    <Textarea
                      placeholder="Send a message to your assigned reviewer..."
                      value={messageText}
                      onChange={(e) => setMessageText(e.target.value)}
                      disabled={isLoading}
                      className="min-h-24"
                    />
                    <Button type="submit" disabled={isLoading || !messageText.trim()} className="w-full bg-cyan-600 hover:bg-cyan-700">
                      {isLoading ? 'Sending...' : 'Send Message'}
                    </Button>
                  </form>
                </CardContent>
              </Card>
            </div>

            {/* Right Column - Quick Info */}
            <div className="space-y-6">
              <Card className="bg-cyan-50 border-cyan-200">
                <CardHeader>
                  <CardTitle className="text-base">Status Updates</CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  {report.status === 'pending' && (
                    <p className="text-sm text-cyan-900">
                      Your report is pending initial review. We'll assign it to a reviewer within 24 hours.
                    </p>
                  )}
                  {report.status === 'under_review' && (
                    <p className="text-sm text-cyan-900">
                      A specialized reviewer has been assigned to your case and is actively investigating.
                    </p>
                  )}
                  {report.status === 'need_more_info' && (
                    <Alert className="bg-orange-50 border-orange-200 p-3">
                      <AlertCircle className="h-4 w-4 text-orange-600" />
                      <AlertDescription className="text-orange-900 text-sm">
                        Your assigned reviewer needs additional information. Please check your messages.
                      </AlertDescription>
                    </Alert>
                  )}
                  {report.status === 'escalated' && (
                    <Alert className="bg-red-50 border-red-200 p-3">
                      <AlertCircle className="h-4 w-4 text-red-600" />
                      <AlertDescription className="text-red-900 text-sm">
                        Your case has been escalated for priority handling.
                      </AlertDescription>
                    </Alert>
                  )}
                  {report.status === 'closed' && (
                    <Alert className="bg-green-50 border-green-200 p-3">
                      <CheckCircle className="h-4 w-4 text-green-600" />
                      <AlertDescription className="text-green-900 text-sm">
                        Your case has been closed. Check your messages for final resolution details.
                      </AlertDescription>
                    </Alert>
                  )}
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="text-base">Need Help?</CardTitle>
                </CardHeader>
                <CardContent className="space-y-2">
                  <Button asChild variant="outline" className="w-full justify-start">
                    <Link href="/resources">View Resources</Link>
                  </Button>
                  <Button asChild variant="outline" className="w-full justify-start">
                    <Link href="/resources/getting-support">Legal Options</Link>
                  </Button>
                </CardContent>
              </Card>
            </div>
          </div>
        </div>
      </main>
      <Footer />
    </>
  )
}
