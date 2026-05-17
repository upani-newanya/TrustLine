'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { AdminSidebar } from '@/components/admin-sidebar'
import { AdminTopbar } from '@/components/admin-topbar'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Badge } from '@/components/ui/badge'
import { Switch } from '@/components/ui/switch'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { getCurrentUserRole } from '@/lib/auth'
import { apiFetch } from '@/lib/api'
import { Download, Eye, Flag, Search, AlertTriangle } from 'lucide-react'

export default function AdminEvidencePage() {
  const [evidence, setEvidence] = useState<any[]>([])
  const [filteredEvidence, setFilteredEvidence] = useState<any[]>([])
  const [searchQuery, setSearchQuery] = useState('')
  const [typeFilter, setTypeFilter] = useState('all')
  const router = useRouter()

  useEffect(() => {
    const role = getCurrentUserRole()
    if (role !== 'admin') {
      router.push('/login')
      return
    }

    async function load() {
      try {
        const data = await apiFetch<any[]>('/evidence')
        setEvidence(data)
        setFilteredEvidence(data)
      } catch (err) {
        console.error('Failed to load evidence', err)
      }
    }
    load()
  }, [router])

  useEffect(() => {
    let filtered = evidence

    if (typeFilter !== 'all') {
      filtered = filtered.filter(e => (e.file_type || '').split('/')[0] === typeFilter)
    }

    if (searchQuery) {
      filtered = filtered.filter(e =>
        (e.original_file_name || '').toLowerCase().includes(searchQuery.toLowerCase()) ||
        (e.complaint_id || '').toString().toLowerCase().includes(searchQuery.toLowerCase())
      )
    }

    setFilteredEvidence(filtered)
  }, [searchQuery, typeFilter, evidence])

  const handleToggleSensitive = async (evidenceId: string) => {
    const file = evidence.find(e => e.id === evidenceId)
    if (file) {
      try {
        await apiFetch(`/evidence/${evidenceId}`, {
          method: 'PATCH',
          body: JSON.stringify({ is_sensitive: !file.is_sensitive }),
        })
        const data = await apiFetch<any[]>('/evidence')
        setEvidence(data)
      } catch (err) {
        console.error('Failed to update evidence', err)
      }
    }
  }

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
  }

  const getFileTypeDisplay = (fileType: string) => {
    const parts = (fileType || '').split('/')
    return parts[1] ? parts[1].toUpperCase() : fileType
  }

  const fileTypes = ['all', ...new Set(evidence.map(e => (e.file_type || '').split('/')[0]).filter(Boolean))]

  return (
    <div className="min-h-screen bg-slate-50">
      <AdminSidebar />
      <AdminTopbar />

      <main className="ml-64 pt-20 pb-12">
        <div className="max-w-7xl mx-auto px-8">
          {/* Header */}
          <div className="mb-8">
            <h1 className="text-4xl font-bold text-slate-900">Evidence Management</h1>
            <p className="text-slate-600 mt-2">View and manage all uploaded evidence files</p>
          </div>

          {/* Filters */}
          <Card className="mb-8">
            <CardHeader>
              <CardTitle className="text-lg flex items-center gap-2">
                <Search className="w-5 h-5" />
                Search & Filter
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="search">Search by filename or Case ID</Label>
                  <Input
                    id="search"
                    placeholder="e.g., screenshot.png or TL-2026-000101"
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="type">File Type</Label>
                  <Select value={typeFilter} onValueChange={setTypeFilter}>
                    <SelectTrigger id="type">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {fileTypes.map(type => (
                        <SelectItem key={type} value={type}>
                          {type === 'all' ? 'All Types' : type.toUpperCase()}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div className="flex items-end">
                  <Button
                    variant="outline"
                    onClick={() => {
                      setSearchQuery('')
                      setTypeFilter('all')
                    }}
                    className="w-full"
                  >
                    Clear Filters
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Evidence Table */}
          <Card>
            <CardHeader>
              <CardDescription>
                {filteredEvidence.length} file{filteredEvidence.length !== 1 ? 's' : ''} found
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b border-slate-200">
                      <th className="text-left text-sm font-semibold text-slate-900 pb-3 px-4">Filename</th>
                      <th className="text-left text-sm font-semibold text-slate-900 pb-3 px-4">Case ID</th>
                      <th className="text-left text-sm font-semibold text-slate-900 pb-3 px-4">Type</th>
                      <th className="text-left text-sm font-semibold text-slate-900 pb-3 px-4">Size</th>
                      <th className="text-left text-sm font-semibold text-slate-900 pb-3 px-4">Uploaded</th>
                      <th className="text-left text-sm font-semibold text-slate-900 pb-3 px-4">Sensitive</th>
                      <th className="text-left text-sm font-semibold text-slate-900 pb-3 px-4">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {filteredEvidence.map((file) => (
                      <tr key={file.id} className="border-b border-slate-200 hover:bg-slate-50">
                        <td className="px-4 py-3">
                          <div className="flex items-center gap-2">
                            {file.is_sensitive && (
                              <AlertTriangle className="w-4 h-4 text-red-600" />
                            )}
                            <div>
                              <p className="font-medium text-slate-900 text-sm">{file.original_file_name}</p>
                            </div>
                          </div>
                        </td>
                        <td className="px-4 py-3 text-sm font-mono text-slate-600">
                          <Link href={`/admin/reports/${file.complaint_id}`} className="text-cyan-600 hover:text-cyan-700">
                            {file.complaint_id}
                          </Link>
                        </td>
                        <td className="px-4 py-3 text-sm text-slate-600">
                          <Badge variant="outline">{getFileTypeDisplay(file.file_type)}</Badge>
                        </td>
                        <td className="px-4 py-3 text-sm text-slate-600">
                          {formatFileSize(file.file_size)}
                        </td>
                        <td className="px-4 py-3 text-sm text-slate-600">
                          {new Date(file.uploaded_at).toLocaleDateString()}
                        </td>
                        <td className="px-4 py-3">
                          <Switch
                            checked={file.is_sensitive}
                            onCheckedChange={() => handleToggleSensitive(file.id)}
                          />
                        </td>
                        <td className="px-4 py-3 text-sm space-x-2 flex">
                          <Button size="sm" variant="ghost" className="h-8">
                            <Eye className="w-4 h-4" />
                          </Button>
                          <Button size="sm" variant="ghost" className="h-8">
                            <Download className="w-4 h-4" />
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
