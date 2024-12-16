import * as Sentry from '@sentry/nextjs';
import { Button } from '@/components/ui/button';

export default function SentryTest() {
  const throwError = () => {
    try {
      throw new Error('Test error for Sentry');
    } catch (error) {
      Sentry.captureException(error);
      console.error('Error enviado a Sentry:', error);
    }
  };

  const throwUnhandledError = () => {
    // Este error no está en un try-catch, será capturado por el error boundary global
    throw new Error('Test unhandled error for Sentry');
  };

  const logMessage = () => {
    Sentry.captureMessage('Test message from frontend', 'info');
    console.log('Mensaje enviado a Sentry');
  };

  return (
    <div className="p-4 space-y-4 border rounded-lg">
      <h2 className="text-xl font-bold">Sentry Test Panel</h2>
      <div className="space-y-2">
        <Button 
          onClick={throwError}
          variant="outline"
          className="w-full"
        >
          Trigger Handled Error
        </Button>
        
        <Button 
          onClick={throwUnhandledError}
          variant="destructive"
          className="w-full"
        >
          Trigger Unhandled Error
        </Button>
        
        <Button 
          onClick={logMessage}
          variant="secondary"
          className="w-full"
        >
          Send Test Message
        </Button>
      </div>
    </div>
  );
}
