'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Check, Crown, Users, TrendingUp, Zap } from 'lucide-react'

interface SubscriptionPlan {
  name: string
  price: number
  features: string[]
  max_providers: number
  max_appointments_per_month: number
}

interface PricingPlans {
  [key: string]: SubscriptionPlan
}

export default function PricingPage() {
  const router = useRouter()
  const [plans, setPlans] = useState<PricingPlans>({})
  const [currentPlan, setCurrentPlan] = useState<string>('trial')
  const [loading, setLoading] = useState(true)
  const [upgrading, setUpgrading] = useState<string | null>(null)

  useEffect(() => {
    loadPlans()
    loadCurrentPlan()
  }, [])

  const loadPlans = async () => {
    try {
      const response = await fetch('http://localhost:7000/subscription/plans')
      if (response.ok) {
        const data = await response.json()
        setPlans(data.plans)
      }
    } catch (error) {
      console.error('Error loading plans:', error)
    }
  }

  const loadCurrentPlan = async () => {
    try {
      const token = localStorage.getItem('access_token')
      if (!token) return

      const response = await fetch('http://localhost:7000/subscription/current', {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      
      if (response.ok) {
        const data = await response.json()
        setCurrentPlan(data.current_plan)
      }
    } catch (error) {
      console.error('Error loading current plan:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleUpgrade = async (planName: string) => {
    setUpgrading(planName)
    
    try {
      const token = localStorage.getItem('access_token')
      if (!token) {
        router.push('/auth/login')
        return
      }

      const response = await fetch('http://localhost:7000/subscription/upgrade', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ plan_name: planName })
      })

      if (response.ok) {
        setCurrentPlan(planName)
        // In a real app, integrate with Stripe here
        alert('Plan upgraded successfully! (Demo mode - no payment processed)')
      }
    } catch (error) {
      console.error('Error upgrading plan:', error)
      alert('Error upgrading plan. Please try again.')
    } finally {
      setUpgrading(null)
    }
  }

  const getPlanIcon = (planName: string) => {
    const icons = {
      trial: Users,
      starter: Zap,
      professional: TrendingUp,
      enterprise: Crown
    }
    return icons[planName as keyof typeof icons] || Users
  }

  const getPlanColor = (planName: string) => {
    const colors = {
      trial: 'border-gray-200',
      starter: 'border-blue-200 bg-blue-50',
      professional: 'border-purple-200 bg-purple-50',
      enterprise: 'border-amber-200 bg-amber-50'
    }
    return colors[planName as keyof typeof colors] || 'border-gray-200'
  }

  const isPopular = (planName: string) => planName === 'professional'

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading pricing plans...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex justify-between items-center">
            <div className="flex items-center space-x-4">
              <Button variant="outline" onClick={() => router.push('/dashboard')}>
                ← Back to Dashboard
              </Button>
              <h1 className="text-2xl font-bold text-gray-900">Pricing Plans</h1>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-6xl mx-auto p-6">
        {/* Hero Section */}
        <div className="text-center mb-12">
          <h2 className="text-4xl font-bold text-gray-900 mb-4">
            Choose the Perfect Plan for Your Practice
          </h2>
          <p className="text-xl text-gray-600 mb-8">
            Reduce no-shows and increase revenue with AI-powered appointment optimization
          </p>
          <div className="flex justify-center items-center space-x-4 text-sm text-gray-500">
            <span>✓ 14-day free trial</span>
            <span>✓ No setup fees</span>
            <span>✓ Cancel anytime</span>
          </div>
        </div>

        {/* Pricing Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
          {Object.entries(plans).map(([planKey, plan]) => {
            const Icon = getPlanIcon(planKey)
            const isCurrentPlan = currentPlan === planKey
            const popular = isPopular(planKey)
            
            return (
              <Card 
                key={planKey} 
                className={`relative ${getPlanColor(planKey)} ${popular ? 'ring-2 ring-purple-500' : ''}`}
              >
                {popular && (
                  <Badge className="absolute -top-3 left-1/2 transform -translate-x-1/2 bg-purple-500">
                    Most Popular
                  </Badge>
                )}
                
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <Icon className="h-8 w-8 text-blue-600" />
                    {isCurrentPlan && (
                      <Badge variant="outline">Current Plan</Badge>
                    )}
                  </div>
                  <CardTitle className="capitalize">{plan.name}</CardTitle>
                  <CardDescription>
                    Perfect for {planKey === 'trial' ? 'getting started' : 
                                planKey === 'starter' ? 'small practices' :
                                planKey === 'professional' ? 'growing practices' :
                                'large organizations'}
                  </CardDescription>
                </CardHeader>

                <CardContent className="space-y-4">
                  <div className="text-center">
                    <div className="text-3xl font-bold">
                      ${plan.price}
                      <span className="text-lg font-normal text-gray-500">/month</span>
                    </div>
                    {planKey === 'trial' && (
                      <p className="text-sm text-green-600 font-medium">Free for 14 days</p>
                    )}
                  </div>

                  <ul className="space-y-2 text-sm">
                    {plan.features.map((feature, index) => (
                      <li key={index} className="flex items-start space-x-2">
                        <Check className="h-4 w-4 text-green-500 mt-0.5 flex-shrink-0" />
                        <span>{feature}</span>
                      </li>
                    ))}
                  </ul>

                  <div className="border-t pt-4">
                    <div className="text-xs text-gray-500 space-y-1">
                      <p>Up to {plan.max_providers} providers</p>
                      <p>
                        {plan.max_appointments_per_month === 999999 ? 
                          'Unlimited appointments' : 
                          `${plan.max_appointments_per_month} appointments/month`
                        }
                      </p>
                    </div>
                  </div>

                  <Button
                    className="w-full"
                    variant={popular ? 'default' : 'outline'}
                    disabled={isCurrentPlan || upgrading === planKey}
                    onClick={() => handleUpgrade(planKey)}
                  >
                    {upgrading === planKey ? (
                      <>
                        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                        Upgrading...
                      </>
                    ) : isCurrentPlan ? (
                      'Current Plan'
                    ) : planKey === 'trial' ? (
                      'Start Free Trial'
                    ) : (
                      'Upgrade to ' + plan.name
                    )}
                  </Button>
                </CardContent>
              </Card>
            )
          })}
        </div>

        {/* Features Comparison */}
        <Card className="bg-white">
          <CardHeader>
            <CardTitle>Feature Comparison</CardTitle>
            <CardDescription>
              See what's included in each plan
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b">
                    <th className="text-left p-4">Features</th>
                    <th className="text-center p-4">Trial</th>
                    <th className="text-center p-4">Starter</th>
                    <th className="text-center p-4">Professional</th>
                    <th className="text-center p-4">Enterprise</th>
                  </tr>
                </thead>
                <tbody className="text-sm">
                  <tr className="border-b">
                    <td className="p-4 font-medium">AI No-Show Predictions</td>
                    <td className="text-center p-4">Basic</td>
                    <td className="text-center p-4">✓</td>
                    <td className="text-center p-4">Advanced</td>
                    <td className="text-center p-4">Advanced</td>
                  </tr>
                  <tr className="border-b">
                    <td className="p-4 font-medium">Schedule Optimization</td>
                    <td className="text-center p-4">-</td>
                    <td className="text-center p-4">✓</td>
                    <td className="text-center p-4">✓</td>
                    <td className="text-center p-4">✓</td>
                  </tr>
                  <tr className="border-b">
                    <td className="p-4 font-medium">Custom Reports</td>
                    <td className="text-center p-4">-</td>
                    <td className="text-center p-4">-</td>
                    <td className="text-center p-4">✓</td>
                    <td className="text-center p-4">✓</td>
                  </tr>
                  <tr className="border-b">
                    <td className="p-4 font-medium">API Access</td>
                    <td className="text-center p-4">-</td>
                    <td className="text-center p-4">-</td>
                    <td className="text-center p-4">-</td>
                    <td className="text-center p-4">✓</td>
                  </tr>
                  <tr>
                    <td className="p-4 font-medium">Support</td>
                    <td className="text-center p-4">Email</td>
                    <td className="text-center p-4">Priority</td>
                    <td className="text-center p-4">Phone</td>
                    <td className="text-center p-4">Dedicated</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>

        {/* FAQ Section */}
        <div className="mt-12 text-center">
          <p className="text-gray-600">
            Have questions? Contact our sales team at{' '}
            <a href="mailto:sales@chronoguard.ai" className="text-blue-600 hover:text-blue-500">
              sales@chronoguard.ai
            </a>
          </p>
        </div>
      </div>
    </div>
  )
}