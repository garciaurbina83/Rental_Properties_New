"use client"

import { FormLabel, FormLabelProps } from '@chakra-ui/react';
import * as React from 'react';

const Label = React.forwardRef<HTMLLabelElement, FormLabelProps>(
  ({ children, ...props }, ref) => {
    return (
      <FormLabel ref={ref} {...props}>
        {children}
      </FormLabel>
    );
  }
);

Label.displayName = 'Label';

export { Label };
