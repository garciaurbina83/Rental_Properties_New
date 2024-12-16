'use client';

import { Property } from '@/types/property';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Box } from '@chakra-ui/react';

interface PropertyListProps {
  properties: Property[];
  onDelete: (id: number) => void;
}

export default function PropertyList({ properties, onDelete }: PropertyListProps) {
  const getStatusBadge = (status: string = 'available') => {
    const statusColors = {
      available: "green",
      rented: "blue",
      maintenance: "yellow",
      unavailable: "gray"
    };

    return (
      <Badge colorScheme={statusColors[status as keyof typeof statusColors] || "gray"}>
        {status.charAt(0).toUpperCase() + status.slice(1)}
      </Badge>
    );
  };

  return (
    <Box borderWidth="1px" borderRadius="lg">
      <Table variant="simple">
        <TableHeader>
          <TableRow>
            <TableHead>Name</TableHead>
            <TableHead>Address</TableHead>
            <TableHead>Size</TableHead>
            <TableHead>Bedrooms</TableHead>
            <TableHead>Monthly Rent</TableHead>
            <TableHead>Status</TableHead>
            <TableHead>Actions</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {properties.length === 0 ? (
            <TableRow>
              <TableCell colSpan={7} className="h-24 text-center">
                No properties found.
              </TableCell>
            </TableRow>
          ) : (
            properties.map((property) => (
              <TableRow key={property.id}>
                <TableCell>{property.name || 'Unnamed Property'}</TableCell>
                <TableCell>{`${property.address}, ${property.city || ''}, ${property.state || ''}`}</TableCell>
                <TableCell>{property.size ? `${property.size} m²` : 'N/A'}</TableCell>
                <TableCell>{property.bedrooms || 'N/A'}</TableCell>
                <TableCell>
                  {property.monthly_rent
                    ? new Intl.NumberFormat('en-US', {
                        style: 'currency',
                        currency: 'USD'
                      }).format(property.monthly_rent)
                    : 'N/A'}
                </TableCell>
                <TableCell>{getStatusBadge(property.status)}</TableCell>
                <TableCell>
                  <Button
                    variant="destructive"
                    size="sm"
                    onClick={() => onDelete(property.id)}
                  >
                    Delete
                  </Button>
                </TableCell>
              </TableRow>
            ))
          )}
        </TableBody>
      </Table>
    </Box>
  );
}
