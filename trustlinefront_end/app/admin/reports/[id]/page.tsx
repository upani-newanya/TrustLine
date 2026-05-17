'use client'

import { useEffect, useState } from 'react'
import { useParams, useRouter } from 'next/navigation'
import Link from 'next/link'
import { AdminSidebar } from '@/components/admin-sidebar'
import { AdminTopbar } from '@/components/admin-topbar'
import { StatusBadge } from '@/components/status-badge'
import { PriorityBadge } from '@/components/priority-badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Textarea } from '@/components/ui/textarea'
import { Alert, AlertDescription } from '@/components/ui/alert'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { 
  getCurrentUserRole,
  fetchCurrentUser,
} from '@/lib/auth'
import { apiFetch } from '@/lib/api'
import { ArrowLeft, Download, Eye, FileText, MessageSquare, AlertCircle, Lock, Clock, Shield } from 'lucide-react'

export default function AdminReportDetailPage() {
  const params = useParams()
  const router = useRouter()
  const reportId = params.id as string

  const [report, setReport] = useState<any>(null)
  const [evidence, setEvidence] = useState<any[]>([])
  const [messages, setMessages] = useState<any[]>([])
  const [internalNote, setInternalNote] = useState('')
  const [messageText, setMessageText] = useState('')
  const [newStatus, setNewStatus] = useState('')
  const [newPriority, setNewPriority] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [selectedTemplate, setSelectedTemplate] = useState('')
  const [adminName, setAdminName] = useState('Admin')

  const messageTemplates = [
    { id: 'evidence-request', label: 'Request More Evidence', text: 'We need additional evidence to proceed with the investigation. Please upload the following: [specific details]' },
    { id: 'safety-steps', label: 'Provide Safety Steps', text: 'Here are some immediate steps you can take to protect yourself: 1) Block the user, 2) Report to the platform, 3) Contact law enforcement if needed' },
    { id: 'case-update', label: 'Case Update', text: 'We have made progress on your case. Our team is actively investigating and will provide a full update within 48 hours.' },
    { id: 'legal-info', label: 'Legal Information', text: 'Based on the information provided, you may have legal options available. We recommend consulting with a lawyer for specific advice.' },
  ]

  useEffect(() => {
    const role = getCurrentUserRole()
    if (role !== 'admin') {
      router.push('/login')
      return
    }

    async function load() {
      try {
        const [complaint, evidenceData, messagesData, user] = await Promise.all([
          apiFetch<any>(`/admin/complaints/${reportId}`),
          apiFetch<any[]>(`/evidence/${reportId}`),
          apiFetch<any[]>(`/messages/${reportId}`),
          fetchCurrentUser(),
        ])
        if (!complaint) {
          router.push('/admin/reports')
          return
        }
        setReport(complaint)
        setEvidence(evidenceData)
        setMessages(messagesData)
        setNewStatus(complaint.status)
        setNewPriority(complaint.priority)
        if (user) setAdminName(user.full_name)
      } catch {
        router.push('/admin/reports')
      }
    }
    load()
  }, [reportId, router])

  const handleStatusChange = async (status: string) => {
    setNewStatus(status)
    try {
      const updated = await apiFetch<any>(`/admin/complaints/${reportId}/status`, {
        method: 'PATCH',
        body: JSON.stringify({ status }),
      })
      setReport(updated)
    } catch (err) {
      console.error('Failed to update status', err)
    }
  }

  const handlePriorityChange = async (priority: string) => {
    setNewPriority(priority)
    try {
      const updated = await apiFetch<any>(`/admin/complaints/${reportId}/priority`, {
        method: 'PATCH',
        body: JSON.stringify({ priority }),
      })
      setReport(updated)
    } catch (err) {
      console.error('Failed to update priority', err)
    }
  }

  const handleAddInternalNote = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!internalNote.trim() || !report) return

    setIsLoading(true)
    try {
      await apiFetch(`/admin/complaints/${reportId}/internal-note`, {
        method: 'POST',
        body: JSON.stringify({ content: internalNote }),
      })
      // Reload complaint to get updated notes
      const updated = await apiFetch<any>(`/admin/complaints/${reportId}`)
      setReport(updated)
      setInternalNote('')
    } catch (err) {
      console.error('Failed to add internal note', err)
    }
    setIsLoading(false)
  }

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault()
    const messageContent = selectedTemplate
      ? messageTemplates.find(t => t.id === selectedTemplate)?.text || messageText
      : messageText

    if (!messageContent.trim() || !report) return

    setIsLoading(true)
    try {
      await apiFetch(`/messages/${reportId}`, {
        method: 'POST',
        body: JSON.stringify({ body: messageContent }),
      })
      // Reload messages
      const updatedMsgs = await apiFetch<any[]>(`/messages/${reportId}`)
      setMessages(updatedMsgs)
      setMessageText('')
      setSelectedTemplate('')
    } catch (err) {
      console.error('Failed to send message', err)
    }
    setIsLoading(false)
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
      <div className="min-h-screen bg-slate-50">
        <AdminSidebar />
        <AdminTopbar />
        <main className="ml-64 pt-20">
          <div className="max-w-7xl mx-auto px-8">Loading...</div>
        </main>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-slate-50">
      <AdminSidebar />
      <AdminTopbar />

      <main className="ml-64 pt-20 pb-12">
        <div className="max-w-7xl mx-auto px-8">
          {/* Header */}
          <Button asChild variant="ghost" className="mb-6">
            <Link href="/admin/reports" className="flex items-center gap-2">
              <ArrowLeft className="w-4 h-4" />
              Back to Reports
            </Link>
          </Button>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Main Content */}
            <div className="lg:col-span-2 space-y-6">
              {/* Case Header */}
              <Card>
                <CardHeader>
                  <div className="flex justify-between items-start">
                    <div>
                      <CardTitle className="text-2xl">{report.case_id}</CardTitle>
                      <CardDescription className="mt-2">
                        {report.reporter_name || 'Anonymous'} • {new Date(report.created_at).toLocaleDateString()}
                      </CardDescription>
                    </div>
                    <div className="flex gap-2">
                      <StatusBadge status={report.status} />
                      <PriorityBadge priority={report.priority} />
                    </div>
                  </div>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <p className="text-sm text-slate-600">Incident Type</p>
                      <p className="font-semibold text-slate-900">{report.category}</p>
                    </div>
                    <div>
                      <p className="text-sm text-slate-600">Platform</p>
                      <p className="font-semibold text-slate-900">{report.source_platform || '—'}</p>
                    </div>
                  </div>

                  <div className="border-t border-slate-200 pt-4">
                    <p className="text-sm text-slate-600 mb-2">Description</p>
                    <p className="text-slate-900">{report.incident_description}</p>
                  </div>
                </CardContent>
              </Card>

              {/* Victim / Reporter Information */}
              {(report.victim_name || report.victim_phone || report.victim_address || report.guardian_phone) && (
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Shield className="w-5 h-5" />
                      Victim Information
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="grid grid-cols-2 gap-4">
                      {report.victim_name && (
                        <div>
                          <p className="text-sm text-slate-600">Full Name</p>
                          <p className="font-semibold text-slate-900">{report.victim_name}</p>
                        </div>
                      )}
                      {report.victim_phone && (
                        <div>
                          <p className="text-sm text-slate-600">Phone Number</p>
                          <p className="font-semibold text-slate-900">{report.victim_phone}</p>
                        </div>
                      )}
                      {report.victim_address && (
                        <div className="col-span-2">
                          <p className="text-sm text-slate-600">Address</p>
                          <p className="font-semibold text-slate-900">{report.victim_address}</p>
                        </div>
                      )}
                      {report.guardian_phone && (
                        <div>
                          <p className="text-sm text-slate-600">Guardian / Trusted Contact</p>
                          <p className="font-semibold text-slate-900">{report.guardian_phone}</p>
                        </div>
                      )}
                    </div>
                  </CardContent>
                </Card>
              )}

              {/* Collected Details from Chatbot */}
              {report.collected_fields && Object.keys(report.collected_fields).length > 0 && (
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <FileText className="w-5 h-5" />
                      Chatbot Collected Details
                    </CardTitle>
                    <CardDescription>All information gathered during the chatbot conversation</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="grid grid-cols-2 gap-4">
                      {Object.entries(report.collected_fields as Record<string, string>)
                        .filter(([key]) => !['victim_name', 'victim_phone', 'victim_address', 'guardian_phone', 'incident_description'].includes(key))
                        .map(([key, value]) => (
                          <div key={key} className={String(value).length > 60 ? 'col-span-2' : ''}>
                            <p className="text-sm text-slate-600">{key.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())}</p>
                            <p className="font-semibold text-slate-900">{String(value)}</p>
                          </div>
                        ))}
                    </div>
                  </CardContent>
                </Card>
              )}

              {/* Evidence */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <FileText className="w-5 h-5" />
                    Evidence ({evidence.length})
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  {evidence.length === 0 ? (
                    <p className="text-slate-600 text-sm">No evidence uploaded</p>
                  ) : (
                    evidence.map((file) => (
                      <div key={file.id} className="border border-slate-200 rounded p-4 flex items-start justify-between hover:bg-slate-50">
                        <div className="flex-1">
                          <div className="flex items-center gap-3 mb-2">
                            <FileText className="w-5 h-5 text-slate-400" />
                            <div>
                              <p className="font-medium text-slate-900">{file.original_file_name}</p>
                              <p className="text-xs text-slate-600">
                                {formatFileSize(file.file_size)} • {new Date(file.uploaded_at).toLocaleDateString()}
                              </p>
                            </div>
                          </div>
                          {file.is_sensitive && (
                            <Badge className="bg-red-100 text-red-800 text-xs">Sensitive Content</Badge>
                          )}
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
                    ))
                  )}
                </CardContent>
              </Card>

              {/* Messages */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <MessageSquare className="w-5 h-5" />
                    Secure Messaging
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <Alert className="mb-4 bg-cyan-50 border-cyan-200">
                    <Lock className="h-4 w-4" />
                    <AlertDescription className="text-cyan-900">
                      All messages are encrypted. Only you and the reporter can see these messages.
                    </AlertDescription>
                  </Alert>

                  <div className="space-y-4 mb-6 max-h-96 overflow-y-auto">
                    {messages.filter((m: any) => !m.is_internal).map((msg: any) => {
                      const isAdmin = msg.sender_role === 'admin'
                      return (
                      <div key={msg.id} className={`flex gap-3 ${isAdmin ? 'flex-row-reverse' : ''}`}>
                        <div className={`w-8 h-8 rounded-full flex items-center justify-center text-white text-xs font-bold ${isAdmin ? 'bg-cyan-600' : 'bg-slate-600'}`}>
                          {(msg.sender_name || '?').charAt(0)}
                        </div>
                        <div>
                          <p className="text-xs text-slate-600 mb-1">{msg.sender_name || 'User'}</p>
                          <div className={`rounded-lg px-4 py-2 ${isAdmin ? 'bg-cyan-100 text-cyan-900' : 'bg-slate-100 text-slate-900'}`}>
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
                    <Select value={selectedTemplate} onValueChange={setSelectedTemplate}>
                      <SelectTrigger>
                        <SelectValue placeholder="Use template or write custom message..." />
                      </SelectTrigger>
                      <SelectContent>
                        {messageTemplates.map(t => (
                          <SelectItem key={t.id} value={t.id}>{t.label}</SelectItem>
                        ))}
                      </SelectContent>
                    </Select>

                    {!selectedTemplate && (
                      <Textarea
                        placeholder="Write your message..."
                        value={messageText}
                        onChange={(e) => setMessageText(e.target.value)}
                        disabled={isLoading}
                        className="min-h-24"
                      />
                    )}

                    <Button type="submit" disabled={isLoading || (!selectedTemplate && !messageText.trim())} className="w-full bg-cyan-600 hover:bg-cyan-700">
                      Send Message
                    </Button>
                  </form>
                </CardContent>
              </Card>
            </div>

            {/* Right Sidebar */}
            <div className="space-y-6">
              {/* Status & Priority Controls */}
              <Card>
                <CardHeader>
                  <CardTitle className="text-base flex items-center gap-2">
                    <Shield className="w-5 h-5" />
                    Case Controls
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="space-y-2">
                    <p className="text-sm font-medium text-slate-900">Status</p>
                    <Select value={newStatus} onValueChange={handleStatusChange}>
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="pending">Pending</SelectItem>
                        <SelectItem value="under_review">Under Review</SelectItem>
                        <SelectItem value="need_more_info">Need More Info</SelectItem>
                        <SelectItem value="escalated">Escalated</SelectItem>
                        <SelectItem value="closed">Closed</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <div className="space-y-2">
                    <p className="text-sm font-medium text-slate-900">Priority</p>
                    <Select value={newPriority} onValueChange={handlePriorityChange}>
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="low">Low</SelectItem>
                        <SelectItem value="medium">Medium</SelectItem>
                        <SelectItem value="high">High</SelectItem>
                        <SelectItem value="urgent">Urgent</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <div className="pt-2 border-t border-slate-200">
                    <p className="text-sm font-medium text-slate-900 mb-2">Assigned To</p>
                    <Badge className="bg-cyan-100 text-cyan-800">
                      {report.assigned_admin_id ? adminName : 'Unassigned'}
                    </Badge>
                  </div>
                </CardContent>
              </Card>

              {/* Internal Notes */}
              <Card>
                <CardHeader>
                  <CardTitle className="text-base">Internal Notes</CardTitle>
                  <CardDescription>Visible only to admin team</CardDescription>
                </CardHeader>
                <CardContent className="space-y-3">
                  <div className="max-h-48 overflow-y-auto space-y-3">
                    {(report.internal_notes || []).map((note: any) => (
                      <div key={note.id} className="bg-slate-100 rounded p-3">
                        <p className="text-xs font-medium text-slate-900">{note.admin_name || adminName}</p>
                        <p className="text-sm text-slate-700 mt-1">{note.content}</p>
                        <p className="text-xs text-slate-500 mt-2">
                          {new Date(note.created_at).toLocaleDateString()} {new Date(note.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                        </p>
                      </div>
                    ))}
                  </div>

                  <form onSubmit={handleAddInternalNote} className="space-y-2 border-t border-slate-200 pt-3">
                    <Textarea
                      placeholder="Add internal note..."
                      value={internalNote}
                      onChange={(e) => setInternalNote(e.target.value)}
                      disabled={isLoading}
                      className="min-h-20 text-sm"
                    />
                    <Button type="submit" disabled={isLoading || !internalNote.trim()} variant="outline" className="w-full">
                      Add Note
                    </Button>
                  </form>
                </CardContent>
              </Card>

              {/* Timeline */}
              <Card>
                <CardHeader>
                  <CardTitle className="text-base flex items-center gap-2">
                    <Clock className="w-5 h-5" />
                    Timeline
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  <div className="flex gap-3">
                    <div className="text-center">
                      <div className="w-8 h-8 rounded-full bg-green-100 flex items-center justify-center">
                        <span className="text-xs font-bold text-green-700">✓</span>
                      </div>
                    </div>
                    <div className="flex-1">
                      <p className="text-sm font-medium text-slate-900">Report Submitted</p>
                      <p className="text-xs text-slate-600">
                        {new Date(report.created_at).toLocaleDateString()}
                      </p>
                    </div>
                  </div>
                  {report.assigned_admin_id && (
                    <div className="flex gap-3">
                      <div className="text-center">
                        <div className="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center">
                          <span className="text-xs font-bold text-blue-700">✓</span>
                        </div>
                      </div>
                      <div className="flex-1">
                        <p className="text-sm font-medium text-slate-900">Assigned to Reviewer</p>
                        <p className="text-xs text-slate-600">{adminName}</p>
                      </div>
                    </div>
                  )}
                </CardContent>
              </Card>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}
