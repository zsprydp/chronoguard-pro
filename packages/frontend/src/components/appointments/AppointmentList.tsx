'use client'

import { useState, useEffect } from 'react'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { 
  Clock, 
  User, 
  AlertTriangle, 
  Phone, 
  Calendar,
  TrendingUp,
  CheckCircle2,
  XCircle,
  AlertCircle,
  Send,
  Eye,
  MoreVertical
} from 'lucide-react'

interface Appointment {
  id: string
  provider_id: string
  patient_id: string
  scheduled_time: string
  duration_minutes: number
  appointment_type: string
  status: string
  no_show_probability: number
}

interface PatientInfo {
  id: string
  name: string
  phone?: string
  risk_score: number
  total_appointments: number
  no_show_rate: number
}

// Enhanced appointment display with fetched data
export function AppointmentList() {
  const [appointments, setAppointments] = useState<Appointment[]>([])
  const [patients, setPatients] = useState<{[key: string]: PatientInfo}>({})
  const [loading, setLoading] = useState(true)
  const [selectedAppointment, setSelectedAppointment] = useState<string | null>(null)

  useEffect(() => {
    loadAppointments()
  }, [])

  const loadAppointments = async () => {
    try {
      const token = localStorage.getItem('access_token')
      if (!token) return

      // Load appointments
      const appointmentsRes = await fetch('http://localhost:7000/appointments', {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      
      if (appointmentsRes.ok) {
        const appointmentsData = await appointmentsRes.json()
        setAppointments(appointmentsData)
        
        // Load patients data
        const patientsRes = await fetch('http://localhost:7000/patients', {
          headers: { 'Authorization': `Bearer ${token}` }
        })
        
        if (patientsRes.ok) {
          const patientsData = await patientsRes.json()
          const patientsMap = patientsData.reduce((acc: any, patient: any) => {
            acc[patient.id] = patient
            return acc
          }, {})
          setPatients(patientsMap)
        }
      }
    } catch (error) {
      console.error('Error loading appointments:', error)
    } finally {
      setLoading(false)
    }
  }

  const getRiskLevel = (probability: number) => {
    if (probability >= 0.4) return 'high'
    if (probability >= 0.25) return 'medium'
    return 'low'
  }

  const getRiskBadge = (probability: number) => {
    const riskLevel = getRiskLevel(probability)
    const riskPercentage = Math.round(probability * 100)
    
    switch (riskLevel) {
      case 'high':
        return (
          <Badge variant="destructive" className="flex items-center gap-1">
            <AlertTriangle className="h-3 w-3" />
            {riskPercentage}% Risk
          </Badge>
        )
      case 'medium':
        return (
          <Badge variant="secondary" className="flex items-center gap-1 bg-amber-100 text-amber-800">
            <AlertCircle className="h-3 w-3" />
            {riskPercentage}% Risk
          </Badge>
        )
      default:
        return (
          <Badge variant="outline" className="flex items-center gap-1 text-green-700 border-green-200">
            <CheckCircle2 className="h-3 w-3" />
            {riskPercentage}% Risk
          </Badge>
        )
    }
  }

  const formatTime = (dateString: string) => {
    try {
      const date = new Date(dateString)
      return date.toLocaleTimeString('en-US', { 
        hour: 'numeric', 
        minute: '2-digit',
        hour12: true 
      })
    } catch {
      return 'Time TBD'
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status.toLowerCase()) {
      case 'scheduled':
        return <Calendar className="h-4 w-4 text-blue-500" />
      case 'completed':
        return <CheckCircle2 className="h-4 w-4 text-green-500" />
      case 'cancelled':
        return <XCircle className="h-4 w-4 text-red-500" />
      case 'no_show':
        return <AlertTriangle className="h-4 w-4 text-orange-500" />
      default:
        return <Clock className="h-4 w-4 text-gray-500" />
    }
  }

  const handleSendReminder = (appointmentId: string, patientPhone?: string) => {
    if (!patientPhone) {
      alert('No phone number available for this patient')
      return
    }
    // Placeholder for reminder functionality
    alert(`Reminder sent to ${patientPhone}`)
  }

  if (loading) {
    return (
      <div className="space-y-3">
        {[1, 2, 3].map((i) => (
          <div key={i} className="p-4 border rounded-xl animate-pulse">
            <div className="flex justify-between items-center">
              <div className="flex space-x-4">
                <div className="h-4 w-16 bg-gray-200 rounded"></div>
                <div className="h-4 w-24 bg-gray-200 rounded"></div>
                <div className="h-4 w-20 bg-gray-200 rounded"></div>
              </div>
              <div className="h-6 w-20 bg-gray-200 rounded-full"></div>
            </div>
          </div>
        ))}
      </div>
    )
  }

  if (appointments.length === 0) {
    return (
      <Card className="border-dashed border-2 border-gray-200">
        <CardContent className="flex flex-col items-center justify-center py-12 text-center">
          <Calendar className="h-12 w-12 text-gray-400 mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No appointments scheduled</h3>
          <p className="text-sm text-gray-500 mb-6">
            When you have appointments, they'll appear here with AI-powered risk assessments.
          </p>
          <Button>Schedule Appointment</Button>
        </CardContent>
      </Card>
    )
  }

  return (
    <div className="space-y-2">
      {appointments.map((appointment) => {
        const patient = patients[appointment.patient_id]
        const riskLevel = getRiskLevel(appointment.no_show_probability || 0)
        const isSelected = selectedAppointment === appointment.id
        
        return (
          <Card 
            key={appointment.id} 
            className={`
              transition-all duration-200 cursor-pointer border
              ${riskLevel === 'high' ? 'border-red-200 bg-red-50/50' : ''}
              ${riskLevel === 'medium' ? 'border-amber-200 bg-amber-50/50' : ''}
              ${riskLevel === 'low' ? 'border-green-200 bg-green-50/30' : ''}
              ${isSelected ? 'ring-2 ring-blue-500 shadow-lg' : 'hover:shadow-md'}
            `}
            onClick={() => setSelectedAppointment(isSelected ? null : appointment.id)}
          >
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                {/* Left Section - Time & Patient Info */}
                <div className="flex items-center space-x-4">
                  {/* Time with status indicator */}
                  <div className="flex flex-col items-center min-w-0">
                    <div className="flex items-center space-x-2 text-gray-900">
                      {getStatusIcon(appointment.status)}
                      <span className="font-semibold text-sm">
                        {formatTime(appointment.scheduled_time)}
                      </span>
                    </div>
                    <span className="text-xs text-gray-500 mt-1">
                      {appointment.duration_minutes}min
                    </span>
                  </div>

                  {/* Patient Info */}
                  <div className="min-w-0 flex-1">
                    <div className="flex items-center space-x-2 mb-1">
                      <User className="h-4 w-4 text-gray-600 flex-shrink-0" />
                      <span className="font-medium text-gray-900 truncate">
                        {patient?.name || 'Unknown Patient'}
                      </span>
                    </div>
                    <div className="flex items-center space-x-4 text-xs text-gray-500">
                      <span className="capitalize bg-gray-100 px-2 py-1 rounded-full">
                        {appointment.appointment_type}
                      </span>
                      {patient?.total_appointments && (
                        <span className="flex items-center space-x-1">
                          <TrendingUp className="h-3 w-3" />
                          <span>{patient.total_appointments} visits</span>
                        </span>
                      )}
                    </div>
                  </div>
                </div>
                
                {/* Right Section - Risk & Actions */}
                <div className="flex items-center space-x-3">
                  {/* Risk Assessment */}
                  <div className="text-right min-w-0">
                    {getRiskBadge(appointment.no_show_probability || 0)}
                    {patient?.no_show_rate !== undefined && (
                      <div className="text-xs text-gray-500 mt-1">
                        History: {Math.round(patient.no_show_rate * 100)}%
                      </div>
                    )}
                  </div>

                  {/* Quick Actions */}
                  <div className="flex items-center space-x-1">
                    {riskLevel === 'high' && patient?.phone && (
                      <Button
                        size="sm"
                        variant="outline"
                        className="h-8 w-8 p-0"
                        onClick={(e) => {
                          e.stopPropagation()
                          handleSendReminder(appointment.id, patient.phone)
                        }}
                        title="Send reminder"
                      >
                        <Send className="h-3 w-3" />
                      </Button>
                    )}
                    <Button
                      size="sm"
                      variant="outline"
                      className="h-8 w-8 p-0"
                      onClick={(e) => {
                        e.stopPropagation()
                        // Handle view details
                      }}
                      title="View details"
                    >
                      <Eye className="h-3 w-3" />
                    </Button>
                  </div>
                </div>
              </div>

              {/* Expanded Details */}
              {isSelected && (
                <div className="mt-4 pt-4 border-t border-gray-200 space-y-3">
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                    <div>
                      <span className="font-medium text-gray-700">Status:</span>
                      <p className="text-gray-600 capitalize">{appointment.status}</p>
                    </div>
                    <div>
                      <span className="font-medium text-gray-700">Patient Phone:</span>
                      <p className="text-gray-600">{patient?.phone || 'Not provided'}</p>
                    </div>
                    <div>
                      <span className="font-medium text-gray-700">Risk Score:</span>
                      <p className="text-gray-600">{patient?.risk_score || 'N/A'}</p>
                    </div>
                  </div>
                  
                  {riskLevel !== 'low' && (
                    <div className="flex space-x-2">
                      <Button size="sm" variant="outline" className="flex-1">
                        <Phone className="h-3 w-3 mr-2" />
                        Call Patient
                      </Button>
                      <Button size="sm" variant="outline" className="flex-1">
                        <Send className="h-3 w-3 mr-2" />
                        Send Reminder
                      </Button>
                      <Button size="sm" variant="outline" className="flex-1">
                        Reschedule
                      </Button>
                    </div>
                  )}
                </div>
              )}
            </CardContent>
          </Card>
        )
      })}
      
      {/* Summary Footer */}
      <div className="mt-6 p-4 bg-gray-50 rounded-lg">
        <div className="flex justify-between items-center text-sm">
          <span className="text-gray-600">
            Total appointments: {appointments.length}
          </span>
          <div className="flex space-x-4">
            <span className="text-green-600">
              Low risk: {appointments.filter(a => getRiskLevel(a.no_show_probability || 0) === 'low').length}
            </span>
            <span className="text-amber-600">
              Medium risk: {appointments.filter(a => getRiskLevel(a.no_show_probability || 0) === 'medium').length}
            </span>
            <span className="text-red-600">
              High risk: {appointments.filter(a => getRiskLevel(a.no_show_probability || 0) === 'high').length}
            </span>
          </div>
        </div>
      </div>
    </div>
  )
}