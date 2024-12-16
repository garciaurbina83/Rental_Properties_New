'use client';

import { Property } from "@/types/property";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Edit, Trash, MoreHorizontal } from "lucide-react";
import { cn } from "@/lib/utils";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";

interface PropertiesTableProps {
  properties: Property[];
  onEdit?: (property: Property) => void;
  onDelete?: (property: Property) => void;
  onClick?: (property: Property) => void;
}

const statusColors = {
  available: "bg-green-500/10 text-green-500",
  occupied: "bg-blue-500/10 text-blue-500",
  maintenance: "bg-yellow-500/10 text-yellow-500",
};

const statusText = {
  available: "Disponible",
  occupied: "Ocupado",
  maintenance: "Mantenimiento",
};

export default function PropertiesTable({ 
  properties,
  onEdit,
  onDelete,
  onClick
}: PropertiesTableProps) {
  return (
    <div className="rounded-md border">
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Nombre</TableHead>
            <TableHead>Dirección</TableHead>
            <TableHead>Tipo</TableHead>
            <TableHead>Estado</TableHead>
            <TableHead>Habitaciones</TableHead>
            <TableHead>Baños</TableHead>
            <TableHead>Área</TableHead>
            <TableHead className="text-right">Precio</TableHead>
            <TableHead className="w-[70px]"></TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {properties.map((property) => (
            <TableRow
              key={property.id}
              className={cn(onClick && "cursor-pointer hover:bg-accent/5")}
              onClick={() => onClick?.(property)}
            >
              <TableCell className="font-medium">{property.name}</TableCell>
              <TableCell className="max-w-[200px] truncate">
                {property.address.street}, {property.address.city}
              </TableCell>
              <TableCell className="capitalize">{property.type}</TableCell>
              <TableCell>
                <Badge className={cn(statusColors[property.status])}>
                  {statusText[property.status]}
                </Badge>
              </TableCell>
              <TableCell>{property.features.bedrooms}</TableCell>
              <TableCell>{property.features.bathrooms}</TableCell>
              <TableCell>{property.features.squareMeters}m²</TableCell>
              <TableCell className="text-right">
                ${property.price.toLocaleString()}
              </TableCell>
              <TableCell>
                <DropdownMenu>
                  <DropdownMenuTrigger asChild>
                    <Button
                      variant="ghost"
                      className="h-8 w-8 p-0"
                      onClick={(e) => e.stopPropagation()}
                    >
                      <MoreHorizontal className="h-4 w-4" />
                    </Button>
                  </DropdownMenuTrigger>
                  <DropdownMenuContent align="end">
                    <DropdownMenuLabel>Acciones</DropdownMenuLabel>
                    {onEdit && (
                      <DropdownMenuItem onClick={(e) => {
                        e.stopPropagation();
                        onEdit(property);
                      }}>
                        <Edit className="mr-2 h-4 w-4" />
                        Editar
                      </DropdownMenuItem>
                    )}
                    {onDelete && (
                      <>
                        <DropdownMenuSeparator />
                        <DropdownMenuItem
                          className="text-destructive focus:text-destructive"
                          onClick={(e) => {
                            e.stopPropagation();
                            onDelete(property);
                          }}
                        >
                          <Trash className="mr-2 h-4 w-4" />
                          Eliminar
                        </DropdownMenuItem>
                      </>
                    )}
                  </DropdownMenuContent>
                </DropdownMenu>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
}
