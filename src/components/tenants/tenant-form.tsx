'use client';

import { useState, useEffect } from 'react';
import { zodResolver } from '@hookform/resolvers/zod';
import { useForm } from 'react-hook-form';
import * as z from 'zod';
import { format } from 'date-fns';
import { CalendarIcon, User, Home, AlertCircle } from 'lucide-react';
import { Property } from '@/types/property';
import { propertyService } from '@/services/propertyService';
import { tenantService } from '@/services/tenantService';
import DatePicker from "react-datepicker";
import "react-datepicker/dist/react-datepicker.css";

import { Button } from "@/components/ui/button";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from "@/components/ui/dialog";
import { useToast } from "@/components/ui/use-toast";
import { cn } from "@/lib/utils";

const tenantFormSchema = z.object({
  first_name: z.string().min(1, 'First name is required'),
  last_name: z.string().min(1, 'Last name is required'),
  property_id: z.number().min(1, 'Property is required'),
  lease_start: z.date({
    required_error: "Lease start date is required",
  }),
  lease_end: z.date({
    required_error: "Lease end date is required",
  }),
  monthly_rent: z.number().min(0, 'Monthly rent must be greater than 0'),
  deposit: z.number().min(0, 'Deposit must be greater than 0'),
  payment_day: z.number().min(1, 'Payment day is required').max(31, 'Invalid payment day'),
});

type TenantFormValues = z.infer<typeof tenantFormSchema>;

interface TenantFormProps {
  tenantId?: number;
  onClose: () => void;
  onSave: () => void;
  onSuccess?: () => void;
}

