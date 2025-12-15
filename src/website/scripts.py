"""JavaScript code for website interactivity.

This module provides the embedded JavaScript code for the course website,
including navigation, search, dark mode, progress tracking, and content loading.
"""


def get_javascript(modules_json: str) -> str:
    """Get embedded JavaScript for interactivity.
    
    Args:
        modules_json: JSON string of modules data
        
    Returns:
        JavaScript string with all interactive functionality
    """
    return f"""        // Initialize Mermaid
        mermaid.initialize({{ startOnLoad: false, theme: 'default' }});
        
        // Initialize Highlight.js
        if (typeof hljs !== 'undefined') {{
            hljs.highlightAll();
        }}
        
        // Modules data
        const modulesData = {modules_json};
        
        // State
        let currentModuleId = null;
        let currentSession = null;
        let currentContentType = null;
        let searchTimeout = null;
        
        // Progress tracking
        function getViewedSessions() {{
            const stored = localStorage.getItem('viewedSessions');
            return stored ? JSON.parse(stored) : [];
        }}
        
        function markSessionViewed(moduleId, sessionNum) {{
            const viewed = getViewedSessions();
            const key = `${{moduleId}}_${{sessionNum}}`;
            if (!viewed.includes(key)) {{
                viewed.push(key);
                localStorage.setItem('viewedSessions', JSON.stringify(viewed));
                updateProgress();
            }}
        }}
        
        function updateProgress() {{
            const viewed = getViewedSessions();
            const totalSessions = modulesData.reduce((sum, m) => sum + m.sessions.length, 0);
            const percentage = totalSessions > 0 ? Math.round((viewed.length / totalSessions) * 100) : 0;
            const indicator = document.getElementById('progressIndicator');
            if (indicator) {{
                indicator.innerHTML = `<p>Progress: ${{viewed.length}} / ${{totalSessions}} sessions viewed (${{percentage}}%)</p><div class="progress-bar"><div class="progress-fill" style="width: ${{percentage}}%"></div></div>`;
            }}
            // Mark viewed sessions in navigation
            viewed.forEach(key => {{
                const [moduleId, sessionNum] = key.split('_');
                const sessionButton = document.querySelector(`.session-button[data-module-id="${{moduleId}}"][data-session="session_${{sessionNum.padStart(2, '0')}}"]`);
                if (sessionButton) {{
                    sessionButton.classList.add('session-viewed');
                }}
            }});
        }}
        
        // Dark mode
        function initDarkMode() {{
            const stored = localStorage.getItem('darkMode');
            const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
            const isDark = stored ? stored === 'true' : prefersDark;
            document.documentElement.setAttribute('data-theme', isDark ? 'dark' : 'light');
            const toggle = document.getElementById('darkModeToggle');
            if (toggle) toggle.textContent = isDark ? '☀️' : '🌙';
        }}
        
        function toggleDarkMode() {{
            const current = document.documentElement.getAttribute('data-theme');
            const newTheme = current === 'dark' ? 'light' : 'dark';
            document.documentElement.setAttribute('data-theme', newTheme);
            localStorage.setItem('darkMode', newTheme === 'dark' ? 'true' : 'false');
            const toggle = document.getElementById('darkModeToggle');
            if (toggle) toggle.textContent = newTheme === 'dark' ? '☀️' : '🌙';
        }}
        
        initDarkMode();
        updateProgress();
        
        // DOM elements (will be set in initializeEventHandlers)
        let sidebar, navToggle, moduleList, welcomeScreen, contentView, backButton;
        let contentTitle, contentBody, breadcrumbs, tocToggle, tableOfContents, tocList;
        let searchInput, searchButton, searchResults, printButton, darkModeToggle;
        
        // Search functionality
        function performSearch(query) {{
            if (!query || query.length < 2) {{
                searchResults.classList.remove('active');
                return;
            }}
            
            const results = [];
            const lowerQuery = query.toLowerCase();
            
            modulesData.forEach(module => {{
                module.sessions.forEach(session => {{
                    Object.entries(session.content || {{}}).forEach(([type, content]) => {{
                        if (typeof content === 'string') {{
                            const textContent = content.replace(/<[^>]*>/g, '').toLowerCase();
                            if (textContent.includes(lowerQuery)) {{
                                results.push({{
                                    moduleId: module.module_id,
                                    moduleName: module.module_name,
                                    sessionNum: session.session_number,
                                    sessionTitle: session.session_title,
                                    contentType: type,
                                    snippet: content.substring(0, 200).replace(/<[^>]*>/g, '')
                                }});
                            }}
                        }}
                    }});
                }});
            }});
            
            displaySearchResults(results, query);
        }}
        
        function displaySearchResults(results, query) {{
            if (results.length === 0) {{
                searchResults.innerHTML = '<div class="search-result-item">No results found</div>';
                searchResults.classList.add('active');
                return;
            }}
            
            const html = results.slice(0, 10).map(result => {{
                const highlighted = result.snippet.replace(
                    new RegExp(`(${{query}})`, 'gi'),
                    '<span class="search-highlight">$1</span>'
                );
                return `<div class="search-result-item" data-module-id="${{result.moduleId}}" data-session="${{result.sessionNum}}" data-content-type="${{result.contentType}}">
                    <strong>${{result.moduleName}} - ${{result.sessionTitle}} - ${{result.contentType}}</strong><br>
                    <small>${{highlighted}}...</small>
                </div>`;
            }}).join('');
            
            searchResults.innerHTML = html;
            searchResults.classList.add('active');
            
            // Add click handlers
            searchResults.querySelectorAll('.search-result-item').forEach(item => {{
                item.addEventListener('click', () => {{
                    const moduleId = parseInt(item.dataset.moduleId);
                    const sessionNum = parseInt(item.dataset.sessionNum);
                    const contentType = item.dataset.contentType;
                    const sessionKey = `session_${{sessionNum.toString().padStart(2, '0')}}`;
                    loadContent(moduleId, sessionKey, contentType);
                    searchResults.classList.remove('active');
                    searchInput.value = '';
                }});
            }});
        }}
        
        // Generate table of contents from content
        function generateTOC() {{
            if (!tocList || !contentBody) return;
            
            const headings = contentBody.querySelectorAll('h1, h2, h3, h4, h5, h6');
            if (headings.length === 0) {{
                if (tableOfContents) tableOfContents.style.display = 'none';
                return;
            }}
            
            tocList.innerHTML = '';
            headings.forEach((heading, index) => {{
                const id = `heading-${{index}}`;
                heading.id = id;
                const level = parseInt(heading.tagName.charAt(1));
                const li = document.createElement('li');
                li.className = `level-${{level}}`;
                const a = document.createElement('a');
                a.href = `#${{id}}`;
                a.textContent = heading.textContent;
                a.addEventListener('click', (e) => {{
                    e.preventDefault();
                    heading.scrollIntoView({{ behavior: 'smooth', block: 'start' }});
                }});
                li.appendChild(a);
                tocList.appendChild(li);
            }});
        }}
        
        // Initialize all event handlers - must be called after DOM is ready
        function initializeEventHandlers() {{
            // Get DOM elements
            sidebar = document.getElementById('sidebar');
            navToggle = document.getElementById('navToggle');
            moduleList = document.getElementById('moduleList');
            welcomeScreen = document.getElementById('welcomeScreen');
            contentView = document.getElementById('contentView');
            backButton = document.getElementById('backButton');
            contentTitle = document.getElementById('contentTitle');
            contentBody = document.getElementById('contentBody');
            breadcrumbs = document.getElementById('breadcrumbs');
            tocToggle = document.getElementById('tocToggle');
            tableOfContents = document.getElementById('tableOfContents');
            tocList = document.getElementById('tocList');
            searchInput = document.getElementById('searchInput');
            searchButton = document.getElementById('searchButton');
            searchResults = document.getElementById('searchResults');
            printButton = document.getElementById('printButton');
            darkModeToggle = document.getElementById('darkModeToggle');
            
            // Verify critical elements exist
            if (!sidebar) {{
                console.error('Sidebar element not found - retrying...');
                setTimeout(initializeEventHandlers, 100);
                return;
            }}
            
            if (!welcomeScreen || !contentView || !contentBody || !contentTitle) {{
                console.error('Critical content elements not found - retrying...');
                setTimeout(initializeEventHandlers, 100);
                return;
            }}
            
            // Search functionality
            if (searchInput) {{
                searchInput.addEventListener('input', (e) => {{
                    clearTimeout(searchTimeout);
                    searchTimeout = setTimeout(() => performSearch(e.target.value), 300);
                }});
                
                searchInput.addEventListener('keydown', (e) => {{
                    if (e.key === 'Escape') {{
                        if (searchResults) searchResults.classList.remove('active');
                    }}
                }});
            }}
            
            if (searchButton) {{
                searchButton.addEventListener('click', () => {{
                    if (searchInput) performSearch(searchInput.value);
                }});
            }}
            
            // Keyboard shortcut for search (Ctrl/Cmd + K)
            document.addEventListener('keydown', (e) => {{
                if ((e.ctrlKey || e.metaKey) && e.key === 'k') {{
                    e.preventDefault();
                    if (searchInput) searchInput.focus();
                }}
            }});
            
            // Click outside to close search results
            document.addEventListener('click', (e) => {{
                if (searchResults && !searchResults.contains(e.target) && e.target !== searchInput && e.target !== searchButton) {{
                    searchResults.classList.remove('active');
                }}
            }});
            
            // Dark mode toggle
            if (darkModeToggle) {{
                darkModeToggle.addEventListener('click', toggleDarkMode);
            }}
            
            // Print button
            if (printButton) {{
                printButton.addEventListener('click', () => {{
                    window.print();
                }});
            }}
            
            // TOC toggle
            if (tocToggle && tableOfContents) {{
                tocToggle.addEventListener('click', () => {{
                    const isVisible = tableOfContents.style.display !== 'none';
                    tableOfContents.style.display = isVisible ? 'none' : 'block';
                }});
            }}
            
            // Toggle sidebar on mobile
            if (navToggle && sidebar) {{
                navToggle.addEventListener('click', () => {{
                    const isExpanded = navToggle.getAttribute('aria-expanded') === 'true';
                    navToggle.setAttribute('aria-expanded', !isExpanded);
                    sidebar.classList.toggle('collapsed');
                }});
            }}
            
            // Simple event delegation on sidebar - handles all button clicks
            // This works even if buttons are initially hidden (display: none)
            sidebar.addEventListener('click', (e) => {{
                // Check for content button clicks first (most specific, deepest in DOM)
                const contentButton = e.target.closest('.content-button');
                if (contentButton) {{
                    e.stopPropagation();
                    e.preventDefault();
                    
                    const moduleId = parseInt(contentButton.dataset.moduleId);
                    const session = contentButton.dataset.session;
                    const contentType = contentButton.dataset.contentType;
                    
                    console.log('Content button clicked:', {{ moduleId, session, contentType }});
                    
                    // Validate we have all required data
                    if (!moduleId || !session || !contentType) {{
                        console.warn('Content button missing required data attributes', contentButton);
                        return;
                    }}
                    
                    // Remove active class from all buttons
                    document.querySelectorAll('.content-button').forEach(btn => {{
                        btn.classList.remove('active');
                    }});
                    contentButton.classList.add('active');
                    
                    console.log('Calling loadContent...');
                    loadContent(moduleId, session, contentType);
                    return;
                }}
                
                // Check for session button clicks (only if not clicking content button)
                const sessionButton = e.target.closest('.session-button');
                if (sessionButton && !e.target.closest('.content-button')) {{
                    e.stopPropagation();
                    e.preventDefault();
                    const contentList = sessionButton.nextElementSibling;
                    if (contentList && contentList.classList.contains('content-list')) {{
                        const isExpanded = sessionButton.getAttribute('aria-expanded') === 'true';
                        sessionButton.setAttribute('aria-expanded', !isExpanded);
                        contentList.style.display = isExpanded ? 'none' : 'block';
                    }}
                    return;
                }}
                
                // Check for module button clicks (only if not clicking session/content button)
                const moduleButton = e.target.closest('.module-button');
                if (moduleButton && !e.target.closest('.session-button') && !e.target.closest('.content-button')) {{
                    e.stopPropagation();
                    e.preventDefault();
                    const sessionList = moduleButton.nextElementSibling;
                    if (sessionList && sessionList.classList.contains('session-list')) {{
                        const isExpanded = moduleButton.getAttribute('aria-expanded') === 'true';
                        moduleButton.setAttribute('aria-expanded', !isExpanded);
                        sessionList.style.display = isExpanded ? 'none' : 'block';
                    }}
                    return;
                }}
            }});
            
            // Back button handler
            if (backButton) {{
                backButton.addEventListener('click', () => {{
                    showWelcome();
                }});
            }}
            
            console.log('Event handlers initialized successfully');
        }}
        
        // DOM-ready initialization with multiple fallback strategies
        (function() {{
            function init() {{
                initializeEventHandlers();
            }}
            
            // Strategy 1: DOM already loaded
            if (document.readyState === 'complete' || document.readyState === 'interactive') {{
                // DOM already loaded, initialize immediately
                setTimeout(init, 0);
            }} else {{
                // Strategy 2: Wait for DOMContentLoaded
                document.addEventListener('DOMContentLoaded', init);
                // Strategy 3: Fallback to window.onload
                window.addEventListener('load', init);
            }}
        }})();
        
        // Update breadcrumbs
        function updateBreadcrumbs(moduleName, sessionTitle, contentTypeName) {{
            if (!breadcrumbs) return;
            // contentTypeName is already the display name calculated in loadContent
            breadcrumbs.innerHTML = `<a href="#" onclick="showWelcome(); return false;">Course</a> <span>›</span> <a href="#" onclick="event.preventDefault();">${{moduleName}}</a> <span>›</span> <a href="#" onclick="event.preventDefault();">${{sessionTitle}}</a> <span>›</span> <span>${{contentTypeName}}</span>`;
        }}
        
        // Add copy buttons to code blocks
        function addCopyButtons() {{
            contentBody.querySelectorAll('pre code').forEach(block => {{
                const pre = block.parentElement;
                if (pre.querySelector('.copy-code-button')) return;
                
                const button = document.createElement('button');
                button.className = 'copy-code-button';
                button.textContent = 'Copy';
                button.addEventListener('click', () => {{
                    navigator.clipboard.writeText(block.textContent).then(() => {{
                        button.textContent = 'Copied!';
                        setTimeout(() => {{ button.textContent = 'Copy'; }}, 2000);
                    }});
                }});
                pre.appendChild(button);
            }});
        }}
        
        // Load content function
        function loadContent(moduleId, session, contentType) {{
            console.log('loadContent called with:', {{ moduleId, session, contentType }});
            
            // Ensure DOM elements are available
            if (!contentBody || !welcomeScreen || !contentView || !contentTitle) {{
                console.error('Content elements not available - DOM may not be ready', {{
                    contentBody: !!contentBody,
                    welcomeScreen: !!welcomeScreen,
                    contentView: !!contentView,
                    contentTitle: !!contentTitle
                }});
                // Retry initialization
                if (typeof initializeEventHandlers === 'function') {{
                    initializeEventHandlers();
                }}
                return;
            }}
            
            console.log('DOM elements available, loading content...');
            
            // Show loading state
            contentBody.innerHTML = '<div class="loading-spinner"></div>';
            
            const module = modulesData.find(m => m.module_id === moduleId);
            if (!module) {{
                contentBody.innerHTML = '<p>Module not found.</p>';
                return;
            }}
            
            const sessionData = module.sessions.find(s => {{
                const sessionNum = s.session_number || 0;
                return `session_${{sessionNum.toString().padStart(2, '0')}}` === session;
            }});
            if (!sessionData) {{
                contentBody.innerHTML = '<p>Session not found.</p>';
                return;
            }}
            
            const content = sessionData.content[contentType];
            if (!content) {{
                contentBody.innerHTML = '<p>Content not available.</p>';
                return;
            }}
            
            // Update state
            currentModuleId = moduleId;
            currentSession = session;
            currentContentType = contentType;
            
            // Update title
            const moduleName = module.module_name || `Module ${{moduleId}}`;
            const sessionTitle = sessionData.session_title || `Session ${{sessionData.session_number}}`;
            const contentTypeNames = {{
                'lecture': 'Lecture',
                'lab': 'Lab',
                'study_notes': 'Study Notes',
                'questions': 'Questions',
                'application': 'Application',
                'extension': 'Extension',
                'visualization': 'Visualization',
                'integration': 'Integration',
                'investigation': 'Investigation',
                'open_questions': 'Open Questions'
            }};
            const contentTypeName = contentTypeNames[contentType] || contentType;
            
            contentTitle.textContent = `${{moduleName}} - ${{sessionTitle}} - ${{contentTypeName}}`;
            updateBreadcrumbs(moduleName, sessionTitle, contentTypeName);
            
            // Render content
            if (contentType === 'visualization' || contentType.startsWith('diagram_')) {{
                // Mermaid diagram - create div and set text content (not innerHTML)
                const mermaidDiv = document.createElement('div');
                mermaidDiv.className = 'mermaid';
                mermaidDiv.textContent = content;
                contentBody.innerHTML = '';
                contentBody.appendChild(mermaidDiv);
                
                // Show loading, then render
                setTimeout(() => {{
                    try {{
                        mermaid.run();
                    }} catch (e) {{
                        console.error('Mermaid rendering error:', e);
                        mermaidDiv.innerHTML = '<p>Error rendering diagram. Raw content:</p><pre>' + escapeHtml(content) + '</pre>';
                    }}
                }}, 100);
            }} else {{
                // Markdown content (already converted to HTML)
                contentBody.innerHTML = content;
                
                // Add copy buttons to code blocks
                addCopyButtons();
                
                // Highlight code
                if (typeof hljs !== 'undefined') {{
                    contentBody.querySelectorAll('pre code').forEach(block => {{
                        hljs.highlightElement(block);
                    }});
                }}
                
                // Re-initialize Mermaid for any diagrams in the content
                setTimeout(() => {{
                    try {{
                        mermaid.run();
                    }} catch (e) {{
                        console.error('Mermaid rendering error:', e);
                    }}
                }}, 100);
                
                // Generate TOC
                setTimeout(generateTOC, 200);
            }}
            
            // Mark session as viewed
            markSessionViewed(moduleId, sessionData.session_number);
            
            // Show content view
            welcomeScreen.style.display = 'none';
            contentView.style.display = 'block';
            
            // Update ARIA live region
            const indicator = document.getElementById('progressIndicator');
            if (indicator) {{
                indicator.setAttribute('aria-live', 'polite');
            }}
            
            // Scroll to top
            window.scrollTo({{ top: 0, behavior: 'smooth' }});
            
            // Focus management for accessibility
            contentTitle.focus();
        }}
        
        // Show welcome screen
        function showWelcome() {{
            if (!welcomeScreen || !contentView) {{
                console.error('Welcome screen elements not available');
                return;
            }}
            welcomeScreen.style.display = 'block';
            contentView.style.display = 'none';
            currentModuleId = null;
            currentSession = null;
            currentContentType = null;
            if (breadcrumbs) breadcrumbs.innerHTML = '';
            if (tableOfContents) tableOfContents.style.display = 'none';
            document.querySelectorAll('.content-button').forEach(btn => {{
                btn.classList.remove('active');
            }});
        }}
        
        // Make showWelcome available globally
        window.showWelcome = showWelcome;
        
        // Escape HTML helper
        function escapeHtml(text) {{
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }}
        
        // Keyboard navigation
        document.addEventListener('keydown', (e) => {{
            // Escape key closes search or goes back
            if (e.key === 'Escape') {{
                if (searchResults && searchResults.classList.contains('active')) {{
                    searchResults.classList.remove('active');
                    searchInput.blur();
                }} else if (contentView.style.display !== 'none') {{
                    showWelcome();
                }}
            }}
            
            // Tab navigation enhancement
            if (e.key === 'Tab') {{
                // Ensure focusable elements are visible
                const focusable = document.querySelectorAll('a[href], button:not([disabled]), input:not([disabled]), [tabindex]:not([tabindex="-1"])');
                focusable.forEach(el => {{
                    if (el.offsetParent === null && el.tabIndex >= 0) {{
                        el.style.visibility = 'visible';
                    }}
                }});
            }}
        }});
        
        // Initialize on page load
        document.addEventListener('DOMContentLoaded', () => {{
            updateProgress();
            
            // Check for continue where left off
            const lastViewed = localStorage.getItem('lastViewed');
            if (lastViewed) {{
                try {{
                    const {{ moduleId, session, contentType }} = JSON.parse(lastViewed);
                    const module = modulesData.find(m => m.module_id === moduleId);
                    if (module) {{
                        const sessionData = module.sessions.find(s => {{
                            const sessionNum = s.session_number || 0;
                            return `session_${{sessionNum.toString().padStart(2, '0')}}` === session;
                        }});
                        if (sessionData && sessionData.content[contentType]) {{
                            // Optionally auto-load last viewed content
                            // loadContent(moduleId, session, contentType);
                        }}
                    }}
                }} catch (e) {{
                    console.error('Error loading last viewed:', e);
                }}
            }}
            
            // Ensure event handlers are initialized
            if (typeof initializeEventHandlers === 'function') {{
                initializeEventHandlers();
            }}
        }});
        
        // Save last viewed
        function saveLastViewed() {{
            if (currentModuleId && currentSession && currentContentType) {{
                localStorage.setItem('lastViewed', JSON.stringify({{
                    moduleId: currentModuleId,
                    session: currentSession,
                    contentType: currentContentType
                }}));
            }}
        }}
        
        // Update loadContent to save last viewed
        const originalLoadContent = loadContent;
        loadContent = function(...args) {{
            originalLoadContent(...args);
            saveLastViewed();
        }};"""

