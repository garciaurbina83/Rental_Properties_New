import { useEffect, useState } from 'react';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { PropertyFilters } from '@/hooks/useProperties';
import { Button } from '@/components/ui/button';
import { PropertyStatusSelect } from '@/components/property-status';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
  SheetTrigger,
} from '@/components/ui/sheet';
import { SlidersHorizontal, X } from 'lucide-react';
import { cn } from '@/lib/utils';

interface PropertyFiltersProps {
  initialFilters?: PropertyFilters;
  onFiltersChange: (filters: PropertyFilters) => void;
  className?: string;
}

export default function PropertyFilters({
  initialFilters = {},
  onFiltersChange,
  className,
}: PropertyFiltersProps) {
  const [filters, setFilters] = useState<PropertyFilters>(initialFilters);
  const [isOpen, setIsOpen] = useState(false);

  // Actualizar filtros cuando cambien los iniciales
  useEffect(() => {
    setFilters(initialFilters);
  }, [initialFilters]);

  const handleFilterChange = (key: keyof PropertyFilters, value: any) => {
    const newFilters = { ...filters, [key]: value };
    setFilters(newFilters);
    onFiltersChange(newFilters);
  };

  const handleClearFilters = () => {
    setFilters({});
    onFiltersChange({});
    setIsOpen(false);
  };

  const activeFiltersCount = Object.values(filters).filter(Boolean).length;

  return (
    <div className={cn("space-y-4", className)}>
      {/* Barra de búsqueda siempre visible */}
      <div className="flex gap-2">
        <Input
          placeholder="Buscar propiedades..."
          value={filters.search || ''}
          onChange={(e) => handleFilterChange('search', e.target.value)}
          className="flex-1"
        />
        <Sheet open={isOpen} onOpenChange={setIsOpen}>
          <SheetTrigger asChild>
            <Button variant="outline" className="relative">
              <SlidersHorizontal className="h-4 w-4" />
              {activeFiltersCount > 0 && (
                <span className="absolute -top-1 -right-1 h-4 w-4 rounded-full bg-primary text-primary-foreground text-xs flex items-center justify-center">
                  {activeFiltersCount}
                </span>
              )}
            </Button>
          </SheetTrigger>
          <SheetContent>
            <SheetHeader>
              <SheetTitle>Filtros de Búsqueda</SheetTitle>
              <SheetDescription>
                Ajusta los filtros para encontrar las propiedades que buscas
              </SheetDescription>
            </SheetHeader>

            <div className="space-y-6 py-6">
              {/* Tipo de Propiedad */}
              <div className="space-y-2">
                <Label>Tipo de Propiedad</Label>
                <Select
                  value={filters.type || ''}
                  onValueChange={(value) => handleFilterChange('type', value)}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Todos los tipos" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="">Todos los tipos</SelectItem>
                    <SelectItem value="house">Casa</SelectItem>
                    <SelectItem value="apartment">Apartamento</SelectItem>
                    <SelectItem value="commercial">Comercial</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              {/* Estado */}
              <div className="space-y-2">
                <Label>Estado</Label>
                <PropertyStatusSelect
                  value={filters.status as any || 'available'}
                  onChange={(value) => handleFilterChange('status', value)}
                />
              </div>

              {/* Rango de Precio */}
              <div className="space-y-4">
                <Label>Rango de Precio</Label>
                <div className="flex gap-4">
                  <div className="flex-1 space-y-2">
                    <Label>Mínimo</Label>
                    <Input
                      type="number"
                      placeholder="0"
                      value={filters.minPrice || ''}
                      onChange={(e) => handleFilterChange('minPrice', e.target.value ? Number(e.target.value) : undefined)}
                    />
                  </div>
                  <div className="flex-1 space-y-2">
                    <Label>Máximo</Label>
                    <Input
                      type="number"
                      placeholder="Sin límite"
                      value={filters.maxPrice || ''}
                      onChange={(e) => handleFilterChange('maxPrice', e.target.value ? Number(e.target.value) : undefined)}
                    />
                  </div>
                </div>
              </div>

              {/* Habitaciones y Baños */}
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label>Habitaciones (mín.)</Label>
                  <Select
                    value={filters.minBedrooms?.toString() || ''}
                    onValueChange={(value) => handleFilterChange('minBedrooms', value ? Number(value) : undefined)}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Cualquiera" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="">Cualquiera</SelectItem>
                      <SelectItem value="1">1+</SelectItem>
                      <SelectItem value="2">2+</SelectItem>
                      <SelectItem value="3">3+</SelectItem>
                      <SelectItem value="4">4+</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label>Baños (mín.)</Label>
                  <Select
                    value={filters.minBathrooms?.toString() || ''}
                    onValueChange={(value) => handleFilterChange('minBathrooms', value ? Number(value) : undefined)}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Cualquiera" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="">Cualquiera</SelectItem>
                      <SelectItem value="1">1+</SelectItem>
                      <SelectItem value="2">2+</SelectItem>
                      <SelectItem value="3">3+</SelectItem>
                      <SelectItem value="4">4+</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>

              {/* Botón para limpiar filtros */}
              {activeFiltersCount > 0 && (
                <Button
                  variant="outline"
                  className="w-full"
                  onClick={handleClearFilters}
                >
                  <X className="h-4 w-4 mr-2" />
                  Limpiar Filtros
                </Button>
              )}
            </div>
          </SheetContent>
        </Sheet>
      </div>

      {/* Chips de filtros activos */}
      {activeFiltersCount > 0 && (
        <div className="flex flex-wrap gap-2">
          {filters.type && (
            <Button
              variant="secondary"
              size="sm"
              className="h-7"
              onClick={() => handleFilterChange('type', undefined)}
            >
              Tipo: {filters.type}
              <X className="h-4 w-4 ml-2" />
            </Button>
          )}
          {filters.status && (
            <Button
              variant="secondary"
              size="sm"
              className="h-7"
              onClick={() => handleFilterChange('status', undefined)}
            >
              Estado: {filters.status}
              <X className="h-4 w-4 ml-2" />
            </Button>
          )}
          {(filters.minPrice || filters.maxPrice) && (
            <Button
              variant="secondary"
              size="sm"
              className="h-7"
              onClick={() => {
                handleFilterChange('minPrice', undefined);
                handleFilterChange('maxPrice', undefined);
              }}
            >
              Precio: {filters.minPrice || 0} - {filters.maxPrice || '∞'}
              <X className="h-4 w-4 ml-2" />
            </Button>
          )}
          {filters.minBedrooms && (
            <Button
              variant="secondary"
              size="sm"
              className="h-7"
              onClick={() => handleFilterChange('minBedrooms', undefined)}
            >
              {filters.minBedrooms}+ habitaciones
              <X className="h-4 w-4 ml-2" />
            </Button>
          )}
          {filters.minBathrooms && (
            <Button
              variant="secondary"
              size="sm"
              className="h-7"
              onClick={() => handleFilterChange('minBathrooms', undefined)}
            >
              {filters.minBathrooms}+ baños
              <X className="h-4 w-4 ml-2" />
            </Button>
          )}
        </div>
      )}
    </div>
  );
}
