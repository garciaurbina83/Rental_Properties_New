'use client';

import SentryTest from '@/components/sentry-test';
import { useEffect } from 'react';
import * as Sentry from '@sentry/nextjs';

export default function TestPage() {
  useEffect(() => {
    // Verificar que Sentry esté configurado correctamente
    console.log('Sentry DSN:', process.env.NEXT_PUBLIC_SENTRY_DSN);
    
    // Inicializar Sentry con debug activado
    Sentry.init({
      debug: true,
      tracesSampleRate: 1.0,
      replaysOnErrorSampleRate: 1.0,
    });
  }, []);

  return (
    <div className="min-h-screen bg-gray-100 py-12 px-4">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-3xl font-bold mb-8">Página de Prueba de Sentry</h1>
        <div className="bg-white rounded-lg shadow p-6">
          <SentryTest />
        </div>
        <div className="mt-4 text-sm text-gray-600">
          Esta es una página pública para probar la integración con Sentry.
          Revisa la consola del navegador para ver los mensajes de debug.
        </div>
      </div>
    </div>
  );
}
