import { z } from 'zod';

// Esquema para la dirección
export const addressSchema = z.object({
  street: z.string().min(1, 'La calle es requerida'),
  city: z.string().min(1, 'La ciudad es requerida'),
  state: z.string().min(1, 'El estado es requerido'),
  zipCode: z.string().regex(/^\d{5}$/, 'El código postal debe tener 5 dígitos'),
});

// Esquema para las características
export const featuresSchema = z.object({
  bedrooms: z.number().int().min(0, 'El número de habitaciones no puede ser negativo'),
  bathrooms: z.number().int().min(0, 'El número de baños no puede ser negativo'),
  parking: z.number().int().min(0, 'El número de estacionamientos no puede ser negativo'),
  squareMeters: z.number().positive('El área debe ser mayor a 0'),
});

// Esquema para la propiedad
export const propertySchema = z.object({
  name: z.string().min(1, 'El nombre es requerido'),
  description: z.string().min(10, 'La descripción debe tener al menos 10 caracteres'),
  type: z.enum(['house', 'apartment', 'commercial'], {
    errorMap: () => ({ message: 'Tipo de propiedad inválido' }),
  }),
  status: z.enum(['available', 'rented', 'maintenance', 'sold'], {
    errorMap: () => ({ message: 'Estado de propiedad inválido' }),
  }),
  price: z.number().positive('El precio debe ser mayor a 0'),
  address: addressSchema,
  features: featuresSchema,
  images: z.array(z.string().url('URL de imagen inválida')).optional(),
  amenities: z.array(z.string()).optional(),
});

// Esquema para la creación de propiedades (algunos campos opcionales)
export const propertyCreateSchema = propertySchema.extend({
  description: z.string().min(10, 'La descripción debe tener al menos 10 caracteres').optional(),
  images: z.array(z.string().url('URL de imagen inválida')).optional(),
  amenities: z.array(z.string()).optional(),
}).refine(
  (data) => {
    if (data.type === 'commercial') {
      return true; // No validar habitaciones y baños para propiedades comerciales
    }
    return data.features.bedrooms > 0 && data.features.bathrooms > 0;
  },
  {
    message: 'Las propiedades residenciales deben tener al menos una habitación y un baño',
    path: ['features'],
  }
);

// Tipos inferidos de los esquemas
export type Property = z.infer<typeof propertySchema>;
export type PropertyCreate = z.infer<typeof propertyCreateSchema>;

// Función para validar una propiedad
export const validateProperty = (data: unknown): { success: boolean; error?: string } => {
  try {
    propertySchema.parse(data);
    return { success: true };
  } catch (error) {
    if (error instanceof z.ZodError) {
      return {
        success: false,
        error: error.errors.map(err => `${err.path.join('.')}: ${err.message}`).join(', '),
      };
    }
    return { success: false, error: 'Error de validación desconocido' };
  }
};

// Función para validar una propiedad al crearla
export const validatePropertyCreate = (data: unknown): { success: boolean; error?: string } => {
  try {
    propertyCreateSchema.parse(data);
    return { success: true };
  } catch (error) {
    if (error instanceof z.ZodError) {
      return {
        success: false,
        error: error.errors.map(err => `${err.path.join('.')}: ${err.message}`).join(', '),
      };
    }
    return { success: false, error: 'Error de validación desconocido' };
  }
};
