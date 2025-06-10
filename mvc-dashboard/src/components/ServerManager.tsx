import React, { useState } from 'react';
import { ServerStatus } from '../types';
import { PlayIcon, StopIcon, ArrowPathIcon } from '@heroicons/react/24/outline';

interface ServerManagerProps {
  status: ServerStatus;
  onStart: () => Promise<void>;
  onStop: () => Promise<void>;
  onRestart: () => Promise<void>;
}

const ServerManager: React.FC<ServerManagerProps> = ({
  status,
  onStart,
  onStop,
  onRestart,
}) => {
  const [isLoading, setIsLoading] = useState(false);

  const handleAction = async (action: () => Promise<void>) => {
    setIsLoading(true);
    try {
      await action();
    } catch (error) {
      console.error('Error performing server action:', error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="servermanager-root">
      <div className="servermanager-header">Server Management</div>
      <div className="servermanager-body">
        <div className="servermanager-status-row">
          <div>
            <div className="servermanager-status-indicator-row">
              <div
                className={`servermanager-status-dot ${status.isRunning ? 'servermanager-status-dot-running' : 'servermanager-status-dot-stopped'}`}
              />
              <span className="servermanager-status-label">
                {status.isRunning ? 'Running' : 'Stopped'}
              </span>
            </div>
            {status.port && (
              <div className="servermanager-port">
                Port: {status.port}
              </div>
            )}
          </div>
          <div className="servermanager-actions">
            {!status.isRunning ? (
              <button
                className="servermanager-btn servermanager-btn-start"
                onClick={() => handleAction(onStart)}
                disabled={isLoading}
              >
                <PlayIcon className="servermanager-btn-icon" />
                Start
              </button>
            ) : (
              <>
                <button
                  className="servermanager-btn servermanager-btn-stop"
                  onClick={() => handleAction(onStop)}
                  disabled={isLoading}
                >
                  <StopIcon className="servermanager-btn-icon" />
                  Stop
                </button>
                <button
                  className="servermanager-btn servermanager-btn-restart"
                  onClick={() => handleAction(onRestart)}
                  disabled={isLoading}
                >
                  <ArrowPathIcon className="servermanager-btn-icon" />
                  Restart
                </button>
              </>
            )}
          </div>
        </div>

        {/* Server Logs */}
        {/* The logs display has been moved to a dedicated 'Logs' section in App.tsx */}
      </div>
    </div>
  );
};

export default ServerManager; 