import React from 'react';
import { FolderIcon, ServerIcon, CodeBracketIcon, DocumentTextIcon } from '@heroicons/react/24/outline';

export type Section = 'projects' | 'server' | 'routes' | 'logs';

interface LayoutProps {
  children: React.ReactNode;
  activeSection: Section;
  onSectionChange: (section: Section) => void;
}

const Layout: React.FC<LayoutProps> = ({ children, activeSection, onSectionChange }) => {
  return (
    <div className="dashboard-root">
      {/* Sidebar */}
      <div className="sidebar">
        <div className="sidebar-inner">
          <div className="sidebar-header">
            <h1 className="dashboard-title">V1 MVC Dashboard</h1>
          </div>
          <nav className="sidebar-nav">
            <button
              className={`sidebar-btn${activeSection === 'projects' ? ' sidebar-btn-active' : ''}`}
              onClick={() => onSectionChange('projects')}
            >
              <FolderIcon className="sidebar-icon" />
              <div className="sidebar-btn-text">
                Projects
              </div>
            </button>
            <button
              className={`sidebar-btn${activeSection === 'server' ? ' sidebar-btn-active' : ''}`}
              onClick={() => onSectionChange('server')}
            >
              <ServerIcon className="sidebar-icon" />
              <div className="sidebar-btn-text">
                Server
              </div>
            </button>
            <button
              className={`sidebar-btn${activeSection === 'routes' ? ' sidebar-btn-active' : ''}`}
              onClick={() => onSectionChange('routes')}
            >
              <CodeBracketIcon className="sidebar-icon" />
              <div className="sidebar-btn-text">
                Routes
              </div>
            </button>
            <button
              className={`sidebar-btn${activeSection === 'logs' ? ' sidebar-btn-active' : ''}`}
              onClick={() => onSectionChange('logs')}
            >
              <DocumentTextIcon className="sidebar-icon" />
              <div className="sidebar-btn-text">
                Logs
              </div>
            </button>
          </nav>
        </div>
      </div>

      {/* Main content */}
      <div className="main-content">
        <main className="main-inner">
          <div className="main-children">
            {children}
          </div>
        </main>
      </div>
    </div>
  );
};

export default Layout; 