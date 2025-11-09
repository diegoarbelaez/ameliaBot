import React, { useState, useEffect } from 'react';
import './App.css';

function App() {
  const [backendMessage, setBackendMessage] = useState('Loading...');
  const [backendStatus, setBackendStatus] = useState('checking');
  const [error, setError] = useState(null);

  useEffect(() => {
    // Test backend connectivity
    const testBackend = async () => {
      try {
        const apiUrl = process.env.REACT_APP_API_URL || 'http://localhost:8000';
        const response = await fetch(`${apiUrl}/`);
        
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        setBackendMessage(data.message);
        setBackendStatus('connected');
      } catch (err) {
        console.error('Backend connection error:', err);
        setBackendMessage('Failed to connect to backend');
        setBackendStatus('error');
        setError(err.message);
      }
    };

    testBackend();
  }, []);

  return (
    <div className="App">
      <div className="container">
        <div className="card">
          <div className="header">
            <h1>🤖 BotDO</h1>
            <p className="subtitle">Slack & Whapi Integration Bot</p>
          </div>
          
          <div className="content">
            <div className="hello-section">
              <h2>Hello World from React! 👋</h2>
              <p>Frontend is running successfully</p>
            </div>

            <div className="divider"></div>

            <div className="backend-section">
              <h3>Backend Connection</h3>
              <div className={`status-badge ${backendStatus}`}>
                {backendStatus === 'connected' && '✓ Connected'}
                {backendStatus === 'checking' && '⏳ Checking...'}
                {backendStatus === 'error' && '✗ Error'}
              </div>
              <p className="backend-message">{backendMessage}</p>
              {error && <p className="error-message">Error: {error}</p>}
            </div>

            <div className="divider"></div>

            <div className="features">
              <h3>Planned Features</h3>
              <ul>
                <li>📨 Send messages to Slack</li>
                <li>📥 Receive messages from Slack</li>
                <li>📨 Send messages to Whapi</li>
                <li>📥 Receive messages from Whapi</li>
                <li>🔗 Integration with Digital Ocean Agent</li>
              </ul>
            </div>
          </div>

          <div className="footer">
            <p>Ready for development</p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;

