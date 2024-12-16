'use client';

import { useState, useEffect } from 'react';
import { zodResolver } from '@hookform/resolvers/zod';
import { useForm } from 'react-hook-form';
import * as z from 'zod';
import { PropertyType } from '@/types/property';
import { Button } from '@/components/ui/button';
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from '@/components/ui/form';
import { Input } from '@/components/ui/input';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
  DialogFooter,
} from "@/components/ui/dialog";
import { Building2, DollarSign, Home, Ruler, BedDouble, Bath, Plus, AlertCircle } from "lucide-react";
import { cn } from "@/lib/utils";
import { useToast } from "@/components/ui/use-toast";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { propertyService } from '@/services/propertyService';

const propertyFormSchema = z.object({
  name: z.string().optional(),
  address: z.string().optional(),
  city: z.string().optional(),
  state: z.string().optional(),
  zip_code: z.string().optional(),
  property_type: z.enum(['PRINCIPAL', 'UNIT']).default('PRINCIPAL'),
  bedrooms: z.number().min(0).default(0),
  bathrooms: z.number().min(0).default(0),
  parent_property_id: z.number().optional(),
  status: z.enum(['available', 'rented']).default('available'),
  is_active: z.boolean().default(true),
}).superRefine((data, ctx) => {
  if (data.property_type === 'UNIT') {
    // Para unidades, validar nombre y propiedad principal
    if (!data.name) {
      ctx.addIssue({
        code: z.ZodIssueCode.custom,
        message: "Name is required for units",
        path: ["name"]
      });
    }
    if (!data.parent_property_id) {
      ctx.addIssue({
        code: z.ZodIssueCode.custom,
        message: "Parent property is required for units",
        path: ["parent_property_id"]
      });
    }
  } else {
    // Para propiedades principales, validar campos de dirección
    if (!data.address) {
      ctx.addIssue({
        code: z.ZodIssueCode.custom,
        message: "Address is required for principal properties",
        path: ["address"]
      });
    }
    if (!data.city) {
      ctx.addIssue({
        code: z.ZodIssueCode.custom,
        message: "City is required for principal properties",
        path: ["city"]
      });
    }
    if (!data.state) {
      ctx.addIssue({
        code: z.ZodIssueCode.custom,
        message: "State is required for principal properties",
        path: ["state"]
      });
    }
    if (!data.zip_code) {
      ctx.addIssue({
        code: z.ZodIssueCode.custom,
        message: "Zip code is required for principal properties",
        path: ["zip_code"]
      });
    }
  }
});

type PropertyFormValues = z.infer<typeof propertyFormSchema>;

interface PropertyFormProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSubmit: (data: PropertyFormValues) => void;
  parentId?: number;
}

interface Property {
  id: number;
  name: string;
  property_type: 'PRINCIPAL' | 'UNIT';
}

