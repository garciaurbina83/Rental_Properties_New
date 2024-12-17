import SentryTest from '@/components/SentryTest';

export default function SentryTestPage() {
  return (
    <div className="container mx-auto py-8">
      <h1 className="text-2xl font-bold mb-6">Sentry Integration Test</h1>
      <div className="max-w-md mx-auto">
        <SentryTest />
      </div>
      
      <div className="mt-8 p-4 bg-gray-100 rounded-lg">
        <h3 className="font-semibold mb-2">Instrucciones:</h3>
        <ul className="list-disc pl-5 space-y-2">
          <li>
            <strong>Trigger Handled Error:</strong> Genera un error controlado que será capturado y enviado a Sentry
          </li>
          <li>
            <strong>Trigger Unhandled Error:</strong> Genera un error no controlado que será capturado por el error boundary global
          </li>
          <li>
            <strong>Send Test Message:</strong> Envía un mensaje de prueba a Sentry
          </li>
        </ul>
      </div>
    </div>
  );
}
