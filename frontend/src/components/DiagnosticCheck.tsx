import React, { useEffect } from 'react';

const DiagnosticCheck: React.FC = () => {
  useEffect(() => {
    console.log('[DiagnosticCheck] Component mounted successfully');
    
    // Check if we can access basic APIs
    try {
      console.log('[DiagnosticCheck] Window object:', !!window);
      console.log('[DiagnosticCheck] Document object:', !!document);
      console.log('[DiagnosticCheck] React version:', React.version);
      console.log('[DiagnosticCheck] Current URL:', window.location.href);
    } catch (error) {
      console.error('[DiagnosticCheck] Error in diagnostic check:', error);
    }
  }, []);

  return (
    <div style={{ padding: '20px', backgroundColor: '#f0f0f0', border: '1px solid #ccc' }}>
      <h1>Diagnostic Check Component</h1>
      <p>If you can see this, React is rendering components successfully.</p>
      <p>Current time: {new Date().toISOString()}</p>
    </div>
  );
};

export default DiagnosticCheck;