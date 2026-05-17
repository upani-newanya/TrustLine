import { Badge } from '@/components/ui/badge'

export function PriorityBadge({ priority }: { priority: string }) {
  const priorityConfig = {
    low: { className: 'bg-green-100 text-green-800', label: 'Low' },
    medium: { className: 'bg-orange-100 text-orange-800', label: 'Medium' },
    high: { className: 'bg-red-100 text-red-800', label: 'High' },
    urgent: { className: 'bg-purple-100 text-purple-800', label: 'Urgent' },
  }

  const config = priorityConfig[priority as keyof typeof priorityConfig] || {
    className: 'bg-slate-100 text-slate-800',
    label: priority,
  }

  return (
    <Badge className={config.className}>
      {config.label}
    </Badge>
  )
}
