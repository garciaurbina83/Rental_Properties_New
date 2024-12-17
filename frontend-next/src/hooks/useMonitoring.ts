import { useEffect } from 'react';
import { logger } from '@/utils/logger';
import { performanceMonitor } from '@/utils/monitoring';

export const useMonitoring = (componentName: string) => {
  useEffect(() => {
    // Registrar montaje del componente
    const mountTime = performance.now();
    logger.log('info', `Component Mounted: ${componentName}`);

    // Iniciar medición de tiempo de vida
    performanceMonitor.startMeasure(`${componentName}_lifetime`);

    return () => {
      // Registrar desmontaje y duración
      const lifetime = performanceMonitor.endMeasure(`${componentName}_lifetime`);
      logger.log('info', `Component Unmounted: ${componentName}`, { lifetime });
    };
  }, [componentName]);

  const trackEvent = (eventName: string, data?: any) => {
    logger.trackUserInteraction(`${componentName}:${eventName}`, data);
  };

  const trackError = (error: Error, context?: any) => {
    logger.logClientError(error, {
      component: componentName,
      ...context
    });
  };

  return {
    trackEvent,
    trackError
  };
};
