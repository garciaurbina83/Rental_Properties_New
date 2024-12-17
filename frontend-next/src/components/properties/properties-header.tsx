'use client';

import { ChevronsUpDown } from "lucide-react";

type SortConfig = {
  key: 'name' | 'address' | 'status' | 'bedrooms' | 'bathrooms' | 'updated_at';
  direction: 'asc' | 'desc';
} | null;

interface PropertiesHeaderProps {
  handleSort: (key: SortConfig['key']) => void;
  sortConfig: SortConfig;
}

export const PropertiesHeader = ({ handleSort, sortConfig }: PropertiesHeaderProps) => {
  const getSortIcon = (key: SortConfig['key']) => {
    if (sortConfig?.key === key) {
      return (
        <ChevronsUpDown className={`ml-1 h-4 w-4 ${
          sortConfig.direction === 'asc' ? 'transform rotate-180' : ''
        }`} />
      );
    }
    return <ChevronsUpDown className="ml-1 h-4 w-4 text-muted-foreground/50" />;
  };

  return (
    <div className="grid grid-cols-7 gap-4 px-6 py-3 border-b">
      <button 
        onClick={() => handleSort('name')} 
        className="text-sm text-muted-foreground flex items-center cursor-pointer hover:text-foreground"
      >
        Property name {getSortIcon('name')}
      </button>
      <button 
        onClick={() => handleSort('address')} 
        className="text-sm text-muted-foreground flex items-center cursor-pointer hover:text-foreground col-span-2"
      >
        Address {getSortIcon('address')}
      </button>
      <button 
        onClick={() => handleSort('status')} 
        className="text-sm text-muted-foreground flex items-center cursor-pointer hover:text-foreground"
      >
        Status {getSortIcon('status')}
      </button>
      <button 
        onClick={() => handleSort('bedrooms')} 
        className="text-sm text-muted-foreground flex items-center cursor-pointer hover:text-foreground"
      >
        Beds {getSortIcon('bedrooms')}
      </button>
      <button 
        onClick={() => handleSort('bathrooms')} 
        className="text-sm text-muted-foreground flex items-center cursor-pointer hover:text-foreground"
      >
        Baths {getSortIcon('bathrooms')}
      </button>
      <div className="text-sm text-muted-foreground text-right">Actions</div>
    </div>
  );
};
