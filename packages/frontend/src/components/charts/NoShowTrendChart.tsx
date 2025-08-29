'use client'

import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'

const data = [
  { month: 'Jan', rate: 15.2 },
  { month: 'Feb', rate: 14.8 },
  { month: 'Mar', rate: 13.5 },
  { month: 'Apr', rate: 12.9 },
  { month: 'May', rate: 13.2 },
  { month: 'Jun', rate: 12.1 },
  { month: 'Jul', rate: 11.8 },
  { month: 'Aug', rate: 12.8 },
]

export function NoShowTrendChart() {
  return (
    <div className="h-[300px] w-full">
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="month" />
          <YAxis />
          <Tooltip formatter={(value) => [`${value}%`, 'No-Show Rate']} />
          <Area type="monotone" dataKey="rate" stroke="#ef4444" fill="#ef4444" fillOpacity={0.2} />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  )
}