'use client';

import { useState, useEffect } from 'react';
import { DataTable } from '@/components/ui/data-table';
import { Button } from '@/components/ui/button';
import { AlertCircle, Plus, LayoutGrid, Table as TableIcon } from 'lucide-react';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { columns } from './columns';
import { TenantsGrid } from '@/components/tenants/tenants-grid';
import { Header } from "@/components/header";
import { Tenant } from './types';
import { tenantService } from '@/services/tenantService';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { TenantForm } from '@/components/tenants/tenant-form';

export default function TenantsPage() {
  const [tenants, setTenants] = useState<Tenant[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showForm, setShowForm] = useState(false);
  const [selectedTenantId, setSelectedTenantId] = useState<number | undefined>();
  const [viewMode, setViewMode] = useState<'grid' | 'table'>('table');

  const fetchTenants = async () => {
    try {
      setIsLoading(true);
      setError(null);
      const data = await tenantService.getTenants();
      setTenants(Array.isArray(data) ? data : []);
    } catch (err: any) {
      console.error('Error fetching tenants:', err);
      setError(err.message || 'Failed to load tenants');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchTenants();

    // Event listeners for table actions
    const handleEditTenant = (e: CustomEvent) => {
      const tenant = e.detail;
      setSelectedTenantId(tenant.id);
      setShowForm(true);
    };

    const handleDeleteTenant = async (e: CustomEvent) => {
      const tenant = e.detail;
      try {
        await tenantService.deleteTenant(tenant.id);
        await fetchTenants();
      } catch (err) {
        console.error('Error deleting tenant:', err);
      }
    };

    window.addEventListener('EDIT_TENANT', handleEditTenant as EventListener);
    window.addEventListener('DELETE_TENANT', handleDeleteTenant as EventListener);

    return () => {
      window.removeEventListener('EDIT_TENANT', handleEditTenant as EventListener);
      window.removeEventListener('DELETE_TENANT', handleDeleteTenant as EventListener);
    };
  }, []);

  if (error) {
    return (
      <Alert variant="destructive" className="mb-4">
        <AlertCircle className="h-4 w-4" />
        <AlertTitle>Error</AlertTitle>
        <AlertDescription>{error}</AlertDescription>
      </Alert>
    );
  }

  return (
    <div className="h-full flex-1 flex-col space-y-8 p-8 flex">
      <Header
        title="Tenants"
        description="Manage your rental tenants"
      >
        <div className="flex flex-col space-y-4 w-full">
          <Button
            variant="outline"
            size="default"
            className="bg-primary/10 text-primary hover:bg-primary/20 w-full transition-all hover:bg-muted group"
            onClick={() => {
              setSelectedTenantId(undefined);
              setShowForm(true);
            }}
          >
            <Plus className="mr-2 h-4 w-4 transition-transform group-hover:rotate-90" />
            Add Tenant
          </Button>
          <div className="flex justify-end">
            <div className="flex items-center space-x-2">
              <span className="text-sm text-muted-foreground">
                Current view:
              </span>
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="outline" size="sm" className="h-8">
                    {viewMode === 'grid' ? (
                      <LayoutGrid className="mr-2 h-4 w-4" />
                    ) : (
                      <TableIcon className="mr-2 h-4 w-4" />
                    )}
                    {viewMode === 'grid' ? 'Grid View' : 'Table View'}
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end">
                  <DropdownMenuItem onClick={() => setViewMode('grid')}>
                    <LayoutGrid className="mr-2 h-4 w-4" />
                    Grid View
                  </DropdownMenuItem>
                  <DropdownMenuItem onClick={() => setViewMode('table')}>
                    <TableIcon className="mr-2 h-4 w-4" />
                    Table View
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            </div>
          </div>
        </div>
      </Header>

      <div className="bg-secondary/95 backdrop-blur-sm border border-border/5 rounded-md">
        {viewMode === 'grid' ? (
          <TenantsGrid
            tenants={tenants}
            isLoading={isLoading}
            onEdit={(tenant) => {
              setSelectedTenantId(tenant.id);
              setShowForm(true);
            }}
            onDelete={async (tenant) => {
              try {
                await tenantService.deleteTenant(tenant.id);
                await fetchTenants();
              } catch (err) {
                console.error('Error deleting tenant:', err);
              }
            }}
          />
        ) : (
          <DataTable data={tenants} columns={columns} />
        )}
      </div>

      {showForm && (
        <TenantForm 
          tenantId={selectedTenantId} 
          onClose={() => {
            setShowForm(false);
            fetchTenants();
          }} 
        />
      )}
    </div>
  );
}
