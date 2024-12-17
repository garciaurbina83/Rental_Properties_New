import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";
import { Property } from "@/schemas/property";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";

interface PropertyStatusProps {
  status: Property['status'];
  showTooltip?: boolean;
  className?: string;
}

export const statusColors = {
  available: "bg-green-500 hover:bg-green-600",
  rented: "bg-blue-500 hover:bg-blue-600",
  maintenance: "bg-yellow-500 hover:bg-yellow-600",
  sold: "bg-gray-500 hover:bg-gray-600",
} as const;

export const statusText = {
  available: "Disponible",
  rented: "Rentada",
  maintenance: "Mantenimiento",
  sold: "Vendida",
} as const;

export const statusDescriptions = {
  available: "La propiedad está disponible para renta o venta",
  rented: "La propiedad está actualmente rentada",
  maintenance: "La propiedad está en mantenimiento",
  sold: "La propiedad ha sido vendida",
} as const;

export default function PropertyStatus({ status, showTooltip = false, className }: PropertyStatusProps) {
  const badge = (
    <Badge 
      className={cn(
        statusColors[status],
        "cursor-default transition-colors",
        className
      )}
    >
      {statusText[status]}
    </Badge>
  );

  if (!showTooltip) {
    return badge;
  }

  return (
    <TooltipProvider>
      <Tooltip>
        <TooltipTrigger asChild>
          {badge}
        </TooltipTrigger>
        <TooltipContent>
          <p>{statusDescriptions[status]}</p>
        </TooltipContent>
      </Tooltip>
    </TooltipProvider>
  );
}

export function PropertyStatusSelect({ 
  value, 
  onChange,
  disabled = false,
  error
}: {
  value: Property['status'];
  onChange: (value: Property['status']) => void;
  disabled?: boolean;
  error?: string;
}) {
  return (
    <div className="space-y-2">
      <div className="flex flex-wrap gap-2">
        {(Object.keys(statusText) as Array<Property['status']>).map((status) => (
          <Badge
            key={status}
            className={cn(
              statusColors[status],
              "cursor-pointer transition-colors",
              value === status && "ring-2 ring-offset-2",
              disabled && "opacity-50 cursor-not-allowed"
            )}
            onClick={() => !disabled && onChange(status)}
          >
            {statusText[status]}
          </Badge>
        ))}
      </div>
      {error && (
        <p className="text-sm text-red-500">{error}</p>
      )}
    </div>
  );
}
