import React, { useState, useRef } from 'react';
import Editor from '@monaco-editor/react';
import { FileInfo } from '../types';
import { ArrowsRightLeftIcon, XMarkIcon, CheckIcon } from '@heroicons/react/24/outline';

interface CodeEditorProps {
  file: FileInfo;
  onChange: (content: string) => void;
  onClose?: () => void;
}

const CodeEditor: React.FC<CodeEditorProps> = ({ file, onChange, onClose }) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const [content, setContent] = useState(file.content);
  const [hasChanges, setHasChanges] = useState(false);
  const editorRef = useRef<any>(null);

  const getLanguage = (type: string) => {
    switch (type) {
      case 'model':
      case 'controller':
      case 'router':
      case 'view':
        return 'python';
      default:
        return 'plaintext';
    }
  };

  const handleEditorDidMount = (editor: any) => {
    editorRef.current = editor;
  };

  const handleEditorChange = (value: string | undefined) => {
    const newContent = value || '';
    setContent(newContent);
    setHasChanges(newContent !== file.content);
  };

  const handleSave = () => {
    onChange(content);
    setHasChanges(false);
  };

  const handleCancel = () => {
    setContent(file.content);
    setHasChanges(false);
    if (editorRef.current) {
      editorRef.current.setValue(file.content);
    }
  };

  return (
    <div className={`codeeditor-overlay ${isExpanded ? 'expanded' : ''}`}>
      <div className="codeeditor-root">
        <div className="codeeditor-header">
          <div className="codeeditor-title-section">
            <h2 className="codeeditor-title">{file.name}</h2>
            <p className="codeeditor-path">{file.path}</p>
          </div>
          <div className="codeeditor-actions">
            {hasChanges && (
              <>
                <button 
                  className="codeeditor-button save"
                  onClick={handleSave}
                  title="Save changes"
                >
                  <CheckIcon className="codeeditor-icon" />
                  Save
                </button>
                <button 
                  className="codeeditor-button cancel"
                  onClick={handleCancel}
                  title="Discard changes"
                >
                  <XMarkIcon className="codeeditor-icon" />
                  Cancel
                </button>
              </>
            )}
            <button 
              className="codeeditor-button expand"
              onClick={() => setIsExpanded(!isExpanded)}
              title={isExpanded ? "Collapse editor" : "Expand editor"}
            >
              <ArrowsRightLeftIcon className="codeeditor-icon" />
            </button>
            {onClose && (
              <button 
                className="codeeditor-button close"
                onClick={onClose}
                title="Close editor"
              >
                <XMarkIcon className="codeeditor-icon" />
              </button>
            )}
          </div>
        </div>
        <div className="codeeditor-editor">
          <Editor
            height="100%"
            defaultLanguage={getLanguage(file.type)}
            defaultValue={file.content}
            theme="vs-dark"
            onChange={handleEditorChange}
            onMount={handleEditorDidMount}
            options={{
              minimap: { enabled: false },
              fontSize: 14,
              wordWrap: 'on',
              automaticLayout: true,
              scrollBeyondLastLine: false,
              lineNumbers: 'on',
              renderWhitespace: 'selection',
              tabSize: 2,
            }}
          />
        </div>
      </div>
    </div>
  );
};

export default CodeEditor; 