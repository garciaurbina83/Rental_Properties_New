import { useState, useEffect } from 'react';
import { propertyService } from '@/services/propertyService';

// Cache para almacenar las propiedades ya cargadas
const propertyCache = new Map();

export function useProperty(propertyId: number) {
  const [property, setProperty] = useState<any>(propertyCache.get(propertyId) || null);
  const [isLoading, setIsLoading] = useState(!propertyCache.has(propertyId));
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadProperty = async () => {
      // Si la propiedad ya está en caché, no la cargamos de nuevo
      if (propertyCache.has(propertyId)) {
        setProperty(propertyCache.get(propertyId));
        setIsLoading(false);
        return;
      }

      try {
        setIsLoading(true);
        setError(null);
        const data = await propertyService.getProperty(propertyId);
        propertyCache.set(propertyId, data);
        setProperty(data);
      } catch (err) {
        console.error('Error loading property:', err);
        setError('Failed to load property');
      } finally {
        setIsLoading(false);
      }
    };

    loadProperty();
  }, [propertyId]);

  return { property, isLoading, error };
}
