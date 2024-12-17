import { Badge as ChakraBadge, BadgeProps } from '@chakra-ui/react';

interface CustomBadgeProps extends BadgeProps {
  variant?: 'default' | 'secondary' | 'destructive' | 'outline';
}

export function Badge({ variant = 'default', children, ...props }: CustomBadgeProps) {
  const colorScheme = {
    default: 'blue',
    secondary: 'gray',
    destructive: 'red',
    outline: 'gray'
  }[variant];

  return (
    <ChakraBadge
      colorScheme={colorScheme}
      variant={variant === 'outline' ? 'outline' : 'solid'}
      {...props}
    >
      {children}
    </ChakraBadge>
  );
}
