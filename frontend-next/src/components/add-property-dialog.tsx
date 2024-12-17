'use client';

import { useState } from "react";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
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
import { PropertyCreate, PropertyType } from "@/types/property";
import { useToast } from "@/components/ui/use-toast";

interface AddPropertyDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSubmit: (property: PropertyCreate) => void;
}

export default function AddPropertyDialog({
  open,
  onOpenChange,
  onSubmit,
}: AddPropertyDialogProps) {
  const { toast } = useToast();
  const [formData, setFormData] = useState<PropertyCreate>({
    address: "",
    city: "",
    state: "",
    zip_code: "",
    country: "México",
    property_type: "principal",
    status: "available",
    is_active: true
  });

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    setFormData(prev => ({ ...prev, [e.target.name]: e.target.value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    // Validar campos requeridos
    if (!formData.address) {
      toast({
        title: "Error",
        description: "La dirección es obligatoria",
        variant: "destructive",
      });
      return;
    }

    try {
      onSubmit(formData);
      setFormData({
        address: "",
        city: "",
        state: "",
        zip_code: "",
        country: "México",
        property_type: "principal",
        status: "available",
        is_active: true
      });
      onOpenChange(false);
    } catch (error) {
      console.error('Error submitting property:', error);
      toast({
        title: "Error",
        description: "No se pudo crear la propiedad. Por favor, intente nuevamente.",
        variant: "destructive",
      });
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Agregar Nueva Propiedad</DialogTitle>
          <DialogDescription>
            Complete los detalles de la propiedad. Solo la dirección es obligatoria.
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="grid gap-4 py-4">
            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="address" className="text-right">
                Dirección *
              </Label>
              <Input
                id="address"
                name="address"
                value={formData.address}
                onChange={handleInputChange}
                className="col-span-3"
                required
              />
            </div>

            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="city" className="text-right">
                Ciudad
              </Label>
              <Input
                id="city"
                name="city"
                value={formData.city}
                onChange={handleInputChange}
                className="col-span-3"
              />
            </div>

            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="state" className="text-right">
                Estado
              </Label>
              <Input
                id="state"
                name="state"
                value={formData.state}
                onChange={handleInputChange}
                className="col-span-3"
              />
            </div>

            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="zip_code" className="text-right">
                Código Postal
              </Label>
              <Input
                id="zip_code"
                name="zip_code"
                value={formData.zip_code}
                onChange={handleInputChange}
                className="col-span-3"
              />
            </div>

            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="country" className="text-right">
                País
              </Label>
              <Input
                id="country"
                name="country"
                value={formData.country}
                onChange={handleInputChange}
                className="col-span-3"
                placeholder="México"
              />
            </div>

            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="property_type" className="text-right">
                Tipo
              </Label>
              <Select
                name="property_type"
                value={formData.property_type}
                onValueChange={(value) => handleInputChange({ target: { name: 'property_type', value } })}
              >
                <SelectTrigger className="col-span-3">
                  <SelectValue placeholder="Seleccione el tipo" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="principal">Principal</SelectItem>
                  <SelectItem value="unit">Unidad</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="status" className="text-right">
                Estado
              </Label>
              <Select
                name="status"
                value={formData.status}
                onValueChange={(value) => handleInputChange({ target: { name: 'status', value } })}
              >
                <SelectTrigger className="col-span-3">
                  <SelectValue placeholder="Seleccione el estado" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="available">Disponible</SelectItem>
                  <SelectItem value="rented">Rentada</SelectItem>
                  <SelectItem value="maintenance">Mantenimiento</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          <DialogFooter>
            <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>
              Cancelar
            </Button>
            <Button type="submit">Guardar Propiedad</Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
