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
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Property } from "@/types/property";
import { FileText, Download } from "lucide-react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

interface PropertyReportsProps {
  properties: Property[];
}

type ReportType = 'general' | 'occupancy' | 'financial';

interface ReportConfig {
  title: string;
  description: string;
  generate: (properties: Property[]) => any;
}

const reportTypes: Record<ReportType, ReportConfig> = {
  general: {
    title: "Reporte General",
    description: "Resumen general de todas las propiedades",
    generate: (properties) => ({
      totalProperties: properties.length,
      byType: properties.reduce((acc, p) => {
        acc[p.type] = (acc[p.type] || 0) + 1;
        return acc;
      }, {} as Record<string, number>),
      byStatus: properties.reduce((acc, p) => {
        acc[p.status] = (acc[p.status] || 0) + 1;
        return acc;
      }, {} as Record<string, number>),
      averagePrice: properties.reduce((sum, p) => sum + p.price, 0) / properties.length,
    }),
  },
  occupancy: {
    title: "Reporte de Ocupación",
    description: "Estado de ocupación de las propiedades",
    generate: (properties) => ({
      total: properties.length,
      occupied: properties.filter(p => p.status === 'occupied').length,
      available: properties.filter(p => p.status === 'available').length,
      maintenance: properties.filter(p => p.status === 'maintenance').length,
      occupancyRate: (properties.filter(p => p.status === 'occupied').length / properties.length) * 100,
    }),
  },
  financial: {
    title: "Reporte Financiero",
    description: "Resumen financiero de las propiedades",
    generate: (properties) => ({
      totalValue: properties.reduce((sum, p) => sum + p.price, 0),
      averageValue: properties.reduce((sum, p) => sum + p.price, 0) / properties.length,
      byType: properties.reduce((acc, p) => {
        acc[p.type] = (acc[p.type] || 0) + p.price;
        return acc;
      }, {} as Record<string, number>),
    }),
  },
};

export default function PropertyReports({ properties }: PropertyReportsProps) {
  const [selectedReport, setSelectedReport] = useState<ReportType>('general');
  const [reportData, setReportData] = useState<any>(null);

  const generateReport = () => {
    const report = reportTypes[selectedReport].generate(properties);
    setReportData(report);
  };

  const downloadReport = () => {
    if (!reportData) return;

    const jsonStr = JSON.stringify(reportData, null, 2);
    const blob = new Blob([jsonStr], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `reporte_${selectedReport}_${new Date().toISOString().split('T')[0]}.json`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <Dialog>
      <DialogTrigger asChild>
        <Button variant="outline" className="gap-2">
          <FileText className="h-4 w-4" />
          Reportes
        </Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-[600px]">
        <DialogHeader>
          <DialogTitle>Generar Reporte</DialogTitle>
          <DialogDescription>
            Selecciona el tipo de reporte que deseas generar.
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4">
          <Select
            value={selectedReport}
            onValueChange={(value) => setSelectedReport(value as ReportType)}
          >
            <SelectTrigger>
              <SelectValue placeholder="Selecciona un tipo de reporte" />
            </SelectTrigger>
            <SelectContent>
              {Object.entries(reportTypes).map(([key, config]) => (
                <SelectItem key={key} value={key}>
                  {config.title}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>

          <Card>
            <CardHeader>
              <CardTitle>{reportTypes[selectedReport].title}</CardTitle>
              <CardDescription>
                {reportTypes[selectedReport].description}
              </CardDescription>
            </CardHeader>
            <CardContent>
              {reportData && (
                <pre className="bg-muted p-4 rounded-lg overflow-auto max-h-[300px] text-sm">
                  {JSON.stringify(reportData, null, 2)}
                </pre>
              )}
            </CardContent>
          </Card>

          <div className="flex justify-end gap-2">
            <Button variant="outline" onClick={generateReport}>
              Generar Reporte
            </Button>
            {reportData && (
              <Button onClick={downloadReport} className="gap-2">
                <Download className="h-4 w-4" />
                Descargar
              </Button>
            )}
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}
