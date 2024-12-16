'use client';

import { useEffect } from 'react';
import { Box, Button, Heading, Text } from '@chakra-ui/react';

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    console.error('Error:', error);
  }, [error]);

  return (
    <Box p={8} textAlign="center">
      <Heading mb={4}>Something went wrong!</Heading>
      <Text mb={4}>{error.message}</Text>
      <Button
        onClick={reset}
        colorScheme="blue"
      >
        Try again
      </Button>
    </Box>
  );
}
