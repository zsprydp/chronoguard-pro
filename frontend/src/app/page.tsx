'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Calendar, TrendingUp, Users, AlertTriangle, DollarSign } from 'lucide-react'
import { RevenueChart } from '@/components/charts/RevenueChart'
import { NoShowTrendChart } from '@/components/charts/NoShowTrendChart'
import { AppointmentList } from '@/components/appointments/AppointmentList'

interface DashboardMetrics {
  totalAppointments: number
  noShowRate: number
  revenueSaved: number
  upcomingHighRisk: number
  optimizationScore: number
}

export default function Dashboard() {
  const [metrics, setMetrics] = useState<DashboardMetrics>({
    totalAppointments: 0,
    noShowRate: 0,
    revenueSaved: 0,
    upcomingHighRisk: 0,
    optimizationScore: 0
  })

  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    // Simulate API call
    setTimeout(() => {
      setMetrics({
        totalAppointments: 142,
        noShowRate: 12.8,
        revenueSaved: 8420,
        upcomingHighRisk: 7,
        optimizationScore: 87
      })
      setIsLoading(false)
    }, 1000)
  }, [])

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">ChronoGuard Pro</h1>
          <p className="text-lg text-gray-600">AI-Powered Appointment Optimization Dashboard</p>
        </div>

        {/* Key Metrics */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-6 mb-8">
          <Card className="bg-white/80 backdrop-blur-sm border-0 shadow-lg">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Appointments</CardTitle>
              <Calendar className="h-4 w-4 text-blue-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{isLoading ? '...' : metrics.totalAppointments}</div>
              <p className="text-xs text-muted-foreground">This month</p>
            </CardContent>
          </Card>

          <Card className="bg-white/80 backdrop-blur-sm border-0 shadow-lg">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">No-Show Rate</CardTitle>
              <TrendingUp className="h-4 w-4 text-green-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {isLoading ? '...' : `${metrics.noShowRate}%`}
              </div>
              <p className="text-xs text-green-600">-3.2% from last month</p>
            </CardContent>
          </Card>

          <Card className="bg-white/80 backdrop-blur-sm border-0 shadow-lg">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Revenue Saved</CardTitle>
              <DollarSign className="h-4 w-4 text-emerald-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {isLoading ? '...' : `$${metrics.revenueSaved.toLocaleString()}`}
              </div>
              <p className="text-xs text-emerald-600">+$1,200 this month</p>
            </CardContent>
          </Card>

          <Card className="bg-white/80 backdrop-blur-sm border-0 shadow-lg">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">High Risk Today</CardTitle>
              <AlertTriangle className="h-4 w-4 text-amber-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{isLoading ? '...' : metrics.upcomingHighRisk}</div>
              <p className="text-xs text-amber-600">Requires attention</p>
            </CardContent>
          </Card>

          <Card className="bg-white/80 backdrop-blur-sm border-0 shadow-lg">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Optimization Score</CardTitle>
              <Users className="h-4 w-4 text-purple-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {isLoading ? '...' : `${metrics.optimizationScore}%`}
              </div>
              <p className="text-xs text-purple-600">Excellent performance</p>
            </CardContent>
          </Card>
        </div>

        {/* Charts Section */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          <Card className="bg-white/80 backdrop-blur-sm border-0 shadow-lg">
            <CardHeader>
              <CardTitle>Revenue Impact</CardTitle>
              <CardDescription>Monthly savings from optimization</CardDescription>
            </CardHeader>
            <CardContent>
              <RevenueChart />
            </CardContent>
          </Card>

          <Card className="bg-white/80 backdrop-blur-sm border-0 shadow-lg">
            <CardHeader>
              <CardTitle>No-Show Trends</CardTitle>
              <CardDescription>Historical and predicted rates</CardDescription>
            </CardHeader>
            <CardContent>
              <NoShowTrendChart />
            </CardContent>
          </Card>
        </div>

        {/* Action Items and Schedule Preview */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Today's Schedule */}
          <div className="lg:col-span-2">
            <Card className="bg-white/80 backdrop-blur-sm border-0 shadow-lg">
              <CardHeader>
                <div className="flex justify-between items-center">
                  <div>
                    <CardTitle>Today's Schedule</CardTitle>
                    <CardDescription>Appointments with AI risk assessment</CardDescription>
                  </div>
                  <Button size="sm">Optimize Schedule</Button>
                </div>
              </CardHeader>
              <CardContent>
                <AppointmentList />
              </CardContent>
            </Card>
          </div>

          {/* Quick Actions & Alerts */}
          <div className="space-y-6">
            <Card className="bg-white/80 backdrop-blur-sm border-0 shadow-lg">
              <CardHeader>
                <CardTitle>Quick Actions</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <Button className="w-full" variant="default">
                  Run Daily Optimization
                </Button>
                <Button className="w-full" variant="outline">
                  Send High-Risk Reminders
                </Button>
                <Button className="w-full" variant="outline">
                  View Analytics Report
                </Button>
              </CardContent>
            </Card>

            <Card className="bg-white/80 backdrop-blur-sm border-0 shadow-lg">
              <CardHeader>
                <CardTitle>Today's Alerts</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-start space-x-3">
                  <Badge variant="destructive" className="mt-1">High</Badge>
                  <div>
                    <p className="text-sm font-medium">7 high-risk appointments</p>
                    <p className="text-xs text-muted-foreground">Consider sending extra reminders</p>
                  </div>
                </div>
                <div className="flex items-start space-x-3">
                  <Badge variant="secondary" className="mt-1">Medium</Badge>
                  <div>
                    <p className="text-sm font-medium">Schedule optimization available</p>
                    <p className="text-xs text-muted-foreground">Potential $340 revenue gain</p>
                  </div>
                </div>
                <div className="flex items-start space-x-3">
                  <Badge variant="outline" className="mt-1">Low</Badge>
                  <div>
                    <p className="text-sm font-medium">3 empty afternoon slots</p>
                    <p className="text-xs text-muted-foreground">Perfect for same-day bookings</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  )
}