import React from 'react';

interface ErrorBoundaryState {
  hasError: boolean;
  error?: any;
  errorCount: number;
  autoRetrying: boolean;
}

export class ErrorBoundary extends React.Component<React.PropsWithChildren, ErrorBoundaryState> {
  private retryTimeout: NodeJS.Timeout | null = null;

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
        <div style={{ 
          display: 'flex', 
          flexDirection: 'column', 
          alignItems: 'center', 
          justifyContent: 'center', 
          minHeight: '100vh',
          padding: '20px',
          background: '#f5f5f5'
        }}>
          <div style={{ 
            background: 'white', 
            padding: '40px', 
            borderRadius: '8px', 
            boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
            maxWidth: '600px',
            textAlign: 'center'
          }}>
            <h2 style={{ color: '#d32f2f', marginBottom: '16px' }}>[WARNING] Something went wrong</h2>
            
            {autoRetrying && (
              <div style={{ 
                background: '#e3f2fd', 
                padding: '12px', 
                borderRadius: '4px', 
                marginBottom: '16px',
                color: '#1976d2'
              }}>
                🔄 Auto-retry in progress... (Attempt {errorCount}/3)
              </div>
            )}

            {this.isNetworkError(error) && !autoRetrying && (
              <div style={{ 
                background: '#fff3e0', 
                padding: '12px', 
                borderRadius: '4px', 
                marginBottom: '16px',
                color: '#ed6c02'
              }}>
                [WARNING] Network connection issue. Check if backend server is running.
              </div>
            )}

            <pre style={{ 
              background: '#f5f5f5', 
              padding: '16px', 
              borderRadius: '4px',
              overflow: 'auto',
              marginBottom: '24px',
              textAlign: 'left',
              fontSize: '14px'
            }}>
              {String(error?.message || 'Unknown error')}
            </pre>

            <div style={{ display: 'flex', gap: '12px', justifyContent: 'center', flexWrap: 'wrap' }}>
              <button 
                onClick={() => this.setState({ hasError: false, error: null, errorCount: 0 })}
                disabled={autoRetrying}
                style={{
                  padding: '10px 20px',
                  background: autoRetrying ? '#ccc' : '#1976d2',
                  color: 'white',
                  border: 'none',
                  borderRadius: '4px',
                  cursor: autoRetrying ? 'not-allowed' : 'pointer',
                  fontSize: '16px'
                }}
              >
                🔄 Try Again
              </button>
              
              <button 
                onClick={() => window.location.reload()}
                disabled={autoRetrying}
                style={{
                  padding: '10px 20px',
                  background: 'white',
                  color: '#1976d2',
                  border: '1px solid #1976d2',
                  borderRadius: '4px',
                  cursor: autoRetrying ? 'not-allowed' : 'pointer',
                  fontSize: '16px'
                }}
              >
                🔃 Reload Page
              </button>
            </div>

            <p style={{ 
              marginTop: '24px', 
              fontSize: '12px', 
              color: '#666' 
            }}>
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