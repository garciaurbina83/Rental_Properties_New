'use client';

import * as Sentry from "@sentry/nextjs";

export default function SentryTest() {
  const checkSentryConfig = () => {
    const client = Sentry.getCurrentHub().getClient();
    const options = client?.getOptions();
    
    console.log('Sentry Client:', {
      dsn: options?.dsn,
      environment: options?.environment,
      release: options?.release,
      debug: options?.debug,
      defaultIntegrations: options?.defaultIntegrations,
      transport: options?.transport?.toString(),
    });
  };

  const throwError = () => {
    try {
      checkSentryConfig();
      throw new Error("Error de prueba desde el botón");
    } catch (error) {
      console.log('Capturando error con Sentry...');
      
      const eventId = Sentry.captureException(error, {
        tags: {
          location: "test-button",
          environment: "development",
        },
        extra: {
          timestamp: new Date().toISOString(),
        },
      });
      
      console.log('Error enviado a Sentry con ID:', eventId);
      console.error('Error capturado:', error);
    }
  };

  const logMessage = () => {
    checkSentryConfig();
    console.log('Enviando mensaje a Sentry...');
    
    const eventId = Sentry.captureMessage("Mensaje de prueba desde el botón", {
      level: "info",
      tags: {
        location: "test-button",
        environment: "development",
      },
      extra: {
        timestamp: new Date().toISOString(),
      },
    });
    
    console.log('Mensaje enviado a Sentry con ID:', eventId);
  };

  return (
    <div className="space-y-4">
      <div className="flex flex-col space-y-2">
        <button
          onClick={throwError}
          className="bg-red-500 hover:bg-red-600 text-white font-bold py-2 px-4 rounded"
        >
          Lanzar Error
        </button>
        <button
          onClick={logMessage}
          className="bg-blue-500 hover:bg-blue-600 text-white font-bold py-2 px-4 rounded"
        >
          Enviar Mensaje
        </button>
        <button
          onClick={checkSentryConfig}
          className="bg-green-500 hover:bg-green-600 text-white font-bold py-2 px-4 rounded"
        >
          Verificar Config
        </button>
      </div>
      <div className="text-sm text-gray-600">
        <p>Revisa la consola del navegador para ver la información de debug.</p>
      </div>
    </div>
  );
}
