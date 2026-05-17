'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { Navbar } from '@/components/navbar'
import { Footer } from '@/components/footer'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { isAuthenticated } from '@/lib/auth'
import apiFetch from '@/lib/api'
import { ArrowLeft, Send, CheckCircle, AlertCircle, Shield, User, Phone, MapPin } from 'lucide-react'

const INCIDENT_CATEGORIES = [
  { value: 'photo_leak', label: 'Photo / Video Leak' },
  { value: 'sextortion', label: 'Sextortion' },
  { value: 'bank_fraud', label: 'Bank Fraud' },
  { value: 'account_hack', label: 'Account Hack' },
  { value: 'impersonation', label: 'Impersonation' },
  { value: 'cyberbullying', label: 'Cyberbullying' },
  { value: 'harassment', label: 'Harassment' },
  { value: 'scam', label: 'Online Scam' },
  { value: 'blackmail', label: 'Blackmail' },
  { value: 'general', label: 'Other Cybercrime' },
]

const PLATFORMS = [
  'Facebook',
  'Instagram',
  'WhatsApp',
  'Telegram',
  'TikTok',
  'Twitter / X',
  'YouTube',
  'Snapchat',
  'Email',
  'Website',
  'Phone / SMS',
  'Other',
]

export default function NewReportPage() {
  const router = useRouter()
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [success, setSuccess] = useState<{ caseId: string } | null>(null)
  const [error, setError] = useState('')

  const [form, setForm] = useState({
    category: '',
    incident_description: '',
    source_platform: '',
    incident_date: '',
    victim_name: '',
    victim_phone: '',
    victim_address: '',
    guardian_phone: '',
  })

  const update = (field: string, value: string) => {
    setForm(prev => ({ ...prev, [field]: value }))
    setError('')
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')

    if (!isAuthenticated()) {
      router.push('/login')
      return
    }

    if (!form.category) {
      setError('Please select an incident type.')
      return
    }
    if (form.incident_description.length < 10) {
      setError('Please provide a detailed description (at least 10 characters).')
      return
    }

    setIsSubmitting(true)
    try {
      const categoryLabel = INCIDENT_CATEGORIES.find(c => c.value === form.category)?.label || form.category
      const payload: Record<string, any> = {
        title: `${categoryLabel} Report`,
        category: form.category,
        incident_description: form.incident_description,
      }
      if (form.source_platform) payload.source_platform = form.source_platform
      if (form.incident_date) payload.incident_date = new Date(form.incident_date).toISOString()
      if (form.victim_name.trim()) payload.victim_name = form.victim_name.trim()
      if (form.victim_phone.trim()) payload.victim_phone = form.victim_phone.trim()
      if (form.victim_address.trim()) payload.victim_address = form.victim_address.trim()
      if (form.guardian_phone.trim()) payload.guardian_phone = form.guardian_phone.trim()

      const result = await apiFetch<any>('/complaints', {
        method: 'POST',
        body: JSON.stringify(payload),
      })
      setSuccess({ caseId: result.case_id })
    } catch (err: any) {
      setError(err?.message || 'Failed to submit report. Please try again.')
    } finally {
      setIsSubmitting(false)
    }
  }

  if (success) {
    return (
      <>
        <Navbar />
        <main className="min-h-screen bg-gradient-to-b from-slate-50 to-slate-100 py-12">
          <div className="max-w-2xl mx-auto px-4">
            <Card className="border-green-200 bg-green-50">
              <CardContent className="pt-12 pb-12 text-center">
                <CheckCircle className="w-16 h-16 text-green-600 mx-auto mb-6" />
                <h2 className="text-2xl font-bold text-slate-900 mb-2">Report Submitted Successfully</h2>
                <p className="text-slate-600 mb-2">Your tracking ID is:</p>
                <p className="text-3xl font-mono font-bold text-cyan-700 mb-6">{success.caseId}</p>
                <p className="text-sm text-slate-500 mb-8">
                  Save this ID to track the status of your report. Our team will review it and contact you if needed.
                </p>
                <div className="flex gap-4 justify-center">
                  <Button asChild className="bg-cyan-600 hover:bg-cyan-700">
                    <Link href="/dashboard">Go to Dashboard</Link>
                  </Button>
                  <Button asChild variant="outline">
                    <Link href="/reports">View My Reports</Link>
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

  return (
    <>
      <Navbar />
      <main className="min-h-screen bg-gradient-to-b from-slate-50 to-slate-100 py-12">
        <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8">
          {/* Header */}
          <Button asChild variant="ghost" className="mb-6">
            <Link href="/dashboard" className="flex items-center gap-2">
              <ArrowLeft className="w-4 h-4" />
              Back to Dashboard
            </Link>
          </Button>

          <div className="mb-8">
            <h1 className="text-4xl font-bold text-slate-900 mb-2">Submit a Report</h1>
            <p className="text-slate-600">
              Fill in the details below to report a cybercrime incident. All information is kept confidential.
            </p>
          </div>

          {error && (
            <Alert className="mb-6 bg-red-50 border-red-200">
              <AlertCircle className="h-4 w-4 text-red-600" />
              <AlertDescription className="text-red-800">{error}</AlertDescription>
            </Alert>
          )}

          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Incident Details */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Shield className="w-5 h-5 text-cyan-600" />
                  Incident Details
                </CardTitle>
                <CardDescription>Tell us what happened</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="category">
                    Incident Type <span className="text-red-500">*</span>
                  </Label>
                  <Select value={form.category} onValueChange={(v) => update('category', v)}>
                    <SelectTrigger id="category">
                      <SelectValue placeholder="Select the type of incident" />
                    </SelectTrigger>
                    <SelectContent>
                      {INCIDENT_CATEGORIES.map(cat => (
                        <SelectItem key={cat.value} value={cat.value}>{cat.label}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="description">
                    Description <span className="text-red-500">*</span>
                  </Label>
                  <Textarea
                    id="description"
                    placeholder="Describe what happened in detail. Include any relevant information that could help our team investigate."
                    value={form.incident_description}
                    onChange={(e) => update('incident_description', e.target.value)}
                    className="min-h-32"
                  />
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="platform">Platform</Label>
                    <Select value={form.source_platform} onValueChange={(v) => update('source_platform', v)}>
                      <SelectTrigger id="platform">
                        <SelectValue placeholder="Where did it happen?" />
                      </SelectTrigger>
                      <SelectContent>
                        {PLATFORMS.map(p => (
                          <SelectItem key={p} value={p}>{p}</SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="incident_date">When did it happen?</Label>
                    <Input
                      id="incident_date"
                      type="date"
                      value={form.incident_date}
                      onChange={(e) => update('incident_date', e.target.value)}
                      max={new Date().toISOString().split('T')[0]}
                    />
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Victim Information */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <User className="w-5 h-5 text-cyan-600" />
                  Your Information
                </CardTitle>
                <CardDescription>
                  Help us contact you about this case. This information is kept confidential.
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="victim_name" className="flex items-center gap-2">
                      <User className="w-4 h-4 text-slate-400" />
                      Full Name
                    </Label>
                    <Input
                      id="victim_name"
                      placeholder="Your full name"
                      value={form.victim_name}
                      onChange={(e) => update('victim_name', e.target.value)}
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="victim_phone" className="flex items-center gap-2">
                      <Phone className="w-4 h-4 text-slate-400" />
                      Phone Number
                    </Label>
                    <Input
                      id="victim_phone"
                      placeholder="e.g. 077 123 4567"
                      value={form.victim_phone}
                      onChange={(e) => update('victim_phone', e.target.value)}
                    />
                  </div>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="victim_address" className="flex items-center gap-2">
                    <MapPin className="w-4 h-4 text-slate-400" />
                    Address
                  </Label>
                  <Input
                    id="victim_address"
                    placeholder="Your address (optional)"
                    value={form.victim_address}
                    onChange={(e) => update('victim_address', e.target.value)}
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="guardian_phone" className="flex items-center gap-2">
                    <Phone className="w-4 h-4 text-slate-400" />
                    Trusted Contact / Guardian Phone
                  </Label>
                  <Input
                    id="guardian_phone"
                    placeholder="A trusted person we can reach (optional)"
                    value={form.guardian_phone}
                    onChange={(e) => update('guardian_phone', e.target.value)}
                  />
                </div>
              </CardContent>
            </Card>

            {/* Submit */}
            <div className="flex gap-4 justify-end">
              <Button type="button" variant="outline" onClick={() => router.push('/dashboard')}>
                Cancel
              </Button>
              <Button
                type="submit"
                disabled={isSubmitting}
                className="bg-cyan-600 hover:bg-cyan-700 px-8"
              >
                {isSubmitting ? (
                  <span className="flex items-center gap-2">
                    <span className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                    Submitting...
                  </span>
                ) : (
                  <span className="flex items-center gap-2">
                    <Send className="w-4 h-4" />
                    Submit Report
                  </span>
                )}
              </Button>
            </div>
          </form>
        </div>
      </main>
      <Footer />
    </>
  )
}
