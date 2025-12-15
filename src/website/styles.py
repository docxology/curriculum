"""CSS styles for website generation.

This module provides the embedded CSS styles for the course website,
including responsive design, dark mode, and print styles.
"""


def get_css() -> str:
    """Get embedded CSS styles.
    
    Returns:
        CSS string with all styles for the website
    """
    return """        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        :root {
            --primary-color: #667eea;
            --secondary-color: #764ba2;
            --text-color: #333;
            --bg-color: #f5f5f5;
            --content-bg: #ffffff;
            --border-color: #ddd;
            --hover-bg: #f0f0f0;
        }
        
        [data-theme="dark"] {
            --text-color: #e0e0e0;
            --bg-color: #1a1a1a;
            --content-bg: #2d2d2d;
            --border-color: #444;
            --hover-bg: #3a3a3a;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: var(--text-color);
            background-color: var(--bg-color);
            transition: background-color 0.3s, color 0.3s;
        }
        
        .skip-link {
            position: absolute;
            top: -40px;
            left: 0;
            background: var(--primary-color);
            color: white;
            padding: 8px;
            text-decoration: none;
            z-index: 100;
        }
        
        .skip-link:focus {
            top: 0;
        }
        
        header {
            background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
            color: white;
            padding: 2rem;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        .header-content {
            max-width: 1200px;
            margin: 0 auto;
        }
        
        .header-top {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 1rem;
        }
        
        .header-controls {
            display: flex;
            gap: 0.5rem;
            align-items: center;
        }
        
        .search-container {
            position: relative;
        }
        
        .search-input {
            padding: 0.5rem 1rem;
            border: 1px solid rgba(255,255,255,0.3);
            border-radius: 4px;
            background: rgba(255,255,255,0.2);
            color: white;
            width: 200px;
            font-size: 0.9rem;
        }
        
        .search-input::placeholder {
            color: rgba(255,255,255,0.7);
        }
        
        .search-button, .dark-mode-toggle, .print-button {
            background: rgba(255,255,255,0.2);
            border: 1px solid rgba(255,255,255,0.3);
            color: white;
            padding: 0.5rem;
            border-radius: 4px;
            cursor: pointer;
            font-size: 1.2rem;
            transition: background 0.2s;
        }
        
        .search-button:hover, .dark-mode-toggle:hover, .print-button:hover {
            background: rgba(255,255,255,0.3);
        }
        
        .search-results {
            position: absolute;
            top: 100%;
            left: 0;
            right: 0;
            background: white;
            border: 1px solid var(--border-color);
            border-radius: 4px;
            margin-top: 0.5rem;
            max-height: 400px;
            overflow-y: auto;
            display: none;
            z-index: 1000;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        
        .search-results.active {
            display: block;
        }
        
        .search-result-item {
            padding: 0.75rem;
            border-bottom: 1px solid #eee;
            cursor: pointer;
        }
        
        .search-result-item:hover {
            background: var(--hover-bg);
        }
        
        .search-highlight {
            background: yellow;
            font-weight: bold;
        }
        
        header h1 {
            font-size: 2.5rem;
            margin-bottom: 0.5rem;
        }
        
        .course-level {
            font-size: 1.2rem;
            opacity: 0.9;
            margin-bottom: 0.5rem;
        }
        
        .course-description {
            font-size: 1rem;
            opacity: 0.85;
        }
        
        .container {
            display: flex;
            max-width: 1400px;
            margin: 0 auto;
            min-height: calc(100vh - 200px);
        }
        
        .sidebar {
            width: 300px;
            background: white;
            border-right: 1px solid #ddd;
            overflow-y: auto;
            height: calc(100vh - 200px);
            position: sticky;
            top: 0;
        }
        
        .nav-header {
            padding: 1rem;
            border-bottom: 1px solid #eee;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .nav-header h2 {
            font-size: 1.2rem;
            color: #333;
        }
        
        .nav-toggle {
            background: none;
            border: none;
            font-size: 1.5rem;
            cursor: pointer;
            padding: 0.5rem;
            display: none;
        }
        
        .module-list, .session-list, .content-list {
            list-style: none;
        }
        
        .module-button, .session-button, .content-button {
            width: 100%;
            text-align: left;
            padding: 0.75rem 1rem;
            border: none;
            background: none;
            cursor: pointer;
            font-size: 1rem;
            color: #333;
            display: flex;
            justify-content: space-between;
            align-items: center;
            transition: background-color 0.2s;
        }
        
        .module-button:hover, .session-button:hover, .content-button:hover {
            background-color: #f0f0f0;
        }
        
        .module-button {
            font-weight: 600;
            border-bottom: 1px solid #eee;
        }
        
        .session-button {
            padding-left: 2rem;
            font-weight: 500;
        }
        
        .content-button {
            padding-left: 3rem;
            font-size: 0.9rem;
            color: #666;
        }
        
        .content-button.active {
            background-color: #e3f2fd;
            color: #1976d2;
        }
        
        .expand-icon {
            transition: transform 0.2s;
            font-size: 0.8rem;
        }
        
        .module-button[aria-expanded="true"] .expand-icon,
        .session-button[aria-expanded="true"] .expand-icon {
            transform: rotate(180deg);
        }
        
        .content {
            flex: 1;
            padding: 2rem;
            background: white;
            margin: 2rem;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        .welcome-screen {
            text-align: center;
            padding: 4rem 2rem;
        }
        
        .welcome-screen h2 {
            font-size: 2rem;
            margin-bottom: 1rem;
            color: #667eea;
        }
        
        .metadata {
            color: #666;
            font-size: 0.9rem;
            margin-top: 2rem;
        }
        
        .content-view {
            animation: fadeIn 0.3s;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }
        
        .content-header {
            margin-bottom: 2rem;
            padding-bottom: 1rem;
            border-bottom: 2px solid var(--border-color);
        }
        
        .breadcrumbs {
            margin: 0.5rem 0;
            font-size: 0.9rem;
        }
        
        .breadcrumbs a {
            color: var(--primary-color);
            text-decoration: none;
        }
        
        .breadcrumbs a:hover {
            text-decoration: underline;
        }
        
        .breadcrumbs span {
            margin: 0 0.5rem;
            color: #999;
        }
        
        .content-actions {
            display: flex;
            gap: 0.5rem;
            margin-top: 1rem;
        }
        
        .toc-toggle, .print-button {
            background: var(--primary-color);
            color: white;
            border: none;
            padding: 0.5rem 1rem;
            border-radius: 4px;
            cursor: pointer;
            font-size: 0.9rem;
            transition: background-color 0.2s;
        }
        
        .toc-toggle:hover {
            background: #5568d3;
        }
        
        .content-wrapper {
            display: flex;
            gap: 2rem;
        }
        
        .table-of-contents {
            width: 250px;
            background: var(--content-bg);
            padding: 1.5rem;
            border-radius: 8px;
            border: 1px solid var(--border-color);
            position: sticky;
            top: 2rem;
            max-height: calc(100vh - 4rem);
            overflow-y: auto;
        }
        
        .table-of-contents h3 {
            font-size: 1.2rem;
            margin-bottom: 1rem;
            color: var(--text-color);
        }
        
        .table-of-contents ul {
            list-style: none;
            margin-left: 0;
        }
        
        .table-of-contents li {
            margin-bottom: 0.5rem;
        }
        
        .table-of-contents a {
            color: var(--primary-color);
            text-decoration: none;
            font-size: 0.9rem;
        }
        
        .table-of-contents a:hover {
            text-decoration: underline;
        }
        
        .table-of-contents li.level-2 {
            padding-left: 1rem;
        }
        
        .table-of-contents li.level-3 {
            padding-left: 2rem;
        }
        
        .progress-indicator {
            margin-top: 2rem;
            padding: 1rem;
            background: var(--content-bg);
            border-radius: 4px;
            border: 1px solid var(--border-color);
        }
        
        .progress-bar {
            width: 100%;
            height: 8px;
            background: #eee;
            border-radius: 4px;
            overflow: hidden;
            margin-top: 0.5rem;
        }
        
        .progress-fill {
            height: 100%;
            background: var(--primary-color);
            transition: width 0.3s;
        }
        
        .loading-spinner {
            border: 3px solid #f3f3f3;
            border-top: 3px solid var(--primary-color);
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 2rem auto;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .back-button {
            background: var(--primary-color);
            color: white;
            border: none;
            padding: 0.5rem 1rem;
            border-radius: 4px;
            cursor: pointer;
            font-size: 0.9rem;
            margin-bottom: 1rem;
            transition: background-color 0.2s;
        }
        
        .back-button:hover {
            background: #5568d3;
        }
        
        .content-header h2 {
            font-size: 1.8rem;
            color: var(--text-color);
            margin-top: 0.5rem;
        }
        
        .content-body {
            line-height: 1.8;
            flex: 1;
            background: var(--content-bg);
            padding: 2rem;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        .content-body h1, .content-body h2, .content-body h3, .content-body h4, .content-body h5, .content-body h6 {
            margin-top: 2rem;
            margin-bottom: 1rem;
            color: var(--text-color);
            scroll-margin-top: 2rem;
        }
        
        .content-body h1 {
            font-size: 2rem;
            border-bottom: 2px solid var(--primary-color);
            padding-bottom: 0.5rem;
        }
        
        .content-body h2 {
            font-size: 1.5rem;
        }
        
        .content-body h3 {
            font-size: 1.2rem;
        }
        
        .content-body p {
            margin-bottom: 1rem;
        }
        
        .content-body ul, .content-body ol {
            margin-left: 2rem;
            margin-bottom: 1rem;
        }
        
        .content-body code {
            background: #f4f4f4;
            padding: 0.2rem 0.4rem;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
            font-size: 0.9em;
        }
        
        [data-theme="dark"] .content-body code {
            background: #1a1a1a;
            color: #e0e0e0;
        }
        
        .content-body pre {
            background: #f4f4f4;
            padding: 1rem;
            border-radius: 4px;
            overflow-x: auto;
            margin-bottom: 1rem;
            position: relative;
        }
        
        [data-theme="dark"] .content-body pre {
            background: #1a1a1a;
        }
        
        .copy-code-button {
            position: absolute;
            top: 0.5rem;
            right: 0.5rem;
            background: var(--primary-color);
            color: white;
            border: none;
            padding: 0.25rem 0.5rem;
            border-radius: 4px;
            cursor: pointer;
            font-size: 0.8rem;
        }
        
        .content-body pre code {
            background: none;
            padding: 0;
        }
        
        .content-body table {
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 1rem;
        }
        
        .content-body table th,
        .content-body table td {
            padding: 0.75rem;
            border: 1px solid #ddd;
            text-align: left;
        }
        
        .content-body table th {
            background: #f4f4f4;
            font-weight: 600;
        }
        
        .mermaid {
            margin: 2rem 0;
            text-align: center;
        }
        
        footer {
            background: #333;
            color: white;
            text-align: center;
            padding: 1.5rem;
            margin-top: 2rem;
        }
        
        .session-viewed {
            position: relative;
        }
        
        .session-viewed::before {
            content: "✓";
            position: absolute;
            left: -1.5rem;
            color: var(--primary-color);
            font-weight: bold;
        }
        
        @media print {
            .sidebar, .header-controls, .back-button, .toc-toggle, .table-of-contents, .progress-indicator, footer {
                display: none !important;
            }
            
            .content-wrapper {
                display: block;
            }
            
            .content-body {
                box-shadow: none;
                padding: 0;
            }
            
            .content {
                margin: 0;
                padding: 0;
            }
            
            header {
                background: white;
                color: black;
                box-shadow: none;
            }
            
            body {
                background: white;
            }
            
            .content-body h1, .content-body h2, .content-body h3 {
                page-break-after: avoid;
            }
            
            .content-body pre, .content-body table {
                page-break-inside: avoid;
            }
        }
        
        @media (max-width: 768px) {
            .container {
                flex-direction: column;
            }
            
            .sidebar {
                width: 100%;
                height: auto;
                position: relative;
                border-right: none;
                border-bottom: 1px solid var(--border-color);
            }
            
            .nav-toggle {
                display: block;
            }
            
            .content {
                margin: 1rem;
                padding: 1rem;
            }
            
            .content-wrapper {
                flex-direction: column;
            }
            
            .table-of-contents {
                position: relative;
                width: 100%;
                max-height: 300px;
            }
            
            .header-top {
                flex-direction: column;
                align-items: flex-start;
                gap: 1rem;
            }
            
            .search-input {
                width: 100%;
            }
            
            header h1 {
                font-size: 1.8rem;
            }
        }"""







