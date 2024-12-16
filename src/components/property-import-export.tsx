'use client';

import { useState } from "react";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import {
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
} from "@/components/ui/tabs";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Property } from "@/types/property";
import { Download, Upload, FileSpreadsheet, AlertCircle } from "lucide-react";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";

interface PropertyImportExportProps {
  properties: Property[];
  onImport: (properties: Property[]) => void;
}

export default function PropertyImportExport({
  properties,
  onImport,
}: PropertyImportExportProps) {
  const [importError, setImportError] = useState<string>("");

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    try {
      // Verificar tipo de archivo
      if (!file.name.endsWith('.csv') && !file.name.endsWith('.xlsx')) {
        throw new Error('Por favor, sube un archivo CSV o Excel (.xlsx)');
      }

      // Aquí iría la lógica para procesar el archivo
      // Por ahora, solo simularemos la lectura
      const reader = new FileReader();
      reader.onload = async (e) => {
        try {
          // Aquí procesaríamos el contenido del archivo
          // Por ahora, solo mostraremos un mensaje de éxito
          console.log('Archivo cargado:', file.name);
          setImportError("");
        } catch (error) {
          setImportError('Error al procesar el archivo. Verifica el formato.');
        }
      };
      reader.readAsText(file);
    } catch (error) {
      setImportError(error instanceof Error ? error.message : 'Error al cargar el archivo');
    }
  };

  const handleExport = (format: 'csv' | 'excel') => {
    // Convertir propiedades a formato CSV
    const headers = [
      'ID',
      'Nombre',
      'Tipo',
      'Estado',
      'Precio',
      'Descripción',
      'Habitaciones',
      'Baños',
      'Metros Cuadrados',
      'Estacionamientos',
      'Dirección',
      'Ciudad',
      'Estado',
      'Código Postal',
      'Amenidades',
    ].join(',');

    const rows = properties.map(property => [
      property.id,
      property.name,
      property.type,
      property.status,
      property.price,
      `"${property.description}"`,
      property.features.bedrooms,
      property.features.bathrooms,
      property.features.squareMeters,
      property.features.parking,
      `"${property.address.street}"`,
      property.address.city,
      property.address.state,
      property.address.zipCode,
      `"${property.amenities.join('; ')}"`,
    ].join(','));

    const csv = [headers, ...rows].join('\n');
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    
    link.setAttribute('href', url);
    link.setAttribute('download', `propiedades_${new Date().toISOString().split('T')[0]}.csv`);
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <Dialog>
      <DialogTrigger asChild>
        <Button variant="outline" className="gap-2">
          <FileSpreadsheet className="h-4 w-4" />
          Importar/Exportar
        </Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>Importar/Exportar Propiedades</DialogTitle>
          <DialogDescription>
            Importa propiedades desde un archivo CSV o Excel, o exporta la lista actual.
          </DialogDescription>
        </DialogHeader>

        <Tabs defaultValue="import" className="w-full">
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger value="import">Importar</TabsTrigger>
            <TabsTrigger value="export">Exportar</TabsTrigger>
          </TabsList>

          <TabsContent value="import" className="space-y-4">
            <div className="space-y-4">
              <Label htmlFor="file">Archivo CSV o Excel (.xlsx)</Label>
              <Input
                id="file"
                type="file"
                accept=".csv,.xlsx"
                onChange={handleFileUpload}
              />
              {importError && (
                <Alert variant="destructive">
                  <AlertCircle className="h-4 w-4" />
                  <AlertTitle>Error</AlertTitle>
                  <AlertDescription>{importError}</AlertDescription>
                </Alert>
              )}
              <div className="text-sm text-muted-foreground">
                <p>El archivo debe contener las siguientes columnas:</p>
                <ul className="list-disc list-inside mt-2">
                  <li>Nombre</li>
                  <li>Tipo (house, apartment, commercial)</li>
                  <li>Estado (available, occupied, maintenance)</li>
                  <li>Precio</li>
                  <li>Características (habitaciones, baños, etc.)</li>
                  <li>Dirección</li>
                </ul>
              </div>
            </div>
          </TabsContent>

          <TabsContent value="export" className="space-y-4">
            <div className="space-y-4">
              <div className="flex flex-col gap-4">
                <Button
                  variant="outline"
                  className="w-full gap-2"
                  onClick={() => handleExport('csv')}
                >
                  <Download className="h-4 w-4" />
                  Exportar como CSV
                </Button>
                <Button
                  variant="outline"
                  className="w-full gap-2"
                  onClick={() => handleExport('excel')}
                >
                  <Download className="h-4 w-4" />
                  Exportar como Excel
                </Button>
              </div>
              <div className="text-sm text-muted-foreground">
                El archivo exportado incluirá todas las propiedades con sus detalles.
              </div>
            </div>
          </TabsContent>
        </Tabs>
      </DialogContent>
    </Dialog>
  );
}
