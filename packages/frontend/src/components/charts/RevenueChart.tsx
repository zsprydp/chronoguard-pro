'use client'

import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'

const data = [
  { month: 'Jan', saved: 2400 },
  { month: 'Feb', saved: 1398 },
  { month: 'Mar', saved: 9800 },
  { month: 'Apr', saved: 3908 },
  { month: 'May', saved: 4800 },
  { month: 'Jun', saved: 3800 },
  { month: 'Jul', saved: 4300 },
  { month: 'Aug', saved: 8420 },
]

export function RevenueChart() {
  return (
    <div className="h-[300px] w-full">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="month" />
          <YAxis />
          <Tooltip formatter={(value) => [`$${value}`, 'Revenue Saved']} />
          <Line type="monotone" dataKey="saved" stroke="#3b82f6" strokeWidth={2} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}