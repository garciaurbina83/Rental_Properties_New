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
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import { Property, PropertyStatus, PropertyType } from "@/types/property";
import { Plus, Upload } from "lucide-react";

interface NewPropertyFormProps {
  onSubmit: (property: Partial<Property>) => void;
}

export default function NewPropertyForm({ onSubmit }: NewPropertyFormProps) {
  const [formData, setFormData] = useState<Partial<Property>>({
    type: 'house',
    status: 'available',
    features: {
      bedrooms: 0,
      bathrooms: 0,
      squareMeters: 0,
      parking: 0,
    },
    address: {
      street: '',
      city: '',
      state: '',
      zipCode: '',
    },
    images: [],
    amenities: [],
  });

  const handleInputChange = (key: string, value: any) => {
    setFormData((prev) => ({
      ...prev,
      [key]: value,
    }));
  };

  const handleAddressChange = (key: string, value: string) => {
    setFormData((prev) => ({
      ...prev,
      address: {
        ...prev.address!,
        [key]: value,
      },
    }));
  };

  const handleFeaturesChange = (key: string, value: number) => {
    setFormData((prev) => ({
      ...prev,
      features: {
        ...prev.features!,
        [key]: value,
      },
    }));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit(formData);
  };

  return (
    <Dialog>
      <DialogTrigger asChild>
        <Button className="gap-2">
          <Plus className="h-4 w-4" />
          Nueva Propiedad
        </Button>
      </DialogTrigger>
      <DialogContent className="max-w-2xl">
        <DialogHeader>
          <DialogTitle>Agregar Nueva Propiedad</DialogTitle>
          <DialogDescription>
            Ingresa los detalles de la nueva propiedad. Los campos marcados con * son obligatorios.
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Información Básica */}
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="name">Nombre *</Label>
              <Input
                id="name"
                required
                value={formData.name || ''}
                onChange={(e) => handleInputChange('name', e.target.value)}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="price">Precio *</Label>
              <Input
                id="price"
                type="number"
                required
                value={formData.price || ''}
                onChange={(e) => handleInputChange('price', Number(e.target.value))}
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label>Tipo de Propiedad *</Label>
              <Select
                value={formData.type}
                onValueChange={(value) => handleInputChange('type', value)}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Selecciona un tipo" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="house">Casa</SelectItem>
                  <SelectItem value="apartment">Apartamento</SelectItem>
                  <SelectItem value="commercial">Comercial</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label>Estado *</Label>
              <Select
                value={formData.status}
                onValueChange={(value) => handleInputChange('status', value)}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Selecciona un estado" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="available">Disponible</SelectItem>
                  <SelectItem value="occupied">Ocupado</SelectItem>
                  <SelectItem value="maintenance">Mantenimiento</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          {/* Características */}
          <div className="grid grid-cols-4 gap-4">
            <div className="space-y-2">
              <Label>Habitaciones</Label>
              <Input
                type="number"
                min="0"
                value={formData.features?.bedrooms}
                onChange={(e) => handleFeaturesChange('bedrooms', Number(e.target.value))}
              />
            </div>
            <div className="space-y-2">
              <Label>Baños</Label>
              <Input
                type="number"
                min="0"
                value={formData.features?.bathrooms}
                onChange={(e) => handleFeaturesChange('bathrooms', Number(e.target.value))}
              />
            </div>
            <div className="space-y-2">
              <Label>Metros Cuadrados</Label>
              <Input
                type="number"
                min="0"
                value={formData.features?.squareMeters}
                onChange={(e) => handleFeaturesChange('squareMeters', Number(e.target.value))}
              />
            </div>
            <div className="space-y-2">
              <Label>Estacionamientos</Label>
              <Input
                type="number"
                min="0"
                value={formData.features?.parking}
                onChange={(e) => handleFeaturesChange('parking', Number(e.target.value))}
              />
            </div>
          </div>

          {/* Dirección */}
          <div className="space-y-4">
            <Label>Dirección</Label>
            <div className="grid grid-cols-2 gap-4">
              <Input
                placeholder="Calle *"
                required
                value={formData.address?.street}
                onChange={(e) => handleAddressChange('street', e.target.value)}
              />
              <Input
                placeholder="Ciudad *"
                required
                value={formData.address?.city}
                onChange={(e) => handleAddressChange('city', e.target.value)}
              />
              <Input
                placeholder="Estado *"
                required
                value={formData.address?.state}
                onChange={(e) => handleAddressChange('state', e.target.value)}
              />
              <Input
                placeholder="Código Postal *"
                required
                value={formData.address?.zipCode}
                onChange={(e) => handleAddressChange('zipCode', e.target.value)}
              />
            </div>
          </div>

          {/* Descripción */}
          <div className="space-y-2">
            <Label>Descripción</Label>
            <Textarea
              value={formData.description || ''}
              onChange={(e) => handleInputChange('description', e.target.value)}
              placeholder="Describe la propiedad..."
            />
          </div>

          {/* Imágenes */}
          <div className="space-y-2">
            <Label>Imágenes</Label>
            <div className="flex items-center justify-center w-full">
              <label className="flex flex-col items-center justify-center w-full h-32 border-2 border-dashed rounded-lg cursor-pointer hover:bg-accent/5">
                <div className="flex flex-col items-center justify-center pt-5 pb-6">
                  <Upload className="h-8 w-8 text-muted-foreground mb-2" />
                  <p className="text-sm text-muted-foreground">
                    Arrastra y suelta imágenes aquí o haz clic para seleccionar
                  </p>
                </div>
                <input type="file" className="hidden" multiple accept="image/*" />
              </label>
            </div>
          </div>

          <div className="flex justify-end gap-2">
            <DialogTrigger asChild>
              <Button variant="outline">Cancelar</Button>
            </DialogTrigger>
            <Button type="submit">Guardar Propiedad</Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
}
