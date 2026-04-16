import * as Sentry from '@sentry/react';

const dsn = import.meta.env.VITE_SENTRY_DSN;
const environment = import.meta.env.MODE;

export const initializeMonitoring = (): void => {
  if (!dsn) {
    return;
  }

  Sentry.init({
    dsn,
    environment,
    tracesSampleRate: 0.1,
    integrations: [],
    sendDefaultPii: false,
  });
};
