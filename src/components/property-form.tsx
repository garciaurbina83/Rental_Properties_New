'use client';

import { useState } from 'react';
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
} from "@/components/ui/dialog";
import { Building2, DollarSign, Home, Ruler, BedDouble, Bath, Plus } from "lucide-react";
import { cn } from "@/lib/utils";
import { useToast } from "@/components/ui/use-toast";

const propertyFormSchema = z.object({
  name: z.string().optional(),
  address: z.string().min(1, 'Street address is required'),
  city: z.string().min(1, 'City is required'),
  state: z.string().min(1, 'State is required'),
  zip_code: z.string().min(1, 'ZIP code is required'),
  property_type: z.nativeEnum(PropertyType),
  bedrooms: z.coerce.number().min(0).max(20).default(0),
  bathrooms: z.coerce.number().min(0).max(20).default(0),
}).refine((data) => {
  // Si es una unidad, el nombre es requerido
  if (data.property_type === PropertyType.UNIT) {
    return !!data.name && data.name.length > 0;
  }
  return true;
}, {
  message: "Unit name is required for unit properties",
  path: ["name"]
});

type PropertyFormValues = z.infer<typeof propertyFormSchema>;

interface PropertyFormProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSubmit: (data: PropertyFormValues & { name: string, parent_id?: number }) => void;
  parentId?: number;
}

