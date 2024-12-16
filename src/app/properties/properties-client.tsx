'use client';

import { useState, useEffect } from 'react';
import { useAuth, useSession } from '@clerk/nextjs';
import { useToast } from '@/components/ui/use-toast';
import { Button } from '@/components/ui/button';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Property, PropertyCreate } from '@/types/property';
import { propertyService } from '@/services/propertyService';
import { LoadingSpinner } from '@/components/ui/loading-spinner';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { AlertCircle, AlertTriangle } from 'lucide-react';
import AddPropertyDialog from "@/components/add-property-dialog";

export default function PropertiesClient() {
  const [isAddDialogOpen, setIsAddDialogOpen] = useState(false);
  const [properties, setProperties] = useState<Property[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const { toast } = useToast();
  const { getToken } = useAuth();
  const { session } = useSession();

  const fetchProperties = async () => {
    try {
      setIsLoading(true);
      setError(null);

      if (!session) {
        throw new Error('No hay una sesión activa. Por favor, inicie sesión.');
      }

      const token = await getToken({ template: "fastapi" });
      
      // Log detallado del token y la sesión
      console.log('Session:', {
        id: session.id,
        status: session.status,
        expireAt: session.expireAt
      });
      
      if (!token) {
        throw new Error('No se pudo obtener el token de autenticación. Por favor, inicie sesión nuevamente.');
      }

      const data = await propertyService.getProperties(token);
      setProperties(data);
    } catch (error) {
      console.error('Error al cargar las propiedades:', error);
      
      let errorMessage = 'Ocurrió un error al cargar las propiedades.';
      
      if (error instanceof Error) {
        if (error.message.includes('401')) {
          errorMessage = 'Su sesión ha expirado. Por favor, inicie sesión nuevamente.';
        } else if (error.message.includes('403')) {
          errorMessage = 'No tiene permisos para ver las propiedades.';
        } else if (error.message.includes('network')) {
          errorMessage = 'Error de conexión. Por favor, verifique su conexión a internet.';
        } else {
          errorMessage = error.message;
        }
      }
      
      setError(errorMessage);
      toast({
        title: "Error",
        description: errorMessage,
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (session) {
      fetchProperties();
    }
  }, [session]);

  const handlePropertySubmit = async (property: PropertyCreate) => {
    try {
      setError(null);

      if (!session) {
        throw new Error('No hay una sesión activa. Por favor, inicie sesión.');
      }

      const token = await getToken({ template: "fastapi" });
      if (!token) {
        throw new Error('No se pudo obtener el token de autenticación. Por favor, inicie sesión nuevamente.');
      }

      await propertyService.createProperty(property, token);
      toast({
        title: "Éxito",
        description: "La propiedad se ha agregado correctamente.",
      });
      setIsAddDialogOpen(false);
      await fetchProperties();
    } catch (error) {
      console.error('Error al crear la propiedad:', error);
      
      let errorMessage = 'No se pudo crear la propiedad.';
      
      if (error instanceof Error) {
        if (error.message.includes('401')) {
          errorMessage = 'Su sesión ha expirado. Por favor, inicie sesión nuevamente.';
        } else if (error.message.includes('403')) {
          errorMessage = 'No tiene permisos para crear propiedades.';
        } else if (error.message.includes('422')) {
          errorMessage = 'Los datos de la propiedad son inválidos. Por favor, verifique la información.';
        } else if (error.message.includes('network')) {
          errorMessage = 'Error de conexión. Por favor, verifique su conexión a internet.';
        } else {
          errorMessage = error.message;
        }
      }
      
      setError(errorMessage);
      toast({
        title: "Error",
        description: errorMessage,
        variant: "destructive",
      });
    }
  };

  if (!session) {
    return (
      <div className="container mx-auto py-10">
        <Alert variant="warning">
          <AlertTriangle className="h-4 w-4" />
          <AlertTitle>No has iniciado sesión</AlertTitle>
          <AlertDescription>
            Por favor, inicia sesión para ver y administrar tus propiedades.
          </AlertDescription>
        </Alert>
      </div>
    );
  }

  return (
    <div className="container mx-auto py-10">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold">Propiedades</h1>
        <Button 
          onClick={() => setIsAddDialogOpen(true)}
          disabled={isLoading}
        >
          Agregar Propiedad
        </Button>
      </div>

      {error && (
        <Alert variant="destructive" className="mb-6">
          <AlertCircle className="h-4 w-4" />
          <AlertTitle>Error</AlertTitle>
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      <div className="rounded-md border">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Nombre</TableHead>
              <TableHead>Dirección</TableHead>
              <TableHead>Tamaño</TableHead>
              <TableHead>Habitaciones</TableHead>
              <TableHead>Renta Mensual</TableHead>
              <TableHead>Estado</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {isLoading ? (
              <TableRow>
                <TableCell colSpan={6} className="h-24 text-center">
                  <LoadingSpinner />
                  <span className="ml-2">Cargando propiedades...</span>
                </TableCell>
              </TableRow>
            ) : properties.length === 0 ? (
              <TableRow>
                <TableCell colSpan={6} className="h-24 text-center">
                  No hay propiedades registradas.
                </TableCell>
              </TableRow>
            ) : (
              properties.map((property) => (
                <TableRow key={property.id}>
                  <TableCell>{property.name}</TableCell>
                  <TableCell>{`${property.address}, ${property.city}, ${property.state}`}</TableCell>
                  <TableCell>{`${property.size} m²`}</TableCell>
                  <TableCell>{property.bedrooms}</TableCell>
                  <TableCell>
                    {new Intl.NumberFormat('es-MX', {
                      style: 'currency',
                      currency: 'MXN'
                    }).format(property.monthly_rent)}
                  </TableCell>
                  <TableCell>{property.status}</TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </div>

      <AddPropertyDialog
        open={isAddDialogOpen}
        onOpenChange={setIsAddDialogOpen}
        onSubmit={handlePropertySubmit}
      />
    </div>
  );
}
