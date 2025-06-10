import React, { useState } from 'react';
import { Route, HttpRequest, HttpResponse } from '../types';

interface RouteDashboardProps {
  routes: Route[];
  onTestRoute: (request: HttpRequest) => Promise<HttpResponse>;
  onRefreshRoutes: () => void;
}

const RouteDashboard: React.FC<RouteDashboardProps> = ({ routes, onTestRoute, onRefreshRoutes }) => {
  const [selectedRoute, setSelectedRoute] = useState<Route | null>(null);
  const [requestBody, setRequestBody] = useState('');
  const [response, setResponse] = useState<HttpResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isValidJson, setIsValidJson] = useState(true);

  const handleEditorChange = (value: string | undefined) => {
    const newContent = value || '';
    setRequestBody(newContent);
    try {
      if (newContent.trim() === '') {
        setIsValidJson(true);
      } else {
        JSON.parse(newContent);
        setIsValidJson(true);
      }
    } catch (e) {
      setIsValidJson(false);
    }
  };

  const handleTestRoute = async () => {
    if (!selectedRoute || !isValidJson) return;

    setIsLoading(true);
    try {
      const requestHeaders: Record<string, string> = {};
      if (selectedRoute.method === 'POST' || selectedRoute.method === 'PUT') {
        requestHeaders['Content-Type'] = 'application/json';
      }

      const request: HttpRequest = {
        method: selectedRoute.method as 'GET' | 'POST' | 'PUT' | 'DELETE',
        path: selectedRoute.path,
        headers: requestHeaders,
        body: requestBody ? JSON.parse(requestBody) : undefined,
      };

      const result = await onTestRoute(request);
      setResponse(result);
    } catch (error) {
      console.error('Error testing route:', error);
      setResponse({
        status: 500,
        headers: {},
        body: { error: 'Failed to test route' },
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleOpenInNewTab = () => {
    if (selectedRoute) {
      if (selectedRoute.method === 'GET') {
        window.open(`http://localhost:8080${selectedRoute?.path}`, '_blank');
      } else {
        alert('Opening in a new tab is only supported for GET requests.');
      }
    }
  };

  return (
    <div className="routedashboard-root">
      <div className="routedashboard-header">Routes</div>
      <div className="routedashboard-body">
        <div className="routedashboard-grid">
          {/* Routes List */}
          <div className="routedashboard-list-section">
            <div className="routedashboard-list-title">
              Available Routes
              <button className="routedashboard-refresh-btn" onClick={onRefreshRoutes}>
                Refresh
              </button>
            </div>
            <div className="routedashboard-list">
              {routes.map((route) => (
                <div
                  key={`${route.method}-${route.path}`}
                  className={`routedashboard-list-item${selectedRoute === route ? ' routedashboard-list-item-active' : ''}`}
                  onClick={() => setSelectedRoute(route)}
                >
                  <div className="routedashboard-list-item-row">
                    <span className="routedashboard-list-path">{route.path}</span>
                    <span className="routedashboard-list-method">{route.method}</span>
                  </div>
                  <div className="routedashboard-list-meta">
                    {route.controller}.{route.action}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Route Testing */}
          <div className="routedashboard-test-section">
            <div className="routedashboard-test-title">Test Route</div>
            {selectedRoute ? (
              <div className="routedashboard-test-form">
                <div>
                  <label className="routedashboard-test-label">Request Body (JSON)</label>
                  <textarea
                    className={`routedashboard-test-textarea ${!isValidJson ? 'is-invalid' : ''}`}
                    rows={4}
                    value={requestBody}
                    onChange={(e) => handleEditorChange(e.target.value)}
                    placeholder="Enter JSON request body..."
                  />
                  {!isValidJson && (
                    <p className="routedashboard-json-error">Invalid JSON format. Please correct it.</p>
                  )}
                </div>
                <button
                  className="routedashboard-test-btn"
                  onClick={handleTestRoute}
                  disabled={isLoading || !isValidJson}
                >
                  {isLoading ? 'Testing...' : 'Test Route'}
                </button>

                {response && (
                  <div className="routedashboard-response-section">
                    <div className="routedashboard-response-title">Response</div>
                    <div className="routedashboard-response-box">
                      <div className="routedashboard-response-status">Status: {response.status}</div>
                      {response.contentType?.includes('text/html') ? (
                        response.viewOutput && (
                          <div className="routedashboard-response-view">
                            <div className="routedashboard-response-view-title">
                              View Output:
                              <button
                                className="routedashboard-open-new-tab-btn"
                                onClick={handleOpenInNewTab}
                              >
                                Open in New Tab
                              </button>
                            </div>
                            <div
                              className="routedashboard-response-view-box"
                              dangerouslySetInnerHTML={{ __html: response.viewOutput }}
                            />
                          </div>
                        )
                      ) : (
                        <pre className="routedashboard-response-body">
                          {typeof response.body === 'object' ? JSON.stringify(response.body, null, 2) : response.body}
                        </pre>
                      )}
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <div className="routedashboard-test-placeholder">Select a route to test</div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default RouteDashboard; 