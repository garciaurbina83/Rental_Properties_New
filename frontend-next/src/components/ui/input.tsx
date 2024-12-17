import { Input as ChakraInput, InputProps } from '@chakra-ui/react';
import * as React from 'react';

const Input = React.forwardRef<HTMLInputElement, InputProps>(
  (props, ref) => {
    return (
      <ChakraInput
        ref={ref}
        {...props}
      />
    );
  }
);

Input.displayName = 'Input';

export { Input };
