'use client';

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from "recharts";

const data = [
  { name: "Casas", value: 12, rent: 8500 },
  { name: "Apartamentos", value: 8, rent: 6200 },
  { name: "Locales", value: 5, rent: 4800 },
  { name: "Oficinas", value: 3, rent: 3500 },
];

const COLORS = ['#22c55e', '#3b82f6', '#f59e0b', '#ec4899'];

export function PropertiesChart() {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Distribución de Propiedades</CardTitle>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={350}>
          <PieChart>
            <Pie
              data={data}
              cx="50%"
              cy="50%"
              labelLine={false}
              label={({ name, value, percent }) => 
                `${name} (${value})`
              }
              outerRadius={120}
              innerRadius={60}
              paddingAngle={5}
              dataKey="value"
            >
              {data.map((entry, index) => (
                <Cell 
                  key={`cell-${index}`} 
                  fill={COLORS[index % COLORS.length]}
                  strokeWidth={2}
                />
              ))}
            </Pie>
            <Tooltip
              contentStyle={{ 
                backgroundColor: 'hsl(224 71% 4%)',
                border: '1px solid hsl(215 27.9% 16.9%)',
                borderRadius: '6px',
                color: 'white'
              }}
              formatter={(value, name) => [`${value} unidades`, name]}
            />
            <Legend 
              verticalAlign="bottom" 
              height={36}
              formatter={(value) => <span style={{ color: 'white' }}>{value}</span>}
            />
          </PieChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
}
