import { Card, CardContent, CardActions, Typography, Button, Box } from '@mui/material';
import { Edit as EditIcon, Delete as DeleteIcon } from '@mui/icons-material';

interface PropertyCardProps {
  property: {
    id: string;
    address: string;
    type: string;
    rentAmount: number;
    status: string;
  };
  onEdit: (id: string) => void;
  onDelete: (id: string) => void;
}

export function PropertyCard({ property, onEdit, onDelete }: PropertyCardProps) {
  return (
    <Card sx={{ minWidth: 275, mb: 2 }}>
      <CardContent>
        <Typography variant="h6" component="div" gutterBottom>
          {property.address}
        </Typography>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
          <Typography color="text.secondary">
            Type: {property.type}
          </Typography>
          <Typography color="text.secondary">
            Rent: ${property.rentAmount}
          </Typography>
        </Box>
        <Typography 
          sx={{ 
            color: property.status === 'Occupied' ? 'success.main' : 'warning.main'
          }}
        >
          Status: {property.status}
        </Typography>
      </CardContent>
      <CardActions>
        <Button 
          size="small" 
          startIcon={<EditIcon />}
          onClick={() => onEdit(property.id)}
        >
          Edit
        </Button>
        <Button 
          size="small" 
          color="error" 
          startIcon={<DeleteIcon />}
          onClick={() => onDelete(property.id)}
        >
          Delete
        </Button>
      </CardActions>
    </Card>
  );
}
