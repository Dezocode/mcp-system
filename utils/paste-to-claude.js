// Simple script to paste error log into Claude
// 1. Copy this entire script
// 2. Go to Claude.ai
// 3. Open console (F12)
// 4. Paste and run

(function() {
    // YOUR ERROR LOG - Replace this with your actual error log
    const errorLog = `App Errors
1:04:44 PM
Unexpected error while loading URL Error: Error invoking remote method 'GUEST_VIEW_MANAGER_CALL': Error: ERR_ABORTED (-3) loading 'about:blank'
App Errors
1:04:41 PM
Unexpected error while loading URL Error: Error invoking remote method 'GUEST_VIEW_MANAGER_CALL': Error: ERR_ABORTED (-3) loading 'about:blank'
Test Pipeline
12:59:46 PM
This is a test error to verify the logging pipeline works`;

    // Count errors
    const lines = errorLog.split('\n');
    let errorCount = 0;
    let appErrors = 0;
    let testErrors = 0;
    
    for (let i = 0; i < lines.length; i++) {
        if (lines[i] === 'App Errors') {
            appErrors++;
            errorCount++;
        } else if (lines[i] === 'Test Pipeline') {
            testErrors++;
            errorCount++;
        }
    }

    // Format message for Claude
    const message = `I need help with these errors from my application:

Error Summary:
- Total errors: ${errorCount}
- App Errors: ${appErrors} 
- Test Pipeline Errors: ${testErrors}

The main error message is:
"Error invoking remote method 'GUEST_VIEW_MANAGER_CALL': Error: ERR_ABORTED (-3) loading 'about:blank'"

This error appears to be repeating every 3 seconds. Can you help me understand what's causing this and how to fix it?

Full error log sample:
\`\`\`
${errorLog.substring(0, 500)}...
\`\`\``;

    // Method 1: Try React-based input
    function tryReactInput() {
        const textareas = document.querySelectorAll('textarea');
        for (const textarea of textareas) {
            if (textarea.placeholder && textarea.placeholder.toLowerCase().includes('message')) {
                const nativeInputValueSetter = Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, "value").set;
                nativeInputValueSetter.call(textarea, message);
                
                const ev1 = new Event('input', { bubbles: true });
                const ev2 = new Event('change', { bubbles: true });
                textarea.dispatchEvent(ev1);
                textarea.dispatchEvent(ev2);
                
                console.log('✅ Message pasted via React method');
                return true;
            }
        }
        return false;
    }

    // Method 2: Try contenteditable div
    function tryContentEditable() {
        const editables = document.querySelectorAll('[contenteditable="true"]');
        for (const editable of editables) {
            if (editable.className.includes('ProseMirror') || editable.getAttribute('data-placeholder')) {
                editable.focus();
                document.execCommand('selectAll', false, null);
                document.execCommand('insertText', false, message);
                
                editable.dispatchEvent(new Event('input', { bubbles: true }));
                console.log('✅ Message pasted via contenteditable');
                return true;
            }
        }
        return false;
    }

    // Method 3: Clipboard paste simulation
    function tryClipboardPaste() {
        const activeElement = document.activeElement;
        if (activeElement && (activeElement.tagName === 'TEXTAREA' || activeElement.contentEditable === 'true')) {
            navigator.clipboard.writeText(message).then(() => {
                activeElement.focus();
                document.execCommand('paste');
                console.log('✅ Message pasted via clipboard');
            });
            return true;
        }
        return false;
    }

    // Try all methods
    let success = tryReactInput();
    if (!success) success = tryContentEditable();
    if (!success) success = tryClipboardPaste();
    
    if (!success) {
        // Final fallback - copy to clipboard
        navigator.clipboard.writeText(message).then(() => {
            console.log('📋 Message copied to clipboard!');
            console.log('Please click in the message box and press Ctrl/Cmd+V to paste');
            alert('Message copied! Click in Claude\'s message box and press Ctrl/Cmd+V to paste, then press Enter to send.');
        });
    } else {
        // Try to find and click send button
        setTimeout(() => {
            const buttons = document.querySelectorAll('button');
            let sendButton = null;
            
            // Look for send button by various methods
            for (const button of buttons) {
                // Check aria-label
                const ariaLabel = button.getAttribute('aria-label');
                if (ariaLabel && ariaLabel.toLowerCase().includes('send')) {
                    sendButton = button;
                    break;
                }
                
                // Check for SVG icon
                if (button.querySelector('svg') && !button.disabled && button.offsetParent !== null) {
                    // Check if it's likely the send button based on position/style
                    const rect = button.getBoundingClientRect();
                    if (rect.bottom > window.innerHeight * 0.7) { // In lower part of screen
                        sendButton = button;
                    }
                }
            }
            
            if (sendButton && !sendButton.disabled) {
                sendButton.click();
                console.log('🚀 Message sent!');
            } else {
                console.log('⌨️ Please press Enter to send the message');
                alert('Message pasted! Press Enter to send.');
            }
        }, 1000);
    }
})();