'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Progress } from '@/components/ui/progress'
import { Calendar, TrendingUp, Users, AlertTriangle, DollarSign, Crown, Clock, Plus, Zap } from 'lucide-react'
import { RevenueChart } from '@/components/charts/RevenueChart'
import { NoShowTrendChart } from '@/components/charts/NoShowTrendChart'
import { AppointmentList } from '@/components/appointments/AppointmentList'
import { DashboardLayout } from '@/components/layout/DashboardLayout'
import { DashboardFAB } from '@/components/ui/floating-action-button'

interface User {
  id: string
  email: string
  first_name: string
  last_name: string
  role: string
  subscription_status: string
  trial_days_left?: number
  is_verified: boolean
}

interface DashboardStats {
  total_appointments: number
  no_show_rate: number
  revenue_saved: number
  active_patients: number
  upcoming_appointments: number
  high_risk_appointments: number
  subscription_plan: string
  trial_days_left?: number
}

interface SubscriptionPlan {
  name: string
  price: number
  features: string[]
  max_providers: number
  max_appointments_per_month: number
}

interface CurrentSubscription {
  current_plan: string
  plan_details: SubscriptionPlan
  subscription_status: string
  trial_days_left?: number
}

export default function Dashboard() {
  const router = useRouter()
  const [stats, setStats] = useState<DashboardStats | null>(null)
  const [subscription, setSubscription] = useState<CurrentSubscription | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadDashboardData()
  }, [])

  const loadDashboardData = async () => {
    try {
      const token = localStorage.getItem('access_token')
      if (!token) return

      // Load dashboard stats
      const statsResponse = await fetch('http://localhost:7000/dashboard/stats', {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      if (statsResponse.ok) {
        const statsData = await statsResponse.json()
        setStats(statsData)
      }

      // Load subscription info
      const subResponse = await fetch('http://localhost:7000/subscription/current', {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      if (subResponse.ok) {
        const subData = await subResponse.json()
        setSubscription(subData)
      }
    } catch (error) {
      console.error('Error loading dashboard data:', error)
    } finally {
      setLoading(false)
    }
  }

  const getSubscriptionBadge = (plan: string) => {
    const badges = {
      trial: { label: 'Trial', variant: 'outline' as const, icon: Clock },
      starter: { label: 'Starter', variant: 'default' as const, icon: Users },
      professional: { label: 'Pro', variant: 'secondary' as const, icon: TrendingUp },
      enterprise: { label: 'Enterprise', variant: 'destructive' as const, icon: Crown }
    }
    
    const badge = badges[plan as keyof typeof badges] || badges.trial
    const Icon = badge.icon

    return (
      <Badge variant={badge.variant} className="flex items-center gap-1">
        <Icon size={12} />
        {badge.label}
      </Badge>
    )
  }

  if (loading) {
    return (
      <DashboardLayout>
        <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 flex items-center justify-center">
          <div className="text-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
            <p className="text-gray-600">Loading your dashboard...</p>
          </div>
        </div>
      </DashboardLayout>
    )
  }

  const user = JSON.parse(localStorage.getItem('user') || '{}')
  const trialProgress = subscription?.trial_days_left ? 
    ((14 - subscription.trial_days_left) / 14) * 100 : 0

  return (
    <DashboardLayout>
      <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">
        {/* Header */}
        <header className="bg-white/80 backdrop-blur-sm shadow-sm border-b border-white/20 lg:ml-0">
          <div className="max-w-7xl mx-auto px-6 py-6 lg:pl-20">
            <div className="flex justify-between items-center">
              <div>
                <h1 className="text-2xl font-bold text-gray-900 mb-1">
                  Good morning, {user.first_name}! 👋
                </h1>
                <p className="text-gray-600">
                  Here's what's happening with your practice today
                </p>
              </div>
              <div className="hidden md:flex items-center space-x-3">
                <Button className="bg-blue-600 hover:bg-blue-700">
                  <Plus className="h-4 w-4 mr-2" />
                  New Appointment
                </Button>
                <Button variant="outline">
                  <Zap className="h-4 w-4 mr-2" />
                  Optimize Schedule
                </Button>
              </div>
            </div>
          </div>
        </header>

        <div className="max-w-7xl mx-auto p-6 lg:pl-20">
        {/* Trial Alert */}
        {user.subscription_status === 'trial' && subscription?.trial_days_left !== undefined && (
          <Alert className="mb-6 border-amber-200 bg-amber-50">
            <Clock className="h-4 w-4" />
            <AlertDescription>
              <div className="flex justify-between items-start">
                <div>
                  <p className="font-medium text-amber-800">
                    {subscription.trial_days_left} days left in your free trial
                  </p>
                  <p className="text-amber-700 text-sm mt-1">
                    Upgrade now to continue using ChronoGuard Pro after your trial ends.
                  </p>
                  <Progress value={trialProgress} className="w-48 mt-2" />
                </div>
                <Button size="sm" onClick={() => router.push('/pricing')}>
                  Upgrade Now
                </Button>
              </div>
            </AlertDescription>
          </Alert>
        )}

        {/* Key Metrics */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-6 gap-6 mb-8">
          <Card className="bg-white/80 backdrop-blur-sm border-0 shadow-lg">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Appointments</CardTitle>
              <Calendar className="h-4 w-4 text-blue-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats?.total_appointments || 0}</div>
              <p className="text-xs text-muted-foreground">This month</p>
            </CardContent>
          </Card>

          <Card className="bg-white/80 backdrop-blur-sm border-0 shadow-lg">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">No-Show Rate</CardTitle>
              <TrendingUp className="h-4 w-4 text-green-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats?.no_show_rate || 0}%</div>
              <p className="text-xs text-green-600">-3.2% from last month</p>
            </CardContent>
          </Card>

          <Card className="bg-white/80 backdrop-blur-sm border-0 shadow-lg">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Revenue Saved</CardTitle>
              <DollarSign className="h-4 w-4 text-emerald-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">${stats?.revenue_saved?.toLocaleString() || 0}</div>
              <p className="text-xs text-emerald-600">+$1,200 this month</p>
            </CardContent>
          </Card>

          <Card className="bg-white/80 backdrop-blur-sm border-0 shadow-lg">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Active Patients</CardTitle>
              <Users className="h-4 w-4 text-purple-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats?.active_patients || 0}</div>
              <p className="text-xs text-purple-600">+12 this week</p>
            </CardContent>
          </Card>

          <Card className="bg-white/80 backdrop-blur-sm border-0 shadow-lg">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">High Risk Today</CardTitle>
              <AlertTriangle className="h-4 w-4 text-amber-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats?.high_risk_appointments || 0}</div>
              <p className="text-xs text-amber-600">Requires attention</p>
            </CardContent>
          </Card>

          <Card className="bg-white/80 backdrop-blur-sm border-0 shadow-lg">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Plan</CardTitle>
              <Crown className="h-4 w-4 text-blue-600" />
            </CardHeader>
            <CardContent>
              <div className="text-lg font-bold capitalize">{subscription?.current_plan || 'Trial'}</div>
              <p className="text-xs text-muted-foreground">
                {subscription?.plan_details.max_appointments_per_month || 100} appointments/month
              </p>
            </CardContent>
          </Card>
        </div>

        {/* Charts Section */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          <Card className="bg-white/80 backdrop-blur-sm border-0 shadow-lg">
            <CardHeader>
              <CardTitle>Revenue Impact</CardTitle>
              <CardDescription>Monthly savings from AI optimization</CardDescription>
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

        {/* Action Items and Schedule */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
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

          <div className="space-y-6">
            <Card className="bg-white/80 backdrop-blur-sm border-0 shadow-lg">
              <CardHeader>
                <CardTitle>Subscription Details</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {subscription && (
                  <>
                    <div className="flex justify-between items-center">
                      <span className="text-sm font-medium">Current Plan</span>
                      {getSubscriptionBadge(subscription.current_plan)}
                    </div>
                    <div className="text-2xl font-bold">
                      ${subscription.plan_details.price}
                      <span className="text-sm font-normal text-gray-500">/month</span>
                    </div>
                    <div className="space-y-2">
                      <p className="text-sm font-medium">Plan Features:</p>
                      <ul className="text-sm text-gray-600 space-y-1">
                        {subscription.plan_details.features.map((feature, index) => (
                          <li key={index}>• {feature}</li>
                        ))}
                      </ul>
                    </div>
                    <Button 
                      className="w-full" 
                      variant={subscription.current_plan === 'trial' ? 'default' : 'outline'}
                      onClick={() => router.push('/pricing')}
                    >
                      {subscription.current_plan === 'trial' ? 'Upgrade Plan' : 'Change Plan'}
                    </Button>
                  </>
                )}
              </CardContent>
            </Card>

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
                <Button 
                  className="w-full" 
                  variant="outline"
                  onClick={() => router.push('/settings')}
                >
                  Practice Settings
                </Button>
              </CardContent>
            </Card>
          </div>
          </div>
        </div>

        {/* Floating Action Button */}
        <DashboardFAB />
      </div>
    </DashboardLayout>
  )
}