export function PropertyForm({ open, onOpenChange }: PropertyFormProps) {
  const { toast } = useToast();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [properties, setProperties] = useState<Property[]>([]);

  useEffect(() => {
    const loadProperties = async () => {
      try {
        const data = await propertyService.getProperties();
        setProperties(data);
      } catch (err) {
        console.error('Error loading properties:', err);
      }
    };
    loadProperties();
  }, []);

  const form = useForm<PropertyFormValues>({
    resolver: zodResolver(propertyFormSchema),
    defaultValues: {
      name: '',
      address: '',
      city: '',
      state: '',
      zip_code: '',
      property_type: 'PRINCIPAL',
      bedrooms: 0,
      bathrooms: 0,
      status: 'available',
      is_active: true,
    },
  });

  async function onSubmit(data: PropertyFormValues) {
    setIsLoading(true);
    setError(null);
    try {
      console.log('Submitting property data:', data);
      await propertyService.createProperty(data);
      toast({
        title: "Success",
        description: "Property created successfully",
      });
      form.reset();
      onOpenChange(false);
    } catch (err) {
      console.error('Error creating property:', err);
      setError(err instanceof Error ? err.message : 'Error creating property');
      toast({
        variant: "destructive",
        title: "Error",
        description: "Failed to create property",
      });
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Add New Property</DialogTitle>
          <DialogDescription>
            Fill in the property details below.
          </DialogDescription>
        </DialogHeader>
        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
            {error && (
              <Alert variant="destructive">
                <AlertCircle className="h-4 w-4" />
                <AlertTitle>Error</AlertTitle>
                <AlertDescription>{error}</AlertDescription>
              </Alert>
            )}
            <div className="space-y-4">
              <FormField
                control={form.control}
                name="property_type"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Property Type</FormLabel>
                    <Select onValueChange={field.onChange} defaultValue={field.value}>
                      <FormControl>
                        <SelectTrigger>
                          <SelectValue placeholder="Select property type" />
                        </SelectTrigger>
                      </FormControl>
                      <SelectContent>
                        <SelectItem value="PRINCIPAL">Principal</SelectItem>
                        <SelectItem value="UNIT">Unit</SelectItem>
                      </SelectContent>
                    </Select>
                    <FormMessage />
                  </FormItem>
                )}
              />

              {form.watch('property_type') === 'UNIT' && (
                <>
                  <FormField
                    control={form.control}
                    name="name"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Unit Name</FormLabel>
                        <FormControl>
                          <Input placeholder="E.g. Apartment 101" {...field} />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />

                  <FormField
                    control={form.control}
                    name="parent_property_id"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Parent Property</FormLabel>
                        <Select 
                          onValueChange={(value) => field.onChange(parseInt(value))} 
                          value={field.value?.toString()}
                        >
                          <FormControl>
                            <SelectTrigger>
                              <SelectValue placeholder="Select parent property" />
                            </SelectTrigger>
                          </FormControl>
                          <SelectContent>
                            {properties
                              ?.filter(p => p.property_type === 'PRINCIPAL')
                              .map((property) => (
                                <SelectItem key={property.id} value={property.id.toString()}>
                                  {property.address}
                                </SelectItem>
                              ))}
                          </SelectContent>
                        </Select>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                </>
              )}

              {form.watch('property_type') === 'PRINCIPAL' && (
                <>
                  <FormField
                    control={form.control}
                    name="address"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Address</FormLabel>
                        <FormControl>
                          <Input placeholder="Enter address" {...field} />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />

                  <FormField
                    control={form.control}
                    name="city"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>City</FormLabel>
                        <FormControl>
                          <Input placeholder="Enter city" {...field} />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />

                  <FormField
                    control={form.control}
                    name="state"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>State</FormLabel>
                        <FormControl>
                          <Input placeholder="Enter state" {...field} />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />

                  <FormField
                    control={form.control}
                    name="zip_code"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Zip Code</FormLabel>
                        <FormControl>
                          <Input placeholder="Enter zip code" {...field} />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                </>
              )}

              <div className="grid grid-cols-2 gap-4">
                <FormField
                  control={form.control}
                  name="bedrooms"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Bedrooms</FormLabel>
                      <FormControl>
                        <Input 
                          type="number" 
                          placeholder="0"
                          {...field}
                          onChange={(e) => field.onChange(parseInt(e.target.value))}
                        />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                <FormField
                  control={form.control}
                  name="bathrooms"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Bathrooms</FormLabel>
                      <FormControl>
                        <Input 
                          type="number" 
                          placeholder="0"
                          {...field}
                          onChange={(e) => field.onChange(parseInt(e.target.value))}
                        />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
              </div>
            </div>

            <DialogFooter>
              <Button type="submit" disabled={isLoading}>
                {isLoading ? (
                  <>
                    <span className="loading loading-spinner"></span>
                    Creating...
                  </>
                ) : (
                  'Create Property'
                )}
              </Button>
            </DialogFooter>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  );
}
