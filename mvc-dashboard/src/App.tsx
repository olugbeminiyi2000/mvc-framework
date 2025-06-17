import React, { useState, useEffect, useCallback } from 'react';
import Layout, { Section } from './components/Layout';
import WebAppSelector from './components/WebAppSelector';
import FileTree from './components/FileTree';
import CodeEditor from './components/CodeEditor';
import RouteDashboard from './components/RouteDashboard';
import ServerManager from './components/ServerManager';
import Joyride, { CallBackProps, STATUS, Step } from 'react-joyride';
import { WebApp, FileInfo, Route, ServerStatus, HttpRequest, HttpResponse } from './types';
import { mvcService } from './services/mvcService';
import { InformationCircleIcon, CheckCircleIcon, ExclamationCircleIcon, QuestionMarkCircleIcon } from '@heroicons/react/24/outline';

const REQUIRED_FILES = ['__init__.py', 'model.py', 'view.py', 'controller.py', 'router.py'];

const App: React.FC = () => {
  const [webApps, setWebApps] = useState<WebApp[]>([]);
  const [selectedWebApp, setSelectedWebApp] = useState<WebApp | null>(null);
  const [selectedFile, setSelectedFile] = useState<FileInfo | null>(null);
  const [routes, setRoutes] = useState<Route[]>([]);
  const [serverStatus, setServerStatus] = useState<ServerStatus>({
    isRunning: false,
    logs: [],
  });
  const [activeSection, setActiveSection] = useState<Section>('projects');
  const [showTooltip, setShowTooltip] = useState(false);
  const [registrationMessage, setRegistrationMessage] = useState<string | null>(null);
  const [registrationError, setRegistrationError] = useState<string | null>(null);
  const [isRegistering, setIsRegistering] = useState(false);
  const [registrationSuccessIcon, setRegistrationSuccessIcon] = useState(false);
  const [registrationErrorIcon, setRegistrationErrorIcon] = useState(false);

  // Joyride Tour State
  const [runTour, setRunTour] = useState(false);
  const tourSteps: Step[] = [
    {
      target: '.sidebar-header',
      content: 'Welcome to the V1 Framework Dashboard! This tour will guide you through its main features.',
      disableBeacon: true,
      placement: 'right',
      title: 'Welcome!',
    },
    {
      target: '.webappselector-root',
      content: 'Here you can select an existing web application or create a new one.',
      placement: 'bottom',
    },
    {
      target: '.sidebar-btn:nth-child(1)',
      content: 'Use these sidebar links to navigate between different sections of the dashboard.',
      placement: 'right',
      title: 'Navigation',
    },
    {
      target: '#webapp-select',
      content: 'Select an existing project from this dropdown.',
      placement: 'bottom',
    },
    {
      target: '.webappselector-create',
      content: 'Or create a brand new project here.',
      placement: 'bottom',
    },
    {
      target: '.filetree-info-compact',
      content: 'This section shows your project\'s files. Required MVC files are highlighted.',
      placement: 'left',
      title: 'Project Files',
    },
    {
      target: '.sidebar-btn:nth-child(2)',
      content: 'Manage your MVC server (start, stop, restart) and view its status here.',
      placement: 'right',
      title: 'Server Management',
    },
    {
      target: '.sidebar-btn:nth-child(3)',
      content: 'View and test all registered routes for your selected web app.',
      placement: 'right',
      title: 'Routes Dashboard',
    },
    {
      target: '.sidebar-btn:nth-child(4)',
      content: 'Monitor all real-time logs from your Flask backend and MVC server subprocess here.',
      placement: 'right',
      title: 'Server Logs',
    },
    {
      target: '.routedashboard-test-section',
      content: 'This is where you can test your registered routes by sending HTTP requests and viewing the responses.',
      placement: 'top',
      title: 'Test Your Routes',
    },
    {
      target: '.server-logs-container',
      content: 'All server and application logs will appear here in real-time, helping you debug your application.',
      placement: 'top',
      title: 'Real-time Logs',
    },
  ];

  useEffect(() => {
    const hasVisitedBefore = localStorage.getItem('hasVisitedDashboard');
    if (!hasVisitedBefore) {
      setRunTour(true);
      localStorage.setItem('hasVisitedDashboard', 'true');
    }
  }, []);

  const handleJoyrideCallback = (data: CallBackProps) => {
    const { status } = data;
    const finishedStatuses: string[] = [STATUS.FINISHED, STATUS.SKIPPED];

    if (finishedStatuses.includes(status)) {
      setRunTour(false);
    }
  };

  useEffect(() => {
    const loadWebApps = async () => {
      try {
        const apps = await mvcService.getWebApps();
        setWebApps(apps);
        if (apps.length > 0) {
          setSelectedWebApp(apps[0]);
        } else {
          setSelectedWebApp(null);
        }
      } catch (error) {
        console.error('Error loading web apps:', error);
      }
    };
    loadWebApps();
  }, []);

  const loadRoutes = useCallback(async () => {
    if (selectedWebApp) {
      try {
        const appRoutes = await mvcService.getRoutes(selectedWebApp.name);
        setRoutes(appRoutes);
      } catch (error) {
        console.error('Error loading routes:', error);
      }
    } else {
      setRoutes([]);
    }
  }, [selectedWebApp]);

  useEffect(() => {
    loadRoutes();
    setSelectedFile(null);
  }, [selectedWebApp, loadRoutes]);

  const handleRefreshRoutes = () => {
    loadRoutes();
  };

  const handleRegisterRoutes = async () => {
    if (!selectedWebApp) {
      setRegistrationError('Please select a web application first.');
      setRegistrationMessage(null);
      setRegistrationSuccessIcon(false);
      setRegistrationErrorIcon(false);
      return;
    }

    setRegistrationMessage(null);
    setRegistrationError(null);
    setIsRegistering(true);
    setRegistrationSuccessIcon(false);
    setRegistrationErrorIcon(false);

    try {
      const result = await mvcService.registerRoutes(selectedWebApp.name);
      if (result.success) {
        setRegistrationMessage(result.message);
        setRegistrationSuccessIcon(true);
        loadRoutes();
      } else {
        setRegistrationError(result.message);
        setRegistrationErrorIcon(true);
      }
    } catch (error: any) {
      setRegistrationError(`Failed to register routes: ${error.message || 'Unknown error'}`);
      setRegistrationErrorIcon(true);
    } finally {
      setTimeout(() => {
        setRegistrationMessage(null);
        setRegistrationError(null);
        setRegistrationSuccessIcon(false);
        setRegistrationErrorIcon(false);
        setIsRegistering(false);
      }, 5000);
    }
  };

  const handleFileSelect = async (file: FileInfo) => {
    if (!selectedWebApp) return;
    try {
      const content = await mvcService.getFileContent(selectedWebApp.name, file.path);
      setSelectedFile({ ...file, content });
    } catch (error) {
      console.error('Error loading file content:', error);
    }
  };

  const handleFileChange = async (content: string) => {
    if (!selectedFile || !selectedWebApp) return;
    try {
      await mvcService.saveFileContent(selectedWebApp.name, selectedFile.path, content);
      setSelectedFile({ ...selectedFile, content });
    } catch (error) {
      console.error('Error saving file:', error);
    }
  };

  const handleTestRoute = async (request: HttpRequest): Promise<HttpResponse> => {
    if (!selectedWebApp) {
      throw new Error('No web app selected');
    }
    return mvcService.testRoute(selectedWebApp.name, request);
  };

  const handleStartServer = async () => {
    if (!selectedWebApp) return;
    try {
      await mvcService.startServer(selectedWebApp.name);
      const status = await mvcService.getServerStatus(selectedWebApp.name);
      setServerStatus(status);
    } catch (error) {
      console.error('Error starting server:', error);
    }
  };

  const handleStopServer = async () => {
    if (!selectedWebApp) return;
    try {
      await mvcService.stopServer(selectedWebApp.name);
      const status = await mvcService.getServerStatus(selectedWebApp.name);
      setServerStatus(status);
    } catch (error) {
      console.error('Error stopping server:', error);
    }
  };

  const handleRestartServer = async () => {
    if (!selectedWebApp) return;
    try {
      setServerStatus({
        isRunning: false,
        logs: ['Restarting...'],
        port: serverStatus.port,
        pid: serverStatus.pid,
      });

      await mvcService.restartServer(selectedWebApp.name);

      setTimeout(async () => {
        const status = await mvcService.getServerStatus(selectedWebApp.name);
        setServerStatus(status);
      }, 2000);

    } catch (error) {
      console.error('Error restarting server:', error);
      setServerStatus({
        isRunning: false,
        logs: serverStatus.logs.concat([`Error during restart: ${(error as any)?.message || 'Unknown error'}`]),
        port: serverStatus.port,
        pid: serverStatus.pid,
      });
    }
  };

  const handleCreateWebApp = async (name: string) => {
    try {
      const newApp = await mvcService.createWebApp(name);
      const apps = await mvcService.getWebApps();
      setWebApps(apps);
      setSelectedWebApp(newApp);
    } catch (error) {
      alert('Failed to create project: ' + (error as any)?.message);
    }
  };

  const allFiles = selectedWebApp
    ? [
      ...selectedWebApp.models,
      ...selectedWebApp.views,
      ...selectedWebApp.controllers,
      ...(selectedWebApp.router ? [selectedWebApp.router] : []),
      ...(selectedWebApp.init ? [selectedWebApp.init] : []),
    ]
    : [];
  const presentFileNames = allFiles.map(f => f.name);
  const missingFiles = REQUIRED_FILES.filter(f => !presentFileNames.includes(f));

  return (
    <Layout activeSection={activeSection} onSectionChange={setActiveSection}>
      <>
        <Joyride
          run={runTour}
          steps={tourSteps}
          continuous
          showProgress
          showSkipButton
          callback={handleJoyrideCallback}
          styles={{
            options: {
              zIndex: 10000,
              primaryColor: '#22c55e', // green-500
              backgroundColor: '#ffffff',
              textColor: '#1f2937', // gray-800
              arrowColor: '#ffffff',
              fontFamily: 'ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace',
            },
            tooltip: {
              fontFamily: 'ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace',
            },
            buttonNext: {
              backgroundColor: '#22c55e', // green-500
              color: '#ffffff',
              fontFamily: 'ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace',
            },
            buttonBack: {
              color: '#22c55e', // green-500
              fontFamily: 'ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace',
            },
            buttonSkip: {
              color: '#22c55e', // green-500
              fontFamily: 'ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace',
            },
            buttonClose: {
              color: '#22c55e', // green-500
              fontFamily: 'ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace',
            },
          }}
          locale={{
            back: 'Back',
            close: 'Close',
            last: 'Finish',
            next: 'Next',
            skip: 'Skip',
          }}
        />
        <WebAppSelector
          webApps={webApps}
          selectedWebApp={selectedWebApp}
          onSelectWebApp={setSelectedWebApp}
          onCreateWebApp={handleCreateWebApp}
        />
        <div style={{ position: 'absolute', top: '1rem', right: '1rem' }}>
          <button
            className="flex items-center text-gray-600 hover:text-blue-500 transition-colors"
            onClick={() => setRunTour(true)}
            title="Start Tour"
          >
            <QuestionMarkCircleIcon className="w-6 h-6 mr-1" />
            <span className="text-sm">Start Tour</span>
          </button>
        </div>
        {selectedWebApp ? (
          <>
            {activeSection === 'projects' && (
              <>
                <div className="filetree-info-compact">
                  <span
                    className="filetree-info-icon-compact"
                    onMouseEnter={() => setShowTooltip(true)}
                    onMouseLeave={() => setShowTooltip(false)}
                  >
                    <InformationCircleIcon />
                  </span>
                  <span>Required files for playground,</span>
                  {selectedFile ? (
                    <CodeEditor
                      file={selectedFile}
                      onChange={handleFileChange}
                      onClose={() => setSelectedFile(null)}
                    />
                  ) : (
                    <div className="bg-white rounded-lg shadow p-4">
                      <p className="text-gray-500">select a file to edit</p>
                    </div>
                  )}
                  {showTooltip && (
                    <div className="filetree-tooltip">
                      <b>Required files:</b> <br />
                      __init__.py, model.py, view.py, controller.py, router.py<br />
                      <span style={{ fontSize: '0.95em' }}>These must be spelled exactly for the playground to recognize them.</span>
                    </div>
                  )}
                </div>
                <FileTree
                  files={allFiles}
                  onFileSelect={handleFileSelect}
                  requiredFiles={REQUIRED_FILES}
                  missingFiles={missingFiles}
                />
                <div className="project-actions" style={{ marginTop: '1rem', display: 'flex', gap: '1rem', alignItems: 'center' }}>
                  {!isRegistering && !registrationSuccessIcon && !registrationErrorIcon && (
                    <button className="btn-primary" onClick={handleRegisterRoutes}>
                      Register Routes
                    </button>
                  )}
                  {isRegistering && !registrationSuccessIcon && !registrationErrorIcon && (
                    <button className="btn-primary" disabled>
                      Registering...
                    </button>
                  )}
                  {registrationSuccessIcon && (
                    <CheckCircleIcon className="text-green-500" style={{ width: '24px', height: '24px', color: '#28a745' }} />
                  )}
                  {registrationErrorIcon && (
                    <ExclamationCircleIcon className="text-red-500" style={{ width: '24px', height: '24px', color: '#dc3545' }} />
                  )}
                  {registrationMessage && <p className="message-success">{registrationMessage}</p>}
                  {registrationError && <p className="message-error">{registrationError}</p>}
                </div>

              </>
            )}
            {activeSection === 'routes' && (
              <RouteDashboard
                routes={routes}
                onTestRoute={handleTestRoute}
                onRefreshRoutes={handleRefreshRoutes}
              />
            )}
            {activeSection === 'server' && (
              <ServerManager
                status={serverStatus}
                onStart={handleStartServer}
                onStop={handleStopServer}
                onRestart={handleRestartServer}
              />
            )}
            {activeSection === 'logs' && (
              <div className="bg-white rounded-lg shadow p-4">
                <h2>Server Logs</h2>
                <div className="server-logs-container" style={{ maxHeight: '500px', overflowY: 'auto', backgroundColor: '#f8f8f8', padding: '10px', borderRadius: '5px' }}>
                  {serverStatus.logs.length > 0 ? (
                    <pre style={{ whiteSpace: 'pre-wrap', wordBreak: 'break-all' }}>
                      {serverStatus.logs.join('\n')}
                    </pre>
                  ) : (
                    <p style={{ color: '#888' }}>No logs available. Start the server and perform some actions to see logs here.</p>
                  )}
                </div>
              </div>
            )}
          </>
        ) : (
          <div className="bg-white rounded-lg shadow p-4">
            <p className="text-gray-500">No project selected. Please create or select a project to continue.</p>
    </div>
        )}
      </>
    </Layout>
  );
};

export default App;
