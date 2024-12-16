import * as Sentry from '@sentry/nextjs';

// Tipos de logs
export enum LogLevel {
  INFO = 'info',
  WARNING = 'warning',
  ERROR = 'error',
  DEBUG = 'debug'
}

// Interfaz para métricas de rendimiento
interface PerformanceMetric {
  name: string;
  value: number;
  unit: string;
  tags?: Record<string, string>;
}

class Logger {
  private static instance: Logger;
  private isDevelopment: boolean;

  private constructor() {
    this.isDevelopment = process.env.NODE_ENV === 'development';
  }

  public static getInstance(): Logger {
    if (!Logger.instance) {
      Logger.instance = new Logger();
    }
    return Logger.instance;
  }

  // Log general con nivel configurable
  public log(level: LogLevel, message: string, extra?: any) {
    const timestamp = new Date().toISOString();
    const logData = {
      timestamp,
      level,
      message,
      ...(extra && { extra })
    };

    if (this.isDevelopment) {
      this.consoleLog(level, logData);
    }

    // Enviar a Sentry si es error
    if (level === LogLevel.ERROR) {
      Sentry.captureMessage(message, {
        level: Sentry.Severity.Error,
        extra: extra
      });
    }
  }

  // Log específico para errores del cliente
  public logClientError(error: Error, context?: any) {
    Sentry.captureException(error, {
      extra: context
    });

    this.log(LogLevel.ERROR, error.message, {
      stack: error.stack,
      context
    });
  }

  // Tracking de interacciones del usuario
  public trackUserInteraction(action: string, details?: any) {
    this.log(LogLevel.INFO, `User Action: ${action}`, details);
    // Aquí se puede integrar con sistemas de analytics
  }

  // Métricas de rendimiento
  public logPerformanceMetric(metric: PerformanceMetric) {
    this.log(LogLevel.INFO, `Performance Metric: ${metric.name}`, {
      value: metric.value,
      unit: metric.unit,
      tags: metric.tags
    });
  }

  // Utilidad para logs en consola durante desarrollo
  private consoleLog(level: LogLevel, data: any) {
    switch (level) {
      case LogLevel.ERROR:
        console.error(data);
        break;
      case LogLevel.WARNING:
        console.warn(data);
        break;
      case LogLevel.INFO:
        console.info(data);
        break;
      case LogLevel.DEBUG:
        console.debug(data);
        break;
    }
  }
}

export const logger = Logger.getInstance();
