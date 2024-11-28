import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { propertyApi } from '../services/api';

export function useProperties() {
  const queryClient = useQueryClient();

  const propertiesQuery = useQuery({
    queryKey: ['properties'],
    queryFn: propertyApi.getProperties,
  });

  const createPropertyMutation = useMutation({
    mutationFn: propertyApi.createProperty,
    onSuccess: () => {
      queryClient.invalidateQueries(['properties']);
    },
  });

  const updatePropertyMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: any }) =>
      propertyApi.updateProperty(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries(['properties']);
    },
  });

  const deletePropertyMutation = useMutation({
    mutationFn: propertyApi.deleteProperty,
    onSuccess: () => {
      queryClient.invalidateQueries(['properties']);
    },
  });

  return {
    properties: propertiesQuery.data?.data || [],
    isLoading: propertiesQuery.isLoading,
    error: propertiesQuery.error,
    createProperty: createPropertyMutation.mutate,
    updateProperty: updatePropertyMutation.mutate,
    deleteProperty: deletePropertyMutation.mutate,
  };
}
