import { Badge } from '@/components/ui/badge'

export function StatusBadge({ status }: { status: string }) {
  const statusConfig = {
    pending: { className: 'bg-yellow-100 text-yellow-800', label: 'Pending' },
    under_review: { className: 'bg-blue-100 text-blue-800', label: 'Under Review' },
    need_more_info: { className: 'bg-orange-100 text-orange-800', label: 'Need More Info' },
    escalated: { className: 'bg-red-100 text-red-800', label: 'Escalated' },
    closed: { className: 'bg-green-100 text-green-800', label: 'Closed' },
  }

  const config = statusConfig[status as keyof typeof statusConfig] || {
    className: 'bg-slate-100 text-slate-800',
    label: status,
  }

  return (
    <Badge className={config.className}>
      {config.label}
    </Badge>
  )
}
