import { useState, useEffect } from 'react';
import { propertyService } from '@/services/propertyService';

// Cache para almacenar las propiedades ya cargadas
const propertyCache = new Map();

export function useProperty(propertyId: number) {
  const [property, setProperty] = useState<any>(propertyCache.get(propertyId) || null);
  const [parentProperty, setParentProperty] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(!propertyCache.has(propertyId));
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadProperty = async () => {
      // Si la propiedad ya está en caché, no la cargamos de nuevo
      if (propertyCache.has(propertyId)) {
        const cachedProperty = propertyCache.get(propertyId);
        setProperty(cachedProperty);
        
        // Si es una unidad, cargar la propiedad principal
        if (cachedProperty?.property_type === 'UNIT' && cachedProperty?.parent_property_id) {
          if (propertyCache.has(cachedProperty.parent_property_id)) {
            setParentProperty(propertyCache.get(cachedProperty.parent_property_id));
          } else {
            try {
              const parentData = await propertyService.getProperty(cachedProperty.parent_property_id);
              propertyCache.set(cachedProperty.parent_property_id, parentData);
              setParentProperty(parentData);
            } catch (err) {
              console.error('Error loading parent property:', err);
            }
          }
        }
        
        setIsLoading(false);
        return;
      }

      try {
        setIsLoading(true);
        setError(null);
        const data = await propertyService.getProperty(propertyId);
        propertyCache.set(propertyId, data);
        setProperty(data);

        // Si es una unidad, cargar la propiedad principal
        if (data?.property_type === 'UNIT' && data?.parent_property_id) {
          try {
            const parentData = await propertyService.getProperty(data.parent_property_id);
            propertyCache.set(data.parent_property_id, parentData);
            setParentProperty(parentData);
          } catch (err) {
            console.error('Error loading parent property:', err);
          }
        }
      } catch (err) {
        console.error('Error loading property:', err);
        setError('Failed to load property');
      } finally {
        setIsLoading(false);
      }
    };

    loadProperty();
  }, [propertyId]);

  return { property, parentProperty, isLoading, error };
}
