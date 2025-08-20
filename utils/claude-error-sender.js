// This script formats error logs and copies them to clipboard for pasting into Claude
// It can also attempt to auto-paste into Claude if running in a browser context

class ClaudeErrorSender {
  constructor() {
    this.errors = [];
  }

  parseErrorLog(logText) {
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
    
    this.errors = errors;
    return errors;
  }

  formatForClaude() {
    if (this.errors.length === 0) return '';

    let output = 'I have the following error log that needs analysis:\n\n';
    output += '```\n';
    output += `Total Errors: ${this.errors.length}\n\n`;
    
    // Group errors by category
    const errorsByCategory = {};
    this.errors.forEach(error => {
      if (!errorsByCategory[error.category]) {
        errorsByCategory[error.category] = [];
      }
      errorsByCategory[error.category].push(error);
    });

    // Format each category
    for (const [category, categoryErrors] of Object.entries(errorsByCategory)) {
      output += `${category} (${categoryErrors.length} occurrences):\n`;
      
      // Show first 5 errors from each category
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

  copyToClipboard(text) {
    if (navigator.clipboard && navigator.clipboard.writeText) {
      return navigator.clipboard.writeText(text);
    } else {
      // Fallback for older browsers
      const textArea = document.createElement('textarea');
      textArea.value = text;
      textArea.style.position = 'fixed';
      textArea.style.opacity = '0';
      document.body.appendChild(textArea);
      textArea.select();
      
      try {
        document.execCommand('copy');
        document.body.removeChild(textArea);
        return Promise.resolve();
      } catch (err) {
        document.body.removeChild(textArea);
        return Promise.reject(err);
      }
    }
  }

  async sendToClaude(errorLog) {
    // Parse the error log
    this.parseErrorLog(errorLog);
    
    // Format for Claude
    const formattedText = this.formatForClaude();
    
    // Copy to clipboard
    await this.copyToClipboard(formattedText);
    
    // Try to find Claude's input field and paste
    // This part will only work if running as a browser extension or userscript
    const claudeInput = document.querySelector('textarea[placeholder*="Message"]') || 
                       document.querySelector('div[contenteditable="true"]');
    
    if (claudeInput) {
      // Focus the input
      claudeInput.focus();
      
      // Clear existing content
      if (claudeInput.tagName === 'TEXTAREA') {
        claudeInput.value = formattedText;
        // Trigger input event
        claudeInput.dispatchEvent(new Event('input', { bubbles: true }));
      } else {
        claudeInput.textContent = formattedText;
        // Trigger input event for contenteditable
        claudeInput.dispatchEvent(new Event('input', { bubbles: true }));
      }
      
      // Wait a bit for the UI to update
      setTimeout(() => {
        // Try to find and click the send button
        const sendButton = document.querySelector('button[aria-label*="Send"]') ||
                          document.querySelector('button svg[data-icon="send"]')?.parentElement ||
                          Array.from(document.querySelectorAll('button')).find(btn => 
                            btn.textContent.includes('Send') || 
                            btn.innerHTML.includes('send'));
        
        if (sendButton && !sendButton.disabled) {
          sendButton.click();
          console.log('Message sent to Claude!');
        } else {
          console.log('Send button not found or disabled. Message copied to clipboard and pasted into input field.');
        }
      }, 100);
    } else {
      console.log('Claude input field not found. Message copied to clipboard. Please paste manually.');
    }
    
    return formattedText;
  }
}

// Export for Node.js
if (typeof module !== 'undefined' && module.exports) {
  module.exports = ClaudeErrorSender;
}

// Example usage
const errorLog = `App Errors
1:04:44 PM
Unexpected error while loading URL Error: Error invoking remote method 'GUEST_VIEW_MANAGER_CALL': Error: ERR_ABORTED (-3) loading 'about:blank'
App Errors
1:04:41 PM
Unexpected error while loading URL Error: Error invoking remote method 'GUEST_VIEW_MANAGER_CALL': Error: ERR_ABORTED (-3) loading 'about:blank'
Test Pipeline
12:59:46 PM
This is a test error to verify the logging pipeline works`;

// If running in browser
if (typeof window !== 'undefined') {
  const sender = new ClaudeErrorSender();
  
  // You can call this function with your error log
  window.sendErrorsToClaude = async (log) => {
    return await sender.sendToClaude(log || errorLog);
  };
  
  console.log('ClaudeErrorSender loaded. Use window.sendErrorsToClaude(errorLog) to send errors to Claude.');
}