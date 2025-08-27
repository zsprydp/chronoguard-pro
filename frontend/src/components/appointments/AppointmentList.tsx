'use client'

import { Badge } from '@/components/ui/badge'
import { Clock, User, AlertTriangle } from 'lucide-react'

const mockAppointments = [
  {
    id: 1,
    time: '09:00 AM',
    patient: 'Sarah Johnson',
    type: 'Consultation',
    riskLevel: 'low',
    probability: 0.12
  },
  {
    id: 2,
    time: '09:30 AM',
    patient: 'Michael Chen',
    type: 'Follow-up',
    riskLevel: 'high',
    probability: 0.45
  },
  {
    id: 3,
    time: '10:00 AM',
    patient: 'Emily Rodriguez',
    type: 'Procedure',
    riskLevel: 'medium',
    probability: 0.28
  },
  {
    id: 4,
    time: '10:30 AM',
    patient: 'David Wilson',
    type: 'Checkup',
    riskLevel: 'low',
    probability: 0.08
  },
  {
    id: 5,
    time: '11:00 AM',
    patient: 'Lisa Thompson',
    type: 'Consultation',
    riskLevel: 'high',
    probability: 0.52
  }
]

export function AppointmentList() {
  const getRiskBadge = (riskLevel: string) => {
    switch (riskLevel) {
      case 'high':
        return <Badge variant="destructive">High Risk</Badge>
      case 'medium':
        return <Badge variant="secondary">Medium Risk</Badge>
      default:
        return <Badge variant="outline">Low Risk</Badge>
    }
  }

  return (
    <div className="space-y-3">
      {mockAppointments.map((appointment) => (
        <div
          key={appointment.id}
          className="flex items-center justify-between p-4 border rounded-lg hover:bg-gray-50"
        >
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2 text-gray-600">
              <Clock className="h-4 w-4" />
              <span className="font-medium">{appointment.time}</span>
            </div>
            <div className="flex items-center space-x-2">
              <User className="h-4 w-4 text-gray-600" />
              <span className="font-medium">{appointment.patient}</span>
            </div>
            <span className="text-sm text-gray-500">{appointment.type}</span>
          </div>
          
          <div className="flex items-center space-x-3">
            <div className="text-right">
              <div className="text-sm font-medium">
                {(appointment.probability * 100).toFixed(0)}% risk
              </div>
              <div className="text-xs text-gray-500">no-show probability</div>
            </div>
            {getRiskBadge(appointment.riskLevel)}
            {appointment.riskLevel === 'high' && (
              <AlertTriangle className="h-4 w-4 text-red-500" />
            )}
          </div>
        </div>
      ))}
    </div>
  )
}