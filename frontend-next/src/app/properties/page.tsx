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
  const [selectedProperty, setSelectedProperty] = useState<Property | undefined>();
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

    const handleAddUnit = (e: CustomEvent) => {
      const property = e.detail;
      setSelectedProperty(property);
      setShowForm(true);
    };

    const handleEditProperty = (e: CustomEvent) => {
      const property = e.detail;
      setSelectedProperty(property);
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

  const handleCloseForm = () => {
    setSelectedProperty(undefined);
    setShowForm(false);
  };

  const handlePropertyAction = async (data: any) => {
    try {
      let newProperty;
      console.log('Property action data:', { data, selectedProperty });
      
      if (selectedProperty?.id) {
        // Modo edición
        console.log('Editing property:', selectedProperty.id);
        newProperty = await propertyService.updateProperty(selectedProperty.id, {
          ...data,
          property_type: selectedProperty.property_type,
        });
      } else if (data.property_type === PropertyType.UNIT) {
        // Modo agregar unidad
        console.log('Creating new unit with data:', data);
        newProperty = await propertyService.createProperty({
          ...data,
          property_type: PropertyType.UNIT,
        });
        console.log('Created new unit:', newProperty);
      } else {
        // Modo agregar propiedad principal
        console.log('Creating new principal property with data:', data);
        newProperty = await propertyService.createProperty({
          ...data,
          property_type: PropertyType.PRINCIPAL,
          parent_property_id: null,
          status: data.status || 'available',
          is_active: true,
        });
        console.log('Created new principal property:', newProperty);
      }
      
      // Refrescar los datos antes de cerrar el formulario
      await fetchProperties();
      handleCloseForm();
    } catch (err: any) {
      console.error('Error handling property action:', err);
      // No cerrar el formulario si hay un error
      throw err;
    }
  };

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
            setSelectedProperty(undefined);
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
              setSelectedProperty(property);
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
        onOpenChange={handleCloseForm}
        onSubmit={handlePropertyAction}
        parentId={selectedProperty?.id}
        propertyToEdit={selectedProperty}
      />
    </div>
  );
}
