"use client"

import * as React from "react"
import { X, CheckCircle, AlertCircle, AlertTriangle, Info } from "lucide-react"
import { cn } from "@/lib/utils"

// Toast types for different feedback scenarios
type ToastVariant = "success" | "error" | "warning" | "info"

interface ToastProps {
  id: string
  title?: string
  message: string
  variant?: ToastVariant
  duration?: number
  onClose: (id: string) => void
}

const variantStyles = {
  success: {
    container: "bg-emerald-50 border-emerald-200 text-emerald-800",
    icon: CheckCircle,
    iconColor: "text-emerald-600"
  },
  error: {
    container: "bg-red-50 border-red-200 text-red-800",
    icon: AlertCircle,
    iconColor: "text-red-600"
  },
  warning: {
    container: "bg-amber-50 border-amber-200 text-amber-800",
    icon: AlertTriangle,
    iconColor: "text-amber-600"
  },
  info: {
    container: "bg-blue-50 border-blue-200 text-blue-800",
    icon: Info,
    iconColor: "text-blue-600"
  }
}

export function Toast({ id, title, message, variant = "info", duration = 5000, onClose }: ToastProps) {
  const [isVisible, setIsVisible] = React.useState(false)
  const [isExiting, setIsExiting] = React.useState(false)

  const style = variantStyles[variant]
  const Icon = style.icon

  React.useEffect(() => {
    // Entrance animation
    const timer = setTimeout(() => setIsVisible(true), 10)
    return () => clearTimeout(timer)
  }, [])

  React.useEffect(() => {
    if (duration > 0) {
      const timer = setTimeout(() => handleClose(), duration)
      return () => clearTimeout(timer)
    }
  }, [duration, id])

  const handleClose = () => {
    setIsExiting(true)
    setTimeout(() => onClose(id), 300)
  }

  return (
    <div
      className={cn(
        "pointer-events-auto relative flex w-full max-w-sm transform rounded-lg border p-4 shadow-lg transition-all duration-300 ease-in-out",
        style.container,
        isVisible && !isExiting ? "translate-x-0 opacity-100 scale-100" : "translate-x-full opacity-0 scale-95"
      )}
      role="alert"
      aria-live="polite"
      aria-atomic="true"
    >
      <div className="flex items-start space-x-3">
        <Icon 
          className={cn("h-5 w-5 flex-shrink-0 mt-0.5", style.iconColor)}
          aria-hidden="true"
        />
        <div className="flex-1 min-w-0">
          {title && (
            <h4 className="text-sm font-semibold mb-1">
              {title}
            </h4>
          )}
          <p className="text-sm">
            {message}
          </p>
        </div>
        <button
          onClick={handleClose}
          className={cn(
            "flex-shrink-0 rounded-md p-1.5 inline-flex focus:outline-none focus:ring-2 focus:ring-offset-2 transition-colors",
            variant === "success" && "text-emerald-500 hover:bg-emerald-100 focus:ring-emerald-500",
            variant === "error" && "text-red-500 hover:bg-red-100 focus:ring-red-500",
            variant === "warning" && "text-amber-500 hover:bg-amber-100 focus:ring-amber-500",
            variant === "info" && "text-blue-500 hover:bg-blue-100 focus:ring-blue-500"
          )}
          aria-label="Close notification"
        >
          <X className="h-4 w-4" />
        </button>
      </div>
    </div>
  )
}

// Toast Container Component
interface ToastContainerProps {
  toasts: Array<{
    id: string
    title?: string
    message: string
    variant?: ToastVariant
    duration?: number
  }>
  onRemoveToast: (id: string) => void
}

export function ToastContainer({ toasts, onRemoveToast }: ToastContainerProps) {
  if (toasts.length === 0) return null

  return (
    <div 
      className="fixed top-4 right-4 z-50 space-y-2 pointer-events-none"
      aria-label="Notifications"
    >
      {toasts.map((toast) => (
        <Toast
          key={toast.id}
          {...toast}
          onClose={onRemoveToast}
        />
      ))}
    </div>
  )
}

// Hook for managing toasts
export function useToast() {
  const [toasts, setToasts] = React.useState<Array<{
    id: string
    title?: string
    message: string
    variant?: ToastVariant
    duration?: number
  }>>([])

  const addToast = React.useCallback((toast: Omit<typeof toasts[0], 'id'>) => {
    const id = Math.random().toString(36).substr(2, 9)
    setToasts(prev => [...prev, { ...toast, id }])
  }, [])

  const removeToast = React.useCallback((id: string) => {
    setToasts(prev => prev.filter(toast => toast.id !== id))
  }, [])

  const toast = React.useCallback({
    success: (message: string, title?: string) => addToast({ message, title, variant: 'success' }),
    error: (message: string, title?: string) => addToast({ message, title, variant: 'error' }),
    warning: (message: string, title?: string) => addToast({ message, title, variant: 'warning' }),
    info: (message: string, title?: string) => addToast({ message, title, variant: 'info' }),
  }, [addToast])

  return {
    toasts,
    toast,
    removeToast
  }
}