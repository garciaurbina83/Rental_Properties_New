'use client';

import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { Card } from "@/components/ui/card";

const data = [
  { name: 'Jan', pending: 5, signed: 0, lost: 0 },
  { name: 'Feb', pending: 8, signed: 0, lost: 0 },
  { name: 'Mar', pending: 7, signed: 0, lost: 0 },
  { name: 'Apr', pending: 4, signed: 0, lost: 0 },
  { name: 'May', pending: 10, signed: 0, lost: 0 },
  { name: 'Jun', pending: 8, signed: 12, lost: 5 },
  { name: 'Jul', pending: 15, signed: 0, lost: 0 },
  { name: 'Aug', pending: 17, signed: 0, lost: 0 },
  { name: 'Sep', pending: 8, signed: 0, lost: 0 },
  { name: 'Oct', pending: 10, signed: 0, lost: 0 },
  { name: 'Nov', pending: 4, signed: 0, lost: 0 },
  { name: 'Dec', pending: 7, signed: 0, lost: 0 },
];

export function RevenueChart() {
  return (
    <Card className="p-6 bg-secondary">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="text-lg font-semibold">Revenue Flow</h3>
          <p className="text-sm text-muted-foreground">Jan 10 - Jan 16</p>
        </div>
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 rounded-full bg-[#FDB022]" />
            <span className="text-sm text-muted-foreground">Pending</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 rounded-full bg-[#22C55E]" />
            <span className="text-sm text-muted-foreground">Signed</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 rounded-full bg-[#FF5757]" />
            <span className="text-sm text-muted-foreground">Lost</span>
          </div>
        </div>
      </div>
      <div className="h-[300px] w-full">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={data} margin={{ top: 5, right: 5, bottom: 5, left: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#374151" vertical={false} />
            <XAxis 
              dataKey="name" 
              stroke="#9CA3AF" 
              axisLine={false}
              tickLine={false}
              dy={10}
              tick={{ fontSize: 12 }}
            />
            <YAxis 
              stroke="#9CA3AF" 
              axisLine={false}
              tickLine={false}
              dx={-10}
              tick={{ fontSize: 12 }}
              tickFormatter={(value) => `${value}%`}
              domain={[0, 25]}
              ticks={[0, 5, 10, 15, 20, 25]}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: '#1F2937',
                border: 'none',
                borderRadius: '8px',
                boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
              }}
              formatter={(value: number) => [`${value}%`]}
            />
            <Area
              type="monotone"
              dataKey="pending"
              stroke="#FDB022"
              fill="#FDB022"
              fillOpacity={0.1}
              strokeWidth={2}
              dot={false}
              activeDot={{ r: 4, fill: "#FDB022" }}
            />
            <Area
              type="monotone"
              dataKey="signed"
              stroke="#22C55E"
              fill="#22C55E"
              fillOpacity={0.1}
              strokeWidth={2}
              dot={false}
              activeDot={{ r: 4, fill: "#22C55E" }}
            />
            <Area
              type="monotone"
              dataKey="lost"
              stroke="#FF5757"
              fill="#FF5757"
              fillOpacity={0.1}
              strokeWidth={2}
              dot={false}
              activeDot={{ r: 4, fill: "#FF5757" }}
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </Card>
  );
}
