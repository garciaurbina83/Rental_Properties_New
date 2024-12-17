'use client';

import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { ArrowUpDown } from "lucide-react";

export type SortOption = {
  value: string;
  label: string;
  field: string;
  direction: 'asc' | 'desc';
};

interface PropertySortProps {
  onSort: (option: SortOption) => void;
}

const sortOptions: SortOption[] = [
  { value: "price-asc", label: "Precio: Menor a Mayor", field: "price", direction: "asc" },
  { value: "price-desc", label: "Precio: Mayor a Menor", field: "price", direction: "desc" },
  { value: "date-desc", label: "Más Recientes", field: "createdAt", direction: "desc" },
  { value: "date-asc", label: "Más Antiguos", field: "createdAt", direction: "asc" },
  { value: "name-asc", label: "Nombre: A-Z", field: "name", direction: "asc" },
  { value: "name-desc", label: "Nombre: Z-A", field: "name", direction: "desc" },
];

export default function PropertySort({ onSort }: PropertySortProps) {
  const handleSortChange = (value: string) => {
    const option = sortOptions.find((opt) => opt.value === value);
    if (option) {
      onSort(option);
    }
  };

  return (
    <Select onValueChange={handleSortChange}>
      <SelectTrigger className="w-[200px]">
        <div className="flex items-center gap-2">
          <ArrowUpDown className="h-4 w-4" />
          <SelectValue placeholder="Ordenar por..." />
        </div>
      </SelectTrigger>
      <SelectContent>
        {sortOptions.map((option) => (
          <SelectItem key={option.value} value={option.value}>
            {option.label}
          </SelectItem>
        ))}
      </SelectContent>
    </Select>
  );
}
