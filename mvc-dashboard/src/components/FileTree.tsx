import React, { useState } from 'react';
import { ChevronRightIcon, ChevronDownIcon, FolderIcon, DocumentIcon, ExclamationTriangleIcon } from '@heroicons/react/24/outline';
import { FileInfo } from '../types';

interface FileTreeProps {
  files: FileInfo[];
  onFileSelect: (file: FileInfo) => void;
  requiredFiles?: string[];
  missingFiles?: string[];
}

interface TreeNode {
  name: string;
  path: string;
  type: 'directory' | 'file';
  children?: TreeNode[];
}

const FileTree: React.FC<FileTreeProps> = ({ files, onFileSelect, requiredFiles = [], missingFiles = [] }) => {
  const [expandedDirs, setExpandedDirs] = useState<Set<string>>(new Set());

  const buildTree = (files: FileInfo[]): TreeNode[] => {
    const tree: TreeNode[] = [];
    const pathMap = new Map<string, TreeNode>();

    files.forEach(file => {
      const parts = file.path.split('/');
      let currentPath = '';
      
      parts.forEach((part, index) => {
        const parentPath = currentPath;
        currentPath = currentPath ? `${currentPath}/${part}` : part;
        
        if (!pathMap.has(currentPath)) {
          const node: TreeNode = {
            name: part,
            path: currentPath,
            type: index === parts.length - 1 ? 'file' : 'directory',
            children: index === parts.length - 1 ? undefined : []
          };
          
          pathMap.set(currentPath, node);
          
          if (parentPath) {
            const parent = pathMap.get(parentPath);
            if (parent && parent.children) {
              parent.children.push(node);
            }
          } else {
            tree.push(node);
          }
        }
      });
    });

    return tree;
  };

  const toggleDir = (path: string) => {
    setExpandedDirs(prev => {
      const next = new Set(prev);
      if (next.has(path)) {
        next.delete(path);
      } else {
        next.add(path);
      }
      return next;
    });
  };

  const isCoreFile = (filename: string) => requiredFiles.includes(filename);

  const renderNode = (node: TreeNode, level: number = 0) => {
    const isExpanded = expandedDirs.has(node.path);
    const paddingLeft = `${level * 1.5}rem`;

    if (node.type === 'directory') {
      return (
        <div key={node.path}>
          <div
            className="filetree-dir"
            style={{ paddingLeft }}
            onClick={() => toggleDir(node.path)}
          >
            {isExpanded ? (
              <ChevronDownIcon className="filetree-chevron" />
            ) : (
              <ChevronRightIcon className="filetree-chevron" />
            )}
            <FolderIcon className="filetree-folder" />
            <span className="filetree-dirname">{node.name}</span>
          </div>
          {isExpanded && node.children && (
            <div>
              {node.children.map(child => renderNode(child, level + 1))}
            </div>
          )}
        </div>
      );
    }

    return (
      <div
        key={node.path}
        className={`filetree-file${isCoreFile(node.name) ? ' filetree-corefile' : ''}`}
        style={{ paddingLeft }}
        onClick={() => onFileSelect(files.find(f => f.path === node.path)!)}
      >
        <DocumentIcon className="filetree-doc" />
        <span className="filetree-filename">{node.name}</span>
        {isCoreFile(node.name) && <span className="filetree-corefile-label">core</span>}
      </div>
    );
  };

  const tree = buildTree(files);

  return (
    <div className="filetree-root">
      <div className="filetree-header">Project Files</div>
      {missingFiles.length > 0 && (
        <div className="filetree-warning">
          <ExclamationTriangleIcon className="filetree-warning-icon" />
          <span>Missing required files: {missingFiles.join(', ')}</span>
        </div>
      )}
      <div className="filetree-list">
        {tree.map(node => renderNode(node))}
      </div>
    </div>
  );
};

export default FileTree; 