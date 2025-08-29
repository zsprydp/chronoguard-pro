'use client'

import React, { useState } from 'react'
import { Button } from './button'
import { cn } from '@/lib/utils'
import { 
  Plus,
  Calendar,
  Users,
  UserPlus,
  Zap,
  X,
  ChevronUp
} from 'lucide-react'

interface FABAction {
  icon: React.ComponentType<{ className?: string }>
  label: string
  onClick: () => void
  className?: string
}

interface FloatingActionButtonProps {
  actions: FABAction[]
  className?: string
}

export function FloatingActionButton({ actions, className }: FloatingActionButtonProps) {
  const [isOpen, setIsOpen] = useState(false)

  const toggleOpen = () => setIsOpen(!isOpen)

  return (
    <div className={cn('fixed bottom-6 right-6 z-50', className)}>
      {/* Action Items */}
      <div className="flex flex-col space-y-2 mb-4">
        {actions.map((action, index) => {
          const Icon = action.icon
          return (
            <div
              key={index}
              className={cn(
                'transform transition-all duration-300 ease-in-out',
                isOpen 
                  ? 'translate-y-0 opacity-100 scale-100' 
                  : 'translate-y-4 opacity-0 scale-95 pointer-events-none',
                `delay-${index * 50}`
              )}
            >
              <div className="flex items-center space-x-3">
                <span className="bg-gray-900 text-white text-xs px-3 py-2 rounded-lg shadow-lg whitespace-nowrap">
                  {action.label}
                </span>
                <Button
                  size="sm"
                  className={cn(
                    'h-12 w-12 rounded-full shadow-lg hover:shadow-xl transform hover:scale-110 transition-all duration-200',
                    action.className || 'bg-blue-600 hover:bg-blue-700'
                  )}
                  onClick={() => {
                    action.onClick()
                    setIsOpen(false)
                  }}
                >
                  <Icon className="h-5 w-5" />
                </Button>
              </div>
            </div>
          )
        })}
      </div>

      {/* Main FAB */}
      <Button
        size="lg"
        onClick={toggleOpen}
        className={cn(
          'h-16 w-16 rounded-full shadow-xl hover:shadow-2xl bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800',
          'transform transition-all duration-300 hover:scale-110 active:scale-95',
          'focus:outline-none focus:ring-4 focus:ring-blue-300 focus:ring-offset-2',
          isOpen && 'rotate-45'
        )}
        aria-label={isOpen ? 'Close quick actions' : 'Open quick actions'}
        aria-expanded={isOpen}
      >
        {isOpen ? (
          <X className="h-6 w-6 transition-transform duration-300" />
        ) : (
          <Plus className="h-6 w-6 transition-transform duration-300" />
        )}
      </Button>

      {/* Background overlay for mobile */}
      {isOpen && (
        <div 
          className="fixed inset-0 bg-black bg-opacity-25 -z-10 md:hidden"
          onClick={() => setIsOpen(false)}
        />
      )}
    </div>
  )
}

// Pre-configured FAB for dashboard
export function DashboardFAB() {
  const actions: FABAction[] = [
    {
      icon: Calendar,
      label: 'New Appointment',
      onClick: () => {
        // Navigate to appointment creation
        window.location.href = '/appointments/new'
      },
      className: 'bg-emerald-600 hover:bg-emerald-700'
    },
    {
      icon: UserPlus,
      label: 'Add Patient',
      onClick: () => {
        // Navigate to patient creation
        window.location.href = '/patients/new'
      },
      className: 'bg-purple-600 hover:bg-purple-700'
    },
    {
      icon: Users,
      label: 'Add Provider',
      onClick: () => {
        // Navigate to provider creation
        window.location.href = '/providers/new'
      },
      className: 'bg-amber-600 hover:bg-amber-700'
    },
    {
      icon: Zap,
      label: 'Optimize Schedule',
      onClick: () => {
        // Trigger schedule optimization
        console.log('Optimizing schedule...')
        // Add toast notification here
      },
      className: 'bg-orange-600 hover:bg-orange-700'
    }
  ]

  return <FloatingActionButton actions={actions} />
}