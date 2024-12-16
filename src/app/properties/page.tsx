'use client';

import { useState, useEffect } from 'react';
import { propertyService } from '@/services/propertyService';
import { Property, PropertyType } from '@/types/property';
import { DataTable } from '@/components/ui/data-table';
import { Button } from '@/components/ui/button';
import { AlertCircle, Plus, LayoutGrid, Table as TableIcon } from 'lucide-react';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { columns } from './columns';
import { PropertyForm } from '@/components/property-form';
import { PropertiesGrid } from '@/components/properties/properties-grid';
import { Header } from "@/components/header";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";

export default function PropertiesPage() {
  const [properties, setProperties] = useState<Property[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showForm, setShowForm] = useState(false);
  const [selectedPropertyId, setSelectedPropertyId] = useState<number | undefined>();
  const [viewMode, setViewMode] = useState<'grid' | 'table'>('table');

  const fetchProperties = async () => {
    try {
      setIsLoading(true);
      setError(null);
      const data = await propertyService.getProperties();
      console.log('Fetched properties:', data);
      setProperties(Array.isArray(data) ? data : []);
    } catch (err: any) {
      console.error('Error fetching properties:', err);
      setError(err.message || 'Failed to load properties');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchProperties();

    // Event listeners para las acciones de la tabla
    const handleAddUnit = (e: CustomEvent) => {
      setSelectedPropertyId(e.detail);
      setShowForm(true);
    };

    const handleEditProperty = (e: CustomEvent) => {
      const property = e.detail;
      setSelectedPropertyId(property.id);
      setShowForm(true);
    };

    const handleDeleteProperty = async (e: CustomEvent) => {
      const property = e.detail;
      try {
        await propertyService.deleteProperty(property.id);
        await fetchProperties();
      } catch (err) {
        console.error('Error deleting property:', err);
      }
    };

    window.addEventListener('ADD_UNIT', handleAddUnit as EventListener);
    window.addEventListener('EDIT_PROPERTY', handleEditProperty as EventListener);
    window.addEventListener('DELETE_PROPERTY', handleDeleteProperty as EventListener);

    return () => {
      window.removeEventListener('ADD_UNIT', handleAddUnit as EventListener);
      window.removeEventListener('EDIT_PROPERTY', handleEditProperty as EventListener);
      window.removeEventListener('DELETE_PROPERTY', handleDeleteProperty as EventListener);
    };
  }, []);

  if (error) {
    return (
      <Alert variant="destructive">
        <AlertCircle className="h-4 w-4" />
        <AlertTitle>Error</AlertTitle>
        <AlertDescription>{error}</AlertDescription>
      </Alert>
    );
  }

  return (
    <div className="flex-1 space-y-4 p-8 pt-6">
      <Header
        title="Properties"
        description="Manage your rental properties"
      >
        <Button
          onClick={() => {
            setSelectedPropertyId(undefined);
            setShowForm(true);
          }}
          size="lg"
          variant="primary"
          className="group font-semibold"
        >
          <Plus className="h-5 w-5 transition-transform group-hover:rotate-90" />
          Add Property
        </Button>
      </Header>

      {viewMode === 'grid' ? (
        <div className="space-y-4">
          <div className="flex items-center justify-end gap-2">
            <span className="text-sm text-muted-foreground">Current view:</span>
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="outline" size="sm">
                  <LayoutGrid className="mr-2 h-4 w-4" />
                  Grid View
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end">
                <DropdownMenuItem onClick={() => setViewMode('grid')}>
                  <LayoutGrid className="mr-2 h-4 w-4" />
                  Grid View
                </DropdownMenuItem>
                <DropdownMenuItem onClick={() => setViewMode('table')}>
                  <TableIcon className="mr-2 h-4 w-4" />
                  Table View
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
          <PropertiesGrid
            properties={properties}
            onEdit={(property) => {
              setSelectedPropertyId(property.id);
              setShowForm(true);
            }}
            onDelete={async (property) => {
              try {
                await propertyService.deleteProperty(property.id);
                await fetchProperties();
              } catch (err) {
                console.error('Error deleting property:', err);
              }
            }}
          />
        </div>
      ) : (
        <div className="space-y-4">
          <div className="flex items-center justify-end gap-2">
            <span className="text-sm text-muted-foreground">Current view:</span>
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="outline" size="sm">
                  <TableIcon className="mr-2 h-4 w-4" />
                  Table View
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end">
                <DropdownMenuItem onClick={() => setViewMode('grid')}>
                  <LayoutGrid className="mr-2 h-4 w-4" />
                  Grid View
                </DropdownMenuItem>
                <DropdownMenuItem onClick={() => setViewMode('table')}>
                  <TableIcon className="mr-2 h-4 w-4" />
                  Table View
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
          <div className="rounded-md border bg-card">
            <DataTable
              columns={columns}
              data={properties}
              isLoading={isLoading}
              pageSize={10}
            />
          </div>
        </div>
      )}

      <PropertyForm
        open={showForm}
        onOpenChange={setShowForm}
        onSubmit={async (data) => {
          try {
            if (selectedPropertyId) {
              const newUnit = await propertyService.createProperty({
                ...data,
                property_type: PropertyType.UNIT,
                parent_id: selectedPropertyId,
              });
              setProperties([...properties, newUnit]);
            } else {
              const newProperty = await propertyService.createProperty({
                ...data,
                property_type: PropertyType.MAIN,
              });
              setProperties([...properties, newProperty]);
            }
            setShowForm(false);
            // Refrescar los datos después de crear la propiedad
            await fetchProperties();
          } catch (err: any) {
            console.error('Error adding property:', err);
          }
        }}
        parentId={selectedPropertyId}
      />
    </div>
  );
}