export function TenantForm({ tenantId, onClose, onSave, onSuccess }: TenantFormProps) {
  const { toast } = useToast();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [properties, setProperties] = useState<Property[]>([]);

  useEffect(() => {
    const loadProperties = async () => {
      try {
        const data = await propertyService.getProperties();
        setProperties(data);
      } catch (err) {
        console.error('Error loading properties:', err);
        setError('Failed to load properties');
      }
    };
    loadProperties();
  }, []);

  const defaultValues: Partial<TenantFormValues> = {
    first_name: "",
    last_name: "",
    property_id: undefined,
    lease_start: undefined,
    lease_end: undefined,
    monthly_rent: 0,
    deposit: 0,
    payment_day: 1,
  };

  const form = useForm<TenantFormValues>({
    resolver: zodResolver(tenantFormSchema),
    defaultValues,
  });

  const onSubmit = async (data: TenantFormValues) => {
    try {
      setIsSubmitting(true);
      setError(null);

      const formattedData = {
        ...data,
        lease_start: format(data.lease_start, 'yyyy-MM-dd'),
        lease_end: format(data.lease_end, 'yyyy-MM-dd'),
        monthly_rent: parseFloat(data.monthly_rent.toString()),
        deposit: parseFloat(data.deposit.toString()),
      };

      if (tenantId) {
        await tenantService.updateTenant(tenantId, formattedData);
      } else {
        await tenantService.createTenant(formattedData);
      }

      toast({
        title: 'Success!',
        description: tenantId ? 'Tenant updated successfully.' : 'Tenant created successfully.',
      });

      onClose();
      onSave();
    } catch (err: any) {
      console.error('Error submitting form:', err);
      setError(err.response?.data?.detail || 'An error occurred while saving the tenant');
      toast({
        title: "Error",
        description: err.response?.data?.detail || 'An error occurred while saving the tenant',
        variant: "destructive",
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Dialog open={true} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-[425px] p-6 bg-secondary/95 backdrop-blur-sm border border-border/5">
        <DialogHeader className="pb-4">
          <DialogTitle className="text-2xl font-bold flex items-center gap-2 text-foreground">
            <User className="h-6 w-6 text-muted-foreground" />
            {tenantId ? 'Edit Tenant' : 'Add New Tenant'}
          </DialogTitle>
          <DialogDescription className="text-muted-foreground">
            Fill in the details below to {tenantId ? 'update the' : 'add a new'} tenant.
          </DialogDescription>
        </DialogHeader>

        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
            {error && (
              <Alert variant="destructive">
                <AlertCircle className="h-4 w-4" />
                <AlertTitle>Error</AlertTitle>
                <AlertDescription>{error}</AlertDescription>
              </Alert>
            )}

            <div className="grid gap-4">
              <FormField
                control={form.control}
                name="first_name"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel className="text-sm font-medium flex items-center gap-2 text-muted-foreground">
                      First Name
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
                name="last_name"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel className="text-sm font-medium flex items-center gap-2 text-muted-foreground">
                      Last Name
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
                name="property_id"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel className="text-sm font-medium flex items-center gap-2 text-muted-foreground">
                      <Home className="h-4 w-4" />
                      Property
                    </FormLabel>
                    <Select onValueChange={(value) => field.onChange(Number(value))} value={field.value?.toString()}>
                      <FormControl>
                        <SelectTrigger className="bg-background/50 border-border/10 focus-visible:ring-1 focus-visible:ring-ring/20">
                          <SelectValue placeholder="Select a property" />
                        </SelectTrigger>
                      </FormControl>
                      <SelectContent>
                        {properties.map((property) => (
                          <SelectItem key={property.id} value={property.id.toString()}>
                            {property.property_type === 'UNIT' 
                              ? `${property.name} (Unit)`
                              : `${property.address} (Principal)`}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <div className="grid gap-4">
                <FormField
                  control={form.control}
                  name="lease_start"
                  render={({ field }) => (
                    <FormItem className="flex flex-col">
                      <FormLabel>Lease Start</FormLabel>
                      <FormControl>
                        <div className="datepicker-container">
                          <DatePicker
                            selected={field.value}
                            onChange={(date: Date) => field.onChange(date)}
                            dateFormat="MMMM d, yyyy"
                            placeholderText="Select lease start date"
                            className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2"
                            showMonthDropdown
                            showYearDropdown
                            dropdownMode="select"
                            popperClassName="datepicker-popper"
                            calendarClassName="datepicker-calendar"
                            showMonthYearPicker={false}
                          />
                        </div>
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                <FormField
                  control={form.control}
                  name="lease_end"
                  render={({ field }) => (
                    <FormItem className="flex flex-col">
                      <FormLabel>Lease End</FormLabel>
                      <FormControl>
                        <div className="datepicker-container">
                          <DatePicker
                            selected={field.value}
                            onChange={(date: Date) => field.onChange(date)}
                            dateFormat="MMMM d, yyyy"
                            minDate={form.getValues('lease_start')}
                            placeholderText="Select lease end date"
                            className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2"
                            showMonthDropdown
                            showYearDropdown
                            dropdownMode="select"
                            popperClassName="datepicker-popper"
                            calendarClassName="datepicker-calendar"
                            showMonthYearPicker={false}
                          />
                        </div>
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
              </div>

              <FormField
                control={form.control}
                name="monthly_rent"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel className="text-sm font-medium flex items-center gap-2 text-muted-foreground">
                      Monthly Rent
                    </FormLabel>
                    <FormControl>
                      <Input
                        type="number"
                        className="bg-background/50 border-border/10 focus-visible:ring-1 focus-visible:ring-ring/20"
                        {...field}
                        onChange={e => field.onChange(Number(e.target.value))}
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="deposit"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel className="text-sm font-medium flex items-center gap-2 text-muted-foreground">
                      Deposit
                    </FormLabel>
                    <FormControl>
                      <Input
                        type="number"
                        className="bg-background/50 border-border/10 focus-visible:ring-1 focus-visible:ring-ring/20"
                        {...field}
                        onChange={e => field.onChange(Number(e.target.value))}
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="payment_day"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel className="text-sm font-medium flex items-center gap-2 text-muted-foreground">
                      Payment Day
                    </FormLabel>
                    <FormControl>
                      <Input
                        type="number"
                        min={1}
                        max={31}
                        className="bg-background/50 border-border/10 focus-visible:ring-1 focus-visible:ring-ring/20"
                        {...field}
                        onChange={e => field.onChange(Number(e.target.value))}
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </div>

            <DialogFooter>
              <Button
                type="submit"
                className="bg-primary/10 text-primary hover:bg-primary/20"
                disabled={isSubmitting}
              >
                {isSubmitting ? (
                  <>Saving...</>
                ) : (
                  <>{tenantId ? 'Save Changes' : 'Add Tenant'}</>
                )}
              </Button>
            </DialogFooter>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  );
}
