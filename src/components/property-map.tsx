'use client';

import { Card } from "@/components/ui/card";
import { MapPin } from "lucide-react";
import { useEffect } from "react";

type Property = {
  id: number;
  name: string;
  lat: number;
  lng: number;
  type: string;
  status: 'occupied' | 'vacant' | 'maintenance';
};

declare global {
  interface Window {
    google: any;
    initMap: () => void;
  }
}

export default function PropertyMap() {
  const properties: Property[] = [
    {
      id: 1,
      name: "Apartamento 301",
      lat: 19.4326,
      lng: -99.1332,
      type: "Apartamento",
      status: 'occupied',
    },
    {
      id: 2,
      name: "Casa 123",
      lat: 19.4361,
      lng: -99.1367,
      type: "Casa",
      status: 'occupied',
    },
    {
      id: 3,
      name: "Local 45",
      lat: 19.4280,
      lng: -99.1355,
      type: "Comercial",
      status: 'maintenance',
    },
  ];

  useEffect(() => {
    // Cargar Google Maps script
    const loadGoogleMaps = () => {
      const script = document.createElement('script');
      script.src = `https://maps.googleapis.com/maps/api/js?key=YOUR_API_KEY&callback=initMap`;
      script.async = true;
      script.defer = true;
      document.head.appendChild(script);
    };

    // Inicializar el mapa
    window.initMap = () => {
      const map = new window.google.maps.Map(document.getElementById('map'), {
        center: { lat: 19.4326, lng: -99.1332 },
        zoom: 13,
        styles: [
          {
            featureType: "all",
            elementType: "labels.text.fill",
            stylers: [{ color: "#6c7079" }],
          },
          {
            featureType: "water",
            elementType: "geometry.fill",
            stylers: [{ color: "#e9eff3" }],
          },
        ],
      });

      // Agregar marcadores para cada propiedad
      properties.forEach((property) => {
        const marker = new window.google.maps.Marker({
          position: { lat: property.lat, lng: property.lng },
          map,
          title: property.name,
          icon: {
            path: window.google.maps.SymbolPath.CIRCLE,
            fillColor: property.status === 'occupied' ? '#22c55e' : 
                      property.status === 'vacant' ? '#f59e0b' : '#ef4444',
            fillOpacity: 1,
            strokeWeight: 0,
            scale: 8,
          },
        });

        // Agregar InfoWindow para cada marcador
        const infoWindow = new window.google.maps.InfoWindow({
          content: `
            <div class="p-2">
              <h3 class="font-medium">${property.name}</h3>
              <p class="text-sm text-muted-foreground">${property.type}</p>
              <p class="text-sm">${property.status}</p>
            </div>
          `,
        });

        marker.addListener('click', () => {
          infoWindow.open(map, marker);
        });
      });
    };

    loadGoogleMaps();

    return () => {
      // Limpiar el script cuando el componente se desmonte
      const script = document.querySelector('script[src*="maps.googleapis.com"]');
      if (script) {
        script.remove();
      }
    };
  }, []);

  return (
    <Card className="p-6">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-lg font-medium">Ubicación de Propiedades</h3>
        <MapPin className="h-5 w-5 text-muted-foreground" />
      </div>
      <div 
        id="map" 
        className="w-full h-[400px] rounded-lg"
        style={{ background: '#f1f5f9' }}
      >
        <div className="flex items-center justify-center h-full text-muted-foreground">
          Cargando mapa...
        </div>
      </div>
      <div className="flex items-center justify-center gap-6 mt-4">
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full bg-green-500" />
          <span className="text-sm">Ocupado</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full bg-amber-500" />
          <span className="text-sm">Vacante</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full bg-red-500" />
          <span className="text-sm">Mantenimiento</span>
        </div>
      </div>
    </Card>
  );
}
