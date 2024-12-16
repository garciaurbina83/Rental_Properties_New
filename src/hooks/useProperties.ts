import { useState, useEffect, useCallback, useRef } from 'react';
import { useInfiniteQuery, useQueryClient } from '@tanstack/react-query';
import { useAuth } from '@clerk/nextjs';
import { Property } from '@/schemas/property';
import { propertyService } from '@/services/propertyService';
import debounce from 'lodash/debounce';

const ITEMS_PER_PAGE = 12;
const CACHE_TIME = 1000 * 60 * 5; // 5 minutos

export interface PropertyFilters {
  search?: string;
  type?: string;
  status?: string;
  minPrice?: number;
  maxPrice?: number;
  minBedrooms?: number;
  minBathrooms?: number;
}

export function useProperties(initialFilters: PropertyFilters = {}) {
  const { getToken } = useAuth();
  const queryClient = useQueryClient();
  const [filters, setFilters] = useState<PropertyFilters>(initialFilters);
  const observerRef = useRef<IntersectionObserver | null>(null);
  const loadMoreRef = useRef<HTMLDivElement | null>(null);

  // Función para obtener propiedades con filtros
  const fetchProperties = async ({ pageParam = 0 }) => {
    const token = await getToken({ template: "fastapi" });
    if (!token) throw new Error('No authentication token available');

    // Generar una clave única para el caché basada en los filtros actuales
    const cacheKey = `properties-${JSON.stringify(filters)}-${pageParam}`;
  
    // Intentar obtener del caché primero
    const cachedData = queryClient.getQueryData(cacheKey);
    if (cachedData) {
      return cachedData;
    }

    const properties = await propertyService.getProperties(token, pageParam * ITEMS_PER_PAGE, ITEMS_PER_PAGE, filters);
  
    // Almacenar en caché
    queryClient.setQueryData(cacheKey, properties);
  
    return properties;
  };

  // Configurar react-query con paginación infinita
  const {
    data,
    fetchNextPage,
    hasNextPage,
    isFetchingNextPage,
    isLoading,
    isError,
    error,
    refetch
  } = useInfiniteQuery(
    ['properties', filters],
    fetchProperties,
    {
      getNextPageParam: (lastPage, pages) => {
        return lastPage.length === ITEMS_PER_PAGE ? pages.length : undefined;
      },
      staleTime: CACHE_TIME,
      cacheTime: CACHE_TIME,
    }
  );

  // Prefetch de la siguiente página
  const prefetchNextPage = useCallback(async (pageParam: number) => {
    const token = await getToken({ template: "fastapi" });
    if (!token) return;

    const nextPageData = await propertyService.getProperties(
      token,
      pageParam * ITEMS_PER_PAGE,
      ITEMS_PER_PAGE,
      filters
    );

    queryClient.setQueryData(
      ['properties', { filters, pageParam }],
      nextPageData
    );
  }, [filters, getToken, queryClient]);

  // Configurar intersection observer para paginación infinita
  useEffect(() => {
    if (!loadMoreRef.current) return;

    observerRef.current = new IntersectionObserver(
      (entries) => {
        if (entries[0].isIntersecting && hasNextPage && !isFetchingNextPage) {
          fetchNextPage();
        }
      },
      { threshold: 0.1 }
    );

    observerRef.current.observe(loadMoreRef.current);

    return () => {
      if (observerRef.current) {
        observerRef.current.disconnect();
      }
    };
  }, [loadMoreRef.current, hasNextPage, isFetchingNextPage]);

  // Debounce para búsqueda en tiempo real
  const debouncedSetFilters = useCallback(
    debounce((newFilters: Partial<PropertyFilters>) => {
      setFilters(prev => ({ ...prev, ...newFilters }));
    }, 300),
    []
  );

  // Función para invalidar el caché
  const invalidateCache = useCallback(() => {
    queryClient.invalidateQueries(['properties']);
  }, [queryClient]);

  // Función para actualizar una propiedad en el caché
  const updatePropertyInCache = useCallback((updatedProperty: Property) => {
    queryClient.setQueryData(['properties', filters], (oldData: any) => {
      if (!oldData) return oldData;
      
      return {
        ...oldData,
        pages: oldData.pages.map((page: Property[]) =>
          page.map(property =>
            property.id === updatedProperty.id ? updatedProperty : property
          )
        ),
      };
    });
  }, [queryClient, filters]);

  return {
    properties: data?.pages.flat() || [],
    isLoading,
    isError,
    error,
    hasNextPage,
    isFetchingNextPage,
    loadMoreRef,
    filters,
    setFilters: debouncedSetFilters,
    refetch,
    invalidateCache,
    updatePropertyInCache,
    prefetchNextPage,
  };
}
