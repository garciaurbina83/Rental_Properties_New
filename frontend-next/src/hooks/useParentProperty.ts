import { useState, useEffect } from 'react';
import { propertyService } from '@/services/propertyService';

// Cache para almacenar las propiedades principales ya cargadas
const parentPropertyCache = new Map();

export function useParentProperty(parentPropertyId: number | null, propertyType: string) {
  const [parentProperty, setParentProperty] = useState<any>(parentPropertyCache.get(parentPropertyId) || null);
  const [isLoading, setIsLoading] = useState(!parentPropertyCache.has(parentPropertyId));
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadParentProperty = async () => {
      console.log('Loading parent property:', { parentPropertyId, propertyType });
      
      // Si no es una unidad o no tiene parent_property_id, no hacemos nada
      if (propertyType !== 'UNIT' || !parentPropertyId) {
        console.log('Skipping load:', { propertyType, parentPropertyId });
        setIsLoading(false);
        return;
      }

      // Si la propiedad ya está en caché, la usamos
      if (parentPropertyCache.has(parentPropertyId)) {
        console.log('Using cached property:', parentPropertyCache.get(parentPropertyId));
        setParentProperty(parentPropertyCache.get(parentPropertyId));
        setIsLoading(false);
        return;
      }

      try {
        setIsLoading(true);
        setError(null);
        console.log('Fetching property:', parentPropertyId);
        const data = await propertyService.getProperty(parentPropertyId);
        console.log('Fetched property:', data);
        parentPropertyCache.set(parentPropertyId, data);
        setParentProperty(data);
      } catch (err) {
        console.error('Error loading parent property:', err);
        setError('Failed to load parent property');
      } finally {
        setIsLoading(false);
      }
    };

    loadParentProperty();
  }, [parentPropertyId, propertyType]);

  return { parentProperty, isLoading, error };
}
