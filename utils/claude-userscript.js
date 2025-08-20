// ==UserScript==
// @name         Claude Error Log Auto-Sender
// @namespace    http://tampermonkey.net/
// @version      1.0
// @description  Automatically paste and send error logs to Claude
// @author       You
// @match        https://claude.ai/*
// @match        https://console.anthropic.com/*
// @grant        none
// ==/UserScript==

(function() {
    'use strict';

    // Add keyboard shortcut (Ctrl/Cmd + Shift + E)
    document.addEventListener('keydown', async (e) => {
        if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key === 'E') {
            e.preventDefault();
            
            // Get clipboard content
            try {
                const clipboardText = await navigator.clipboard.readText();
                if (clipboardText && clipboardText.includes('Error')) {
                    sendErrorLogToClaude(clipboardText);
                } else {
                    alert('No error log found in clipboard. Copy your error log first.');
                }
            } catch (err) {
                // Fallback: show prompt
                const errorLog = prompt('Paste your error log here:');
                if (errorLog) {
                    sendErrorLogToClaude(errorLog);
                }
            }
        }
    });

    function parseErrorLog(logText) {
        const lines = logText.split('\n');
        const errors = [];
        let i = 0;

        while (i < lines.length) {
            const line = lines[i];
            if (line.trim() === '') {
                i++;
                continue;
            }
            
            if (line === 'App Errors' || line === 'Test Pipeline' || 
                (line.trim() && !line.match(/^\d{1,2}:\d{2}:\d{2}\s*[AP]M$/) && 
                 !line.startsWith('Unexpected error') && !line.startsWith('This is a test'))) {
                
                const category = line.trim();
                
                i++;
                if (i < lines.length) {
                    const timestampLine = lines[i];
                    const timeMatch = timestampLine.match(/^(\d{1,2}:\d{2}:\d{2}\s*[AP]M)$/);
                    
                    if (timeMatch) {
                        const timestamp = timeMatch[1];
                        
                        i++;
                        if (i < lines.length) {
                            const message = lines[i].trim();
                            
                            errors.push({
                                category: category,
                                message: message,
                                timestamp: timestamp
                            });
                        }
                    }
                }
            }
            i++;
        }
        
        return errors;
    }

    function formatForClaude(errors) {
        if (errors.length === 0) return '';

        let output = 'I have the following error log that needs analysis:\n\n```\n';
        output += `Total Errors: ${errors.length}\n\n`;
        
        const errorsByCategory = {};
        errors.forEach(error => {
            if (!errorsByCategory[error.category]) {
                errorsByCategory[error.category] = [];
            }
            errorsByCategory[error.category].push(error);
        });

        for (const [category, categoryErrors] of Object.entries(errorsByCategory)) {
            output += `${category} (${categoryErrors.length} occurrences):\n`;
            
            categoryErrors.slice(0, 5).forEach(error => {
                output += `  ${error.timestamp} - ${error.message.substring(0, 100)}${error.message.length > 100 ? '...' : ''}\n`;
            });
            
            if (categoryErrors.length > 5) {
                output += `  ... and ${categoryErrors.length - 5} more\n`;
            }
            output += '\n';
        }
        
        output += '```\n\n';
        output += 'Can you help me understand what\'s causing these errors and how to fix them?';
        
        return output;
    }

    function sendErrorLogToClaude(errorLog) {
        const errors = parseErrorLog(errorLog);
        const formattedText = formatForClaude(errors);
        
        // Find Claude's input field
        const selectors = [
            'textarea[placeholder*="Message"]',
            'textarea[placeholder*="message"]',
            'div[contenteditable="true"]',
            'textarea.ProseMirror',
            'div.ProseMirror[contenteditable="true"]'
        ];
        
        let inputField = null;
        for (const selector of selectors) {
            inputField = document.querySelector(selector);
            if (inputField) break;
        }
        
        if (inputField) {
            // Focus the input
            inputField.focus();
            
            // Clear and set content
            if (inputField.tagName === 'TEXTAREA') {
                inputField.value = formattedText;
                inputField.dispatchEvent(new Event('input', { bubbles: true }));
                inputField.dispatchEvent(new Event('change', { bubbles: true }));
            } else {
                // For contenteditable divs
                inputField.innerHTML = formattedText.replace(/\n/g, '<br>');
                inputField.dispatchEvent(new Event('input', { bubbles: true }));
                
                // Trigger any React/Vue change events
                const nativeInputValueSetter = Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, "value").set;
                nativeInputValueSetter?.call(inputField, formattedText);
                inputField.dispatchEvent(new Event('input', { bubbles: true }));
            }
            
            // Wait for UI to update then send
            setTimeout(() => {
                // Find send button
                const sendSelectors = [
                    'button[aria-label*="Send"]',
                    'button[aria-label*="send"]',
                    'button:has(svg[data-icon="send"])',
                    'button:has(svg path[d*="M2.01 21L23 12"])', // Common send icon path
                ];
                
                let sendButton = null;
                for (const selector of sendSelectors) {
                    try {
                        sendButton = document.querySelector(selector);
                        if (sendButton && !sendButton.disabled) break;
                    } catch (e) {
                        // :has() might not be supported
                    }
                }
                
                // Fallback: find by text content
                if (!sendButton) {
                    sendButton = Array.from(document.querySelectorAll('button')).find(btn => 
                        !btn.disabled && (
                            btn.textContent.toLowerCase().includes('send') ||
                            btn.innerHTML.includes('send') ||
                            btn.getAttribute('aria-label')?.toLowerCase().includes('send')
                        )
                    );
                }
                
                if (sendButton && !sendButton.disabled) {
                    sendButton.click();
                    console.log('Error log sent to Claude!');
                    
                    // Show success notification
                    showNotification('✓ Error log sent to Claude!', 'success');
                } else {
                    // Try pressing Enter
                    const enterEvent = new KeyboardEvent('keydown', {
                        key: 'Enter',
                        code: 'Enter',
                        keyCode: 13,
                        which: 13,
                        bubbles: true,
                        cancelable: true,
                        composed: true
                    });
                    inputField.dispatchEvent(enterEvent);
                    
                    showNotification('Error log pasted. Press Enter to send.', 'info');
                }
            }, 500);
        } else {
            navigator.clipboard.writeText(formattedText);
            showNotification('Claude input not found. Error log copied to clipboard.', 'warning');
        }
    }

    function showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 15px 20px;
            border-radius: 8px;
            font-family: -apple-system, system-ui, sans-serif;
            font-size: 14px;
            font-weight: 500;
            z-index: 10000;
            animation: slideIn 0.3s ease;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        `;
        
        const colors = {
            success: { bg: '#d4edda', color: '#155724', border: '#c3e6cb' },
            info: { bg: '#d1ecf1', color: '#0c5460', border: '#bee5eb' },
            warning: { bg: '#fff3cd', color: '#856404', border: '#ffeaa7' }
        };
        
        const style = colors[type] || colors.info;
        notification.style.backgroundColor = style.bg;
        notification.style.color = style.color;
        notification.style.border = `1px solid ${style.border}`;
        
        notification.textContent = message;
        document.body.appendChild(notification);
        
        // Add animation
        const styleSheet = document.createElement('style');
        styleSheet.textContent = `
            @keyframes slideIn {
                from { transform: translateX(100%); opacity: 0; }
                to { transform: translateX(0); opacity: 1; }
            }
        `;
        document.head.appendChild(styleSheet);
        
        setTimeout(() => {
            notification.style.animation = 'slideIn 0.3s ease reverse';
            setTimeout(() => {
                notification.remove();
                styleSheet.remove();
            }, 300);
        }, 3000);
    }

    // Add floating button for manual trigger
    const button = document.createElement('button');
    button.innerHTML = '📋 Send Error Log';
    button.style.cssText = `
        position: fixed;
        bottom: 20px;
        right: 20px;
        padding: 10px 15px;
        background-color: #007bff;
        color: white;
        border: none;
        border-radius: 25px;
        font-size: 14px;
        font-weight: 500;
        cursor: pointer;
        box-shadow: 0 2px 10px rgba(0,123,255,0.3);
        z-index: 9999;
        transition: all 0.3s;
    `;
    
    button.addEventListener('mouseenter', () => {
        button.style.transform = 'scale(1.05)';
        button.style.boxShadow = '0 4px 15px rgba(0,123,255,0.4)';
    });
    
    button.addEventListener('mouseleave', () => {
        button.style.transform = 'scale(1)';
        button.style.boxShadow = '0 2px 10px rgba(0,123,255,0.3)';
    });
    
    button.addEventListener('click', async () => {
        try {
            const clipboardText = await navigator.clipboard.readText();
            if (clipboardText && clipboardText.includes('Error')) {
                sendErrorLogToClaude(clipboardText);
            } else {
                const errorLog = prompt('Paste your error log here:');
                if (errorLog) {
                    sendErrorLogToClaude(errorLog);
                }
            }
        } catch (err) {
            const errorLog = prompt('Paste your error log here:');
            if (errorLog) {
                sendErrorLogToClaude(errorLog);
            }
        }
    });
    
    // Add button after page loads
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => {
            document.body.appendChild(button);
        });
    } else {
        document.body.appendChild(button);
    }
    
    console.log('Claude Error Log Auto-Sender loaded! Use Ctrl/Cmd+Shift+E or click the button.');
})();