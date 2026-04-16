import React from 'react';
import './ErrorBoundary.css';

interface ErrorBoundaryState {
  hasError: boolean;
  error?: any;
  errorCount: number;
  autoRetrying: boolean;
}

export class ErrorBoundary extends React.Component<React.PropsWithChildren, ErrorBoundaryState> {
  private retryTimeout: ReturnType<typeof setTimeout> | null = null;

  constructor(props: React.PropsWithChildren) {
    super(props);
    this.state = { hasError: false, errorCount: 0, autoRetrying: false };
  }

  static getDerivedStateFromError(error: any): Partial<ErrorBoundaryState> {
    return { hasError: true };
  }

  componentDidCatch(error: any, info: any) {
    console.error('UI ErrorBoundary caught error:', error, info);
    
    this.setState(prevState => ({
      error,
      errorCount: prevState.errorCount + 1,
    }));

    // Auto-retry for network errors
    if (this.isNetworkError(error) && this.state.errorCount < 3) {
      this.autoRetry();
    }

    // Log to backend auto-correction system
    this.logErrorToBackend(error, info);
  }

  componentWillUnmount() {
    if (this.retryTimeout) {
      clearTimeout(this.retryTimeout);
    }
  }

  private isNetworkError(error: any): boolean {
    const msg = (error?.message || '').toLowerCase();
    return msg.includes('network') || msg.includes('fetch') || msg.includes('timeout') || msg.includes('connection');
  }

  private autoRetry = () => {
    this.setState({ autoRetrying: true });
    const delay = Math.min(1000 * Math.pow(2, this.state.errorCount), 10000);
    
    this.retryTimeout = setTimeout(() => {
      console.log('Auto-retrying after error...');
      this.setState({ hasError: false, error: null, autoRetrying: false });
    }, delay);
  };

  private logErrorToBackend = async (error: any, info: any) => {
    try {
      await fetch('/api/error-correction/log', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: error?.message || 'Unknown error',
          stack: error?.stack,
          componentStack: info?.componentStack,
          timestamp: new Date().toISOString(),
          url: window.location.href,
        }),
      });
    } catch (logError) {
      console.warn('Failed to log error to backend:', logError);
    }
  };

  render() {
    if (this.state.hasError) {
      const { error, autoRetrying, errorCount } = this.state;
      
      return (
        <div className="error-boundary-root">
          <div className="error-boundary-card">
            <h2 className="error-boundary-title">[WARNING] Something went wrong</h2>
            
            {autoRetrying && (
              <div className="error-boundary-banner retry">
                🔄 Auto-retry in progress... (Attempt {errorCount}/3)
              </div>
            )}

            {this.isNetworkError(error) && !autoRetrying && (
              <div className="error-boundary-banner network">
                [WARNING] Network connection issue. Check if backend server is running.
              </div>
            )}

            <pre className="error-boundary-message">
              {String(error?.message || 'Unknown error')}
            </pre>

            <div className="error-boundary-actions">
              <button 
                onClick={() => this.setState({ hasError: false, error: null, errorCount: 0 })}
                disabled={autoRetrying}
                className={`error-boundary-button primary${autoRetrying ? ' disabled' : ''}`}
              >
                🔄 Try Again
              </button>
              
              <button 
                onClick={() => window.location.reload()}
                disabled={autoRetrying}
                className={`error-boundary-button secondary${autoRetrying ? ' disabled' : ''}`}
              >
                🔃 Reload Page
              </button>
            </div>

            <p className="error-boundary-footer">
              [OK] Error logged to auto-correction system
            </p>
          </div>
        </div>
      );
    }
    return this.props.children;
  }
}

export default ErrorBoundary;