'use client';

import { Card } from "@/components/ui/card";
import { CheckCircle2, Circle, Clock } from "lucide-react";
import { cn } from "@/lib/utils";

type Task = {
  id: number;
  title: string;
  dueDate: string;
  priority: 'high' | 'medium' | 'low';
  completed: boolean;
};

const priorityColors = {
  high: 'text-red-500',
  medium: 'text-yellow-500',
  low: 'text-blue-500',
};

export default function TaskList() {
  const tasks: Task[] = [
    {
      id: 1,
      title: 'Revisar solicitud de mantenimiento Apt 301',
      dueDate: '2024-01-16',
      priority: 'high',
      completed: false,
    },
    {
      id: 2,
      title: 'Renovar seguro propiedad Casa 123',
      dueDate: '2024-01-20',
      priority: 'medium',
      completed: false,
    },
    {
      id: 3,
      title: 'Actualizar documentación contrato Local 45',
      dueDate: '2024-01-18',
      priority: 'low',
      completed: true,
    },
    {
      id: 4,
      title: 'Contactar inquilino para inspección',
      dueDate: '2024-01-17',
      priority: 'medium',
      completed: false,
    },
  ];

  return (
    <Card className="p-6">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-lg font-medium">Tareas Pendientes</h3>
        <span className="text-sm text-muted-foreground">
          {tasks.filter(t => !t.completed).length} pendientes
        </span>
      </div>
      <div className="space-y-3">
        {tasks.map((task) => (
          <div
            key={task.id}
            className={cn(
              "flex items-start gap-3 p-3 rounded-lg transition-colors",
              task.completed ? "opacity-50" : "hover:bg-accent/5"
            )}
          >
            {task.completed ? (
              <CheckCircle2 className="h-5 w-5 text-green-500 flex-shrink-0" />
            ) : (
              <Circle className="h-5 w-5 text-muted-foreground flex-shrink-0" />
            )}
            <div className="flex-1 min-w-0">
              <p className={cn(
                "font-medium",
                task.completed && "line-through"
              )}>
                {task.title}
              </p>
              <div className="flex items-center gap-2 text-sm text-muted-foreground">
                <Clock className="h-3 w-3" />
                <span>Vence: {task.dueDate}</span>
                <span className={cn(
                  "px-2 py-0.5 rounded-full text-xs",
                  priorityColors[task.priority]
                )}>
                  {task.priority}
                </span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </Card>
  );
}
