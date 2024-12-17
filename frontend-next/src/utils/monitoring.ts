import { logger } from './logger';

interface PerformanceData {
  name: string;
  startTime: number;
  duration?: number;
  metadata?: Record<string, any>;
}

class PerformanceMonitor {
  private static instance: PerformanceMonitor;
  private performanceEntries: Map<string, PerformanceData>;

  private constructor() {
    this.performanceEntries = new Map();
  }

  public static getInstance(): PerformanceMonitor {
    if (!PerformanceMonitor.instance) {
      PerformanceMonitor.instance = new PerformanceMonitor();
    }
    return PerformanceMonitor.instance;
  }

  // Iniciar medición de rendimiento
  public startMeasure(name: string, metadata?: Record<string, any>) {
    const startTime = performance.now();
    this.performanceEntries.set(name, {
      name,
      startTime,
      metadata
    });
  }

  // Finalizar medición y registrar resultados
  public endMeasure(name: string) {
    const entry = this.performanceEntries.get(name);
    if (!entry) {
      logger.log('warning', `No performance measurement found for: ${name}`);
      return;
    }

    const duration = performance.now() - entry.startTime;
    entry.duration = duration;

    logger.logPerformanceMetric({
      name: entry.name,
      value: duration,
      unit: 'ms',
      tags: entry.metadata
    });

    this.performanceEntries.delete(name);
    return duration;
  }

  // Monitorear carga de recursos
  public monitorResourceLoading() {
    if (typeof window !== 'undefined') {
      const observer = new PerformanceObserver((list) => {
        list.getEntries().forEach((entry) => {
          logger.logPerformanceMetric({
            name: `Resource Load: ${entry.name}`,
            value: entry.duration,
            unit: 'ms',
            tags: {
              type: entry.initiatorType,
              size: (entry as any).transferSize?.toString() || 'unknown'
            }
          });
        });
      });

      observer.observe({ entryTypes: ['resource'] });
    }
  }

  // Monitorear errores de red
  public monitorNetworkErrors() {
    if (typeof window !== 'undefined') {
      window.addEventListener('error', (event) => {
        if (event.target instanceof HTMLImageElement || 
            event.target instanceof HTMLScriptElement || 
            event.target instanceof HTMLLinkElement) {
          logger.logClientError(new Error(`Resource failed to load: ${event.target.src || event.target.href}`));
        }
      }, true);
    }
  }

  // Monitorear métricas web vitales
  public monitorWebVitals() {
    if (typeof window !== 'undefined') {
      // Importación dinámica de web-vitals
      import('web-vitals').then(({ getCLS, getFID, getLCP }) => {
        getCLS((metric) => {
          logger.logPerformanceMetric({
            name: 'Cumulative Layout Shift',
            value: metric.value,
            unit: 'none'
          });
        });

        getFID((metric) => {
          logger.logPerformanceMetric({
            name: 'First Input Delay',
            value: metric.value,
            unit: 'ms'
          });
        });

        getLCP((metric) => {
          logger.logPerformanceMetric({
            name: 'Largest Contentful Paint',
            value: metric.value,
            unit: 'ms'
          });
        });
      });
    }
  }
}

export const performanceMonitor = PerformanceMonitor.getInstance();