export function PropertyForm({ open, onOpenChange, onSubmit, parentId }: PropertyFormProps) {
  const { toast } = useToast();
  
  const form = useForm<PropertyFormValues>({
    resolver: zodResolver(propertyFormSchema),
    defaultValues: {
      name: '',
      address: '',
      city: '',
      state: '',
      zip_code: '',
      property_type: PropertyType.MAIN,
      bedrooms: 0,
      bathrooms: 0,
    },
  });

  const onFormSubmit = async (data: PropertyFormValues) => {
    try {
      console.log('Form Data:', data);
      console.log('Parent ID:', parentId);

      const formattedData = {
        ...data,
        name: data.property_type === PropertyType.UNIT ? data.name : data.address,
        parent_id: data.property_type === PropertyType.UNIT ? parentId : undefined,
        bedrooms: Number(data.bedrooms) || 0,
        bathrooms: Number(data.bathrooms) || 0,
      };

      console.log('Formatted Data:', formattedData);
      
      await onSubmit(formattedData);
      
      form.reset();
      onOpenChange(false);
      
      toast({
        title: "Success!",
        description: "Property created successfully.",
      });
    } catch (error) {
      console.error('Error submitting form:', error);
      toast({
        variant: "destructive",
        title: "Error",
        description: error instanceof Error ? error.message : "Failed to create property. Please try again.",
      });
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[800px] p-6 bg-secondary/95 backdrop-blur-sm border border-border/5">
        <DialogHeader className="pb-4">
          <DialogTitle className="text-2xl font-bold flex items-center gap-2 text-foreground">
            <Building2 className="h-6 w-6 text-muted-foreground" />
            Add New Property
          </DialogTitle>
          <DialogDescription className="text-muted-foreground">
            Fill in the details below to add a new property to your portfolio.
          </DialogDescription>
        </DialogHeader>
        <Form {...form}>
          <form onSubmit={form.handleSubmit(onFormSubmit)} className="space-y-4">
            <div className="space-y-4">
              {form.watch('property_type') === PropertyType.UNIT && (
                <FormField
                  control={form.control}
                  name="name"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel className="text-sm font-medium flex items-center gap-2 text-muted-foreground">
                        <Home className="h-4 w-4" />
                        Unit Name
                      </FormLabel>
                      <FormControl>
                        <Input 
                          className="bg-background/50 border-border/10 focus-visible:ring-1 focus-visible:ring-ring/20" 
                          placeholder="Unit Name (required)"
                          {...field} 
                        />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
              )}
              <FormField
                control={form.control}
                name="address"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel className="text-sm font-medium flex items-center gap-2 text-muted-foreground">
                      <Home className="h-4 w-4" />
                      Street Address
                    </FormLabel>
                    <FormControl>
                      <Input 
                        className="bg-background/50 border-border/10 focus-visible:ring-1 focus-visible:ring-ring/20" 
                        placeholder="123 Main St"
                        {...field} 
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <div className="grid gap-4 grid-cols-1 md:grid-cols-2">
                <FormField
                  control={form.control}
                  name="city"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel className="text-sm font-medium flex items-center gap-2 text-muted-foreground">
                        <Home className="h-4 w-4" />
                        City
                      </FormLabel>
                      <FormControl>
                        <Input 
                          className="bg-background/50 border-border/10 focus-visible:ring-1 focus-visible:ring-ring/20" 
                          {...field} 
                        />
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
                      <FormLabel className="text-sm font-medium flex items-center gap-2 text-muted-foreground">
                        <Home className="h-4 w-4" />
                        State
                      </FormLabel>
                      <FormControl>
                        <Input 
                          className="bg-background/50 border-border/10 focus-visible:ring-1 focus-visible:ring-ring/20" 
                          {...field} 
                        />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
              </div>

              <div className="grid gap-4 grid-cols-1 md:grid-cols-2">
                <FormField
                  control={form.control}
                  name="zip_code"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel className="text-sm font-medium flex items-center gap-2 text-muted-foreground">
                        <Home className="h-4 w-4" />
                        ZIP Code
                      </FormLabel>
                      <FormControl>
                        <Input 
                          className="bg-background/50 border-border/10 focus-visible:ring-1 focus-visible:ring-ring/20" 
                          {...field} 
                        />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
              </div>

              <div className="grid gap-12 grid-cols-1 md:grid-cols-3">
                <FormField
                  control={form.control}
                  name="bedrooms"
                  render={({ field }) => (
                    <FormItem className="w-full max-w-[140px]">
                      <FormLabel className="text-sm font-medium flex items-center gap-2 text-muted-foreground">
                        <BedDouble className="h-4 w-4" />
                        Bedrooms
                      </FormLabel>
                      <FormControl>
                        <Input 
                          type="number"
                          min="0"
                          max="20"
                          className="bg-background/50 border-border/10 focus-visible:ring-1 focus-visible:ring-ring/20 h-8 px-2" 
                          {...field}
                          onChange={(e) => field.onChange(e.target.valueAsNumber)}
                          value={field.value || 0}
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
                    <FormItem className="w-full max-w-[140px]">
                      <FormLabel className="text-sm font-medium flex items-center gap-2 text-muted-foreground">
                        <Bath className="h-4 w-4" />
                        Bathrooms
                      </FormLabel>
                      <FormControl>
                        <Input 
                          type="number"
                          min="0"
                          max="20"
                          className="bg-background/50 border-border/10 focus-visible:ring-1 focus-visible:ring-ring/20 h-8 px-2" 
                          {...field}
                          onChange={(e) => field.onChange(e.target.valueAsNumber)}
                          value={field.value || 0}
                        />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
              </div>

              <FormField
                control={form.control}
                name="property_type"
                render={({ field }) => (
                  <FormItem className="w-full">
                    <FormLabel className="text-sm font-medium flex items-center gap-2 text-muted-foreground">
                      <Building2 className="h-4 w-4" />
                      Property Type
                    </FormLabel>
                    <Select onValueChange={field.onChange} defaultValue={field.value}>
                      <FormControl>
                        <SelectTrigger className="bg-background/50 border-border/10 focus:ring-1 focus:ring-ring/20">
                          <SelectValue placeholder="Select property type" />
                        </SelectTrigger>
                      </FormControl>
                      <SelectContent>
                        <SelectItem key="main" value={PropertyType.MAIN}>
                          Main Property
                        </SelectItem>
                        <SelectItem key="unit" value={PropertyType.UNIT}>
                          Unit
                        </SelectItem>
                      </SelectContent>
                    </Select>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </div>

            <div className="flex justify-end gap-4 pt-6">
              <Button
                type="button"
                onClick={() => onOpenChange(false)}
                className="bg-zinc-900 text-zinc-400 hover:text-white border-zinc-800 hover:bg-zinc-800/90 hover:border-zinc-700 transition-colors h-10 px-6"
              >
                Cancel
              </Button>
              <Button 
                type="submit"
                className="bg-indigo-500 hover:bg-indigo-600 text-white shadow-[0_0_20px_rgba(99,102,241,0.3)] hover:shadow-[0_0_25px_rgba(99,102,241,0.4)] transition-all h-10 px-8 font-medium"
              >
                <Plus className="h-4 w-4 mr-2" />
                Add Property
              </Button>
            </div>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  );
}
