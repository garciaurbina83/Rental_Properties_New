'use client';

import { Property } from "@/types/property";
import { Contract } from "@/types/contract";
import { Payment } from "@/types/payment";
import { MaintenanceRequest } from "@/types/maintenance";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import {
  Bed,
  Bath,
  Car,
  Maximize,
  MapPin,
  Calendar,
  FileText,
  Tool,
  Users,
  X,
  Plus,
  Eye,
} from "lucide-react";
import Image from "next/image";
import { cn } from "@/lib/utils";
import { Table, TableHeader, TableRow, TableHead, TableBody, TableCell } from "@/components/ui/table";

interface PropertyDetailProps {
  property: Property;
  onClose: () => void;
  contracts?: Contract[];
  payments?: Payment[];
  maintenanceRequests?: MaintenanceRequest[];
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

export default function PropertyDetail({
  property,
  onClose,
  contracts,
  payments,
  maintenanceRequests,
}: PropertyDetailProps) {
  return (
    <Dialog open={true} onOpenChange={() => onClose()}>
      <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <div className="flex items-start justify-between">
            <div>
              <DialogTitle className="text-2xl">{property.name}</DialogTitle>
              <DialogDescription className="flex items-center gap-2 mt-2">
                <MapPin className="h-4 w-4 text-muted-foreground" />
                {property.address.street}, {property.address.city}, {property.address.state}
              </DialogDescription>
            </div>
            <Badge className={cn(statusColors[property.status])}>
              {statusText[property.status]}
            </Badge>
          </div>
        </DialogHeader>

        {/* Contenido Principal */}
        <div className="space-y-6">
          {/* Galería de Imágenes */}
          <div className="relative aspect-video w-full overflow-hidden rounded-lg">
            <Image
              src={property.images[0] || "/mock/properties/default-property.jpg"}
              alt={property.name}
              fill
              className="object-cover"
            />
          </div>

          {/* Características Principales */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <Card>
              <CardContent className="p-4 flex items-center gap-2">
                <Bed className="h-4 w-4 text-muted-foreground" />
                <div>
                  <p className="text-sm text-muted-foreground">Habitaciones</p>
                  <p className="font-medium">{property.features.bedrooms}</p>
                </div>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-4 flex items-center gap-2">
                <Bath className="h-4 w-4 text-muted-foreground" />
                <div>
                  <p className="text-sm text-muted-foreground">Baños</p>
                  <p className="font-medium">{property.features.bathrooms}</p>
                </div>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-4 flex items-center gap-2">
                <Car className="h-4 w-4 text-muted-foreground" />
                <div>
                  <p className="text-sm text-muted-foreground">Estacionamientos</p>
                  <p className="font-medium">{property.features.parking}</p>
                </div>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-4 flex items-center gap-2">
                <Maximize className="h-4 w-4 text-muted-foreground" />
                <div>
                  <p className="text-sm text-muted-foreground">Área</p>
                  <p className="font-medium">{property.features.squareMeters}m²</p>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Precio */}
          <Card>
            <CardContent className="p-4">
              <p className="text-sm text-muted-foreground">Precio</p>
              <p className="text-2xl font-bold">${property.price.toLocaleString()}</p>
            </CardContent>
          </Card>

          {/* Tabs de Información */}
          <Tabs defaultValue="info" className="w-full">
            <TabsList className="grid w-full grid-cols-5">
              <TabsTrigger value="info">Información</TabsTrigger>
              <TabsTrigger value="documents">Documentos</TabsTrigger>
              <TabsTrigger value="contracts">Contratos</TabsTrigger>
              <TabsTrigger value="payments">Pagos</TabsTrigger>
              <TabsTrigger value="maintenance">Mantenimiento</TabsTrigger>
            </TabsList>

            <TabsContent value="info">
              <div className="space-y-4">
                <h3 className="text-lg font-semibold">Descripción</h3>
                <p className="text-muted-foreground">{property.description}</p>

                <h3 className="text-lg font-semibold">Amenidades</h3>
                <div className="flex flex-wrap gap-2">
                  {property.amenities.map((amenity) => (
                    <Badge key={amenity} variant="secondary">
                      {amenity}
                    </Badge>
                  ))}
                </div>
              </div>
            </TabsContent>

            <TabsContent value="documents">
              <div className="p-4 text-center text-muted-foreground">
                <FileText className="h-8 w-8 mx-auto mb-2" />
                <p>No hay documentos disponibles</p>
              </div>
            </TabsContent>

            <TabsContent value="contracts">
              <div className="space-y-4">
                <div className="flex justify-between items-center">
                  <h3 className="text-lg font-semibold">Contratos</h3>
                  <Button variant="outline" size="sm">
                    <Plus className="h-4 w-4 mr-2" />
                    Nuevo Contrato
                  </Button>
                </div>
                <div className="rounded-md border">
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Inquilino</TableHead>
                        <TableHead>Inicio</TableHead>
                        <TableHead>Fin</TableHead>
                        <TableHead>Renta Mensual</TableHead>
                        <TableHead>Estado</TableHead>
                        <TableHead>Acciones</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {contracts?.map((contract) => (
                        <TableRow key={contract.id}>
                          <TableCell>{contract.tenantId}</TableCell>
                          <TableCell>{new Date(contract.startDate).toLocaleDateString()}</TableCell>
                          <TableCell>{new Date(contract.endDate).toLocaleDateString()}</TableCell>
                          <TableCell>${contract.monthlyRent.toLocaleString()}</TableCell>
                          <TableCell>
                            <Badge variant={
                              contract.status === 'active' ? 'success' :
                              contract.status === 'pending' ? 'warning' :
                              'secondary'
                            }>
                              {contract.status}
                            </Badge>
                          </TableCell>
                          <TableCell>
                            <Button variant="ghost" size="sm">
                              <Eye className="h-4 w-4" />
                            </Button>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </div>
              </div>
            </TabsContent>

            <TabsContent value="payments">
              <div className="space-y-4">
                <div className="flex justify-between items-center">
                  <h3 className="text-lg font-semibold">Pagos</h3>
                  <Button variant="outline" size="sm">
                    <Plus className="h-4 w-4 mr-2" />
                    Registrar Pago
                  </Button>
                </div>
                <div className="rounded-md border">
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Fecha</TableHead>
                        <TableHead>Tipo</TableHead>
                        <TableHead>Monto</TableHead>
                        <TableHead>Estado</TableHead>
                        <TableHead>Método</TableHead>
                        <TableHead>Acciones</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {payments?.map((payment) => (
                        <TableRow key={payment.id}>
                          <TableCell>{new Date(payment.dueDate).toLocaleDateString()}</TableCell>
                          <TableCell>{payment.type}</TableCell>
                          <TableCell>${payment.amount.toLocaleString()}</TableCell>
                          <TableCell>
                            <Badge variant={
                              payment.status === 'paid' ? 'success' :
                              payment.status === 'pending' ? 'warning' :
                              payment.status === 'overdue' ? 'destructive' :
                              'secondary'
                            }>
                              {payment.status}
                            </Badge>
                          </TableCell>
                          <TableCell>{payment.method}</TableCell>
                          <TableCell>
                            <Button variant="ghost" size="sm">
                              <Eye className="h-4 w-4" />
                            </Button>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </div>
              </div>
            </TabsContent>

            <TabsContent value="maintenance">
              <div className="space-y-4">
                <div className="flex justify-between items-center">
                  <h3 className="text-lg font-semibold">Solicitudes de Mantenimiento</h3>
                  <Button variant="outline" size="sm">
                    <Plus className="h-4 w-4 mr-2" />
                    Nueva Solicitud
                  </Button>
                </div>
                <div className="rounded-md border">
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Fecha</TableHead>
                        <TableHead>Título</TableHead>
                        <TableHead>Categoría</TableHead>
                        <TableHead>Prioridad</TableHead>
                        <TableHead>Estado</TableHead>
                        <TableHead>Acciones</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {maintenanceRequests?.map((request) => (
                        <TableRow key={request.id}>
                          <TableCell>{new Date(request.createdAt).toLocaleDateString()}</TableCell>
                          <TableCell>{request.title}</TableCell>
                          <TableCell>{request.category}</TableCell>
                          <TableCell>
                            <Badge variant={
                              request.priority === 'urgent' ? 'destructive' :
                              request.priority === 'high' ? 'warning' :
                              request.priority === 'medium' ? 'secondary' :
                              'default'
                            }>
                              {request.priority}
                            </Badge>
                          </TableCell>
                          <TableCell>
                            <Badge variant={
                              request.status === 'completed' ? 'success' :
                              request.status === 'in_progress' ? 'warning' :
                              request.status === 'pending' ? 'secondary' :
                              'default'
                            }>
                              {request.status}
                            </Badge>
                          </TableCell>
                          <TableCell>
                            <Button variant="ghost" size="sm">
                              <Eye className="h-4 w-4" />
                            </Button>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </div>
              </div>
            </TabsContent>
          </Tabs>
        </div>

        {/* Acciones */}
        <div className="flex justify-end gap-2 mt-6">
          <Button variant="outline" onClick={onClose}>
            Cerrar
          </Button>
          <Button>Editar Propiedad</Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}
