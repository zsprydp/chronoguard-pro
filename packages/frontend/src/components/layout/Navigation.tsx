'use client'

import { useState, useEffect } from 'react'
import { usePathname, useRouter } from 'next/navigation'
import { 
  BarChart3, 
  Calendar, 
  Users, 
  UserCheck, 
  Settings, 
  HelpCircle,
  LogOut,
  Menu,
  X,
  Home,
  Bell,
  CreditCard,
  ChevronDown,
  Shield,
  Zap
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent } from '@/components/ui/card'

interface NavigationProps {
  user?: {
    first_name: string
    last_name: string
    email: string
    subscription_status: string
    trial_days_left?: number
  }
}

export function Navigation({ user }: NavigationProps) {
  const pathname = usePathname()
  const router = useRouter()
  const [isSidebarOpen, setIsSidebarOpen] = useState(false)
  const [isProfileOpen, setIsProfileOpen] = useState(false)

  const mainNavItems = [
    {
      name: 'Dashboard',
      href: '/dashboard',
      icon: Home,
      current: pathname === '/dashboard',
      description: 'Overview and key metrics'
    },
    {
      name: 'Appointments',
      href: '/appointments',
      icon: Calendar,
      current: pathname.startsWith('/appointments'),
      description: 'Schedule and manage appointments',
      badge: 3 // High risk appointments count
    },
    {
      name: 'Patients',
      href: '/patients',
      icon: Users,
      current: pathname.startsWith('/patients'),
      description: 'Patient records and history'
    },
    {
      name: 'Providers',
      href: '/providers',
      icon: UserCheck,
      current: pathname.startsWith('/providers'),
      description: 'Healthcare provider management'
    },
    {
      name: 'Analytics',
      href: '/analytics',
      icon: BarChart3,
      current: pathname.startsWith('/analytics'),
      description: 'AI insights and reports'
    },
  ]

  const secondaryNavItems = [
    {
      name: 'Notifications',
      href: '/notifications',
      icon: Bell,
      current: pathname.startsWith('/notifications'),
      badge: 2 // Unread notifications
    },
    {
      name: 'Billing',
      href: '/billing',
      icon: CreditCard,
      current: pathname.startsWith('/billing')
    },
    {
      name: 'Settings',
      href: '/settings',
      icon: Settings,
      current: pathname.startsWith('/settings')
    },
    {
      name: 'Help & Support',
      href: '/help',
      icon: HelpCircle,
      current: pathname.startsWith('/help')
    }
  ]

  const handleLogout = () => {
    localStorage.removeItem('access_token')
    localStorage.removeItem('user')
    router.push('/auth/login')
  }

  const getSubscriptionBadge = () => {
    if (!user?.subscription_status) return null
    
    const badges = {
      trial: { label: 'Trial', className: 'bg-amber-100 text-amber-800', icon: Zap },
      starter: { label: 'Starter', className: 'bg-blue-100 text-blue-800', icon: Shield },
      professional: { label: 'Pro', className: 'bg-purple-100 text-purple-800', icon: Shield },
      enterprise: { label: 'Enterprise', className: 'bg-emerald-100 text-emerald-800', icon: Shield }
    }
    
    const badge = badges[user.subscription_status as keyof typeof badges] || badges.trial
    const Icon = badge.icon
    
    return (
      <Badge className={`${badge.className} flex items-center gap-1 text-xs`}>
        <Icon className="h-3 w-3" />
        {badge.label}
      </Badge>
    )
  }

  // Close sidebar when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      const sidebar = document.getElementById('mobile-sidebar')
      if (sidebar && !sidebar.contains(event.target as Node) && isSidebarOpen) {
        setIsSidebarOpen(false)
      }
    }

    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [isSidebarOpen])

  return (
    <>
      {/* Mobile menu button */}
      <div className="lg:hidden fixed top-4 left-4 z-50">
        <Button
          variant="outline"
          size="sm"
          onClick={() => setIsSidebarOpen(!isSidebarOpen)}
          className="bg-white shadow-sm"
        >
          {isSidebarOpen ? <X className="h-4 w-4" /> : <Menu className="h-4 w-4" />}
        </Button>
      </div>

      {/* Sidebar */}
      <div
        id="mobile-sidebar"
        className={`
          fixed inset-y-0 left-0 z-40 w-72 bg-white border-r border-gray-200 shadow-lg
          transform transition-transform duration-300 ease-in-out
          lg:translate-x-0 lg:static lg:inset-0
          ${isSidebarOpen ? 'translate-x-0' : '-translate-x-full'}
        `}
      >
        <div className="flex flex-col h-full">
          {/* Header */}
          <div className="p-6 border-b border-gray-100">
            <div className="flex items-center space-x-3">
              <div className="flex-shrink-0 w-10 h-10 bg-blue-600 rounded-lg flex items-center justify-center">
                <Shield className="h-6 w-6 text-white" />
              </div>
              <div className="flex-1 min-w-0">
                <h1 className="text-lg font-semibold text-gray-900 truncate">
                  ChronoGuard Pro
                </h1>
                <p className="text-sm text-gray-500">
                  AI-Powered Optimization
                </p>
              </div>
            </div>
          </div>

          {/* User Profile */}
          {user && (
            <div className="p-4 border-b border-gray-100">
              <Card className="bg-gradient-to-r from-blue-50 to-indigo-50 border-blue-100">
                <CardContent className="p-4">
                  <div className="flex items-center justify-between">
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-gray-900 truncate">
                        {user.first_name} {user.last_name}
                      </p>
                      <p className="text-xs text-gray-500 truncate">
                        {user.email}
                      </p>
                      {user.subscription_status === 'trial' && user.trial_days_left !== undefined && (
                        <p className="text-xs text-amber-600 font-medium mt-1">
                          {user.trial_days_left} days left in trial
                        </p>
                      )}
                    </div>
                    <div className="flex flex-col items-end space-y-1">
                      {getSubscriptionBadge()}
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          )}

          {/* Main Navigation */}
          <nav className="flex-1 overflow-y-auto">
            <div className="px-4 py-4 space-y-1">
              <p className="px-3 text-xs font-semibold text-gray-400 uppercase tracking-wider">
                Main Menu
              </p>
              {mainNavItems.map((item) => {
                const Icon = item.icon
                return (
                  <button
                    key={item.name}
                    onClick={() => {
                      router.push(item.href)
                      setIsSidebarOpen(false)
                    }}
                    className={`
                      group w-full flex items-center px-3 py-3 text-sm font-medium rounded-lg
                      transition-all duration-200 hover:scale-[1.02]
                      ${item.current
                        ? 'bg-blue-100 text-blue-700 border-l-4 border-blue-600'
                        : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
                      }
                    `}
                  >
                    <Icon
                      className={`
                        mr-3 flex-shrink-0 h-5 w-5 transition-colors
                        ${item.current ? 'text-blue-600' : 'text-gray-400 group-hover:text-gray-500'}
                      `}
                    />
                    <div className="flex-1 text-left">
                      <div className="flex items-center justify-between">
                        <span>{item.name}</span>
                        {item.badge && (
                          <Badge variant="destructive" className="ml-2 px-2 py-1 text-xs">
                            {item.badge}
                          </Badge>
                        )}
                      </div>
                      {item.description && (
                        <p className="text-xs text-gray-400 mt-1 group-hover:text-gray-500">
                          {item.description}
                        </p>
                      )}
                    </div>
                  </button>
                )
              })}
            </div>

            <div className="px-4 py-4 space-y-1 border-t border-gray-100">
              <p className="px-3 text-xs font-semibold text-gray-400 uppercase tracking-wider">
                Account & Support
              </p>
              {secondaryNavItems.map((item) => {
                const Icon = item.icon
                return (
                  <button
                    key={item.name}
                    onClick={() => {
                      router.push(item.href)
                      setIsSidebarOpen(false)
                    }}
                    className={`
                      group w-full flex items-center px-3 py-2 text-sm font-medium rounded-lg
                      transition-all duration-200
                      ${item.current
                        ? 'bg-gray-100 text-gray-900'
                        : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
                      }
                    `}
                  >
                    <Icon
                      className={`
                        mr-3 flex-shrink-0 h-4 w-4
                        ${item.current ? 'text-gray-700' : 'text-gray-400 group-hover:text-gray-500'}
                      `}
                    />
                    <span className="flex-1 text-left">{item.name}</span>
                    {item.badge && (
                      <Badge variant="secondary" className="ml-2 px-2 py-1 text-xs">
                        {item.badge}
                      </Badge>
                    )}
                  </button>
                )
              })}
            </div>
          </nav>

          {/* Footer */}
          <div className="p-4 border-t border-gray-100">
            <Button
              variant="ghost"
              onClick={handleLogout}
              className="w-full justify-start text-gray-600 hover:text-gray-900 hover:bg-gray-50"
            >
              <LogOut className="mr-3 h-4 w-4" />
              Sign out
            </Button>
          </div>
        </div>
      </div>

      {/* Mobile overlay */}
      {isSidebarOpen && (
        <div
          className="fixed inset-0 z-30 bg-black bg-opacity-50 lg:hidden"
          onClick={() => setIsSidebarOpen(false)}
        />
      )}
    </>
  )
}