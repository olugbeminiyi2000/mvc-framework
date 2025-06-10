import React, { useState } from 'react';
import { WebApp } from '../types';

interface WebAppSelectorProps {
  webApps: WebApp[];
  selectedWebApp: WebApp | null;
  onSelectWebApp: (webApp: WebApp) => void;
  onCreateWebApp?: (name: string) => void;
}

const WebAppSelector: React.FC<WebAppSelectorProps> = ({ webApps, selectedWebApp, onSelectWebApp, onCreateWebApp }) => {
  const [newWebAppName, setNewWebAppName] = useState('');
  const [showInput, setShowInput] = useState(false);

  const handleCreate = () => {
    if (newWebAppName.trim() && onCreateWebApp) {
      onCreateWebApp(newWebAppName.trim());
      setNewWebAppName('');
      setShowInput(false);
    }
  };

  return (
    <div className="webappselector-root">
      <label className="webappselector-label">Select Project:</label>
      <select
        className="webappselector-dropdown"
        value={selectedWebApp ? selectedWebApp.name : ''}
        onChange={e => {
          const found = webApps.find(w => w.name === e.target.value);
          if (found) onSelectWebApp(found);
        }}
      >
        <option value="" disabled>Select a project...</option>
        {webApps.map(app => (
          <option key={app.name} value={app.name}>{app.name}</option>
        ))}
      </select>
      {onCreateWebApp && (
        <div className="webappselector-create">
          {showInput ? (
            <>
              <input
                className="webappselector-input"
                type="text"
                placeholder="New project name"
                value={newWebAppName}
                onChange={e => setNewWebAppName(e.target.value)}
                onKeyDown={e => { if (e.key === 'Enter') handleCreate(); }}
              />
              <button className="webappselector-btn" onClick={handleCreate}>Create</button>
              <button className="webappselector-btn-cancel" onClick={() => setShowInput(false)}>Cancel</button>
            </>
          ) : (
            <button className="webappselector-btn" onClick={() => setShowInput(true)}>+ New Project</button>
          )}
        </div>
      )}
    </div>
  );
};

export default WebAppSelector; 