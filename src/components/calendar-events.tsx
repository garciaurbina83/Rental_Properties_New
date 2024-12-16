'use client';

import { Card } from "@/components/ui/card";
import { CalendarDays, Clock } from "lucide-react";

type Event = {
  id: number;
  title: string;
  date: string;
  type: 'payment' | 'contract' | 'maintenance' | 'inspection';
  status: 'upcoming' | 'today' | 'overdue';
};

const eventTypes = {
  payment: { color: 'text-green-500', bgColor: 'bg-green-50' },
  contract: { color: 'text-blue-500', bgColor: 'bg-blue-50' },
  maintenance: { color: 'text-orange-500', bgColor: 'bg-orange-50' },
  inspection: { color: 'text-purple-500', bgColor: 'bg-purple-50' },
};

const statusColors = {
  upcoming: 'text-gray-600',
  today: 'text-green-600',
  overdue: 'text-red-600',
};

export default function CalendarEvents() {
  const events: Event[] = [
    {
      id: 1,
      title: 'Vencimiento Contrato - Apt 301',
      date: '2024-01-20',
      type: 'contract',
      status: 'upcoming',
    },
    {
      id: 2,
      title: 'Pago Mensual - Casa 123',
      date: '2024-01-15',
      type: 'payment',
      status: 'today',
    },
    {
      id: 3,
      title: 'Inspección Anual - Local 45',
      date: '2024-01-25',
      type: 'inspection',
      status: 'upcoming',
    },
    {
      id: 4,
      title: 'Mantenimiento Programado',
      date: '2024-01-18',
      type: 'maintenance',
      status: 'upcoming',
    },
  ];

  return (
    <Card className="p-6">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-lg font-medium">Próximos Eventos</h3>
        <CalendarDays className="h-5 w-5 text-muted-foreground" />
      </div>
      <div className="space-y-4">
        {events.map((event) => (
          <div
            key={event.id}
            className="flex items-start gap-4 p-3 rounded-lg hover:bg-accent/5 transition-colors"
          >
            <div
              className={`w-2 h-2 mt-2 rounded-full ${
                eventTypes[event.type].bgColor
              }`}
            />
            <div className="flex-1 min-w-0">
              <p className="font-medium truncate">{event.title}</p>
              <div className="flex items-center gap-2 text-sm">
                <Clock className="h-3 w-3 text-muted-foreground" />
                <span className={statusColors[event.status]}>{event.date}</span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </Card>
  );
}
