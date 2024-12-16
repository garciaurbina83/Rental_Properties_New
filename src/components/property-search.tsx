'use client';

import {
  Command,
  CommandDialog,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
} from "@/components/ui/command";
import { Property } from "@/types/property";
import { Search } from "lucide-react";

interface PropertySearchProps {
  onSearch: (query: string) => void;
  searchResults?: Property[];
  onPropertySelect?: (property: Property) => void;
}

export default function PropertySearch({ 
  onSearch, 
  searchResults = [], 
  onPropertySelect 
}: PropertySearchProps) {
  return (
    <Command className="rounded-lg border shadow-md">
      <div className="flex items-center gap-2 px-3">
        <Search className="h-4 w-4 text-muted-foreground/70" />
        <CommandInput 
          placeholder="Buscar propiedades..." 
          className="h-9"
          onValueChange={onSearch}
        />
      </div>
      {searchResults.length > 0 && (
        <CommandList className="absolute top-full left-0 right-0 z-50 mt-2 rounded-lg border bg-popover shadow-md">
          <CommandEmpty>No se encontraron resultados.</CommandEmpty>
          <CommandGroup heading="Propiedades">
            {searchResults.map((property) => (
              <CommandItem
                key={property.id}
                value={property.name}
                onSelect={() => onPropertySelect?.(property)}
                className="cursor-pointer"
              >
                <div className="flex items-center gap-2">
                  <div className="h-10 w-10 rounded-md bg-accent/10">
                    {/* Aquí podríamos agregar una imagen en miniatura */}
                  </div>
                  <div>
                    <p className="font-medium">{property.name}</p>
                    <p className="text-sm text-muted-foreground">
                      {property.address.city}, {property.address.state}
                    </p>
                  </div>
                </div>
              </CommandItem>
            ))}
          </CommandGroup>
        </CommandList>
      )}
    </Command>
  );
}
