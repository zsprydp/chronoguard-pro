'use client'

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'

export default function HomePage() {
  const router = useRouter()

  useEffect(() => {
    // Check if user is authenticated
    const token = localStorage.getItem('access_token')
    const user = localStorage.getItem('user')

    if (token && user) {
      // User is logged in, redirect to dashboard
      router.push('/dashboard')
    } else {
      // User not logged in, redirect to login
      router.push('/auth/login')
    }
  }, [router])

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 flex items-center justify-center">
      <div className="text-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
        <p className="text-gray-600">Loading ChronoGuard Pro...</p>
      </div>
    </div>
  )
}