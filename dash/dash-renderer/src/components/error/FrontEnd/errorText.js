function htmlToText(html) {
    if (!html.trim().startsWith('<')) {
        return html;
    }
    const doc = new DOMParser().parseFromString(html, 'text/html');
    const plainTraceback = doc.querySelector('.plain textarea');
    if (plainTraceback) {
        return plainTraceback.value.trim();
    }
    return (doc.body.textContent || '').trim();
}

/**
 * Builds the plain text of a debug toolbar error so it can be copied:
 * the message, the frontend stack trace and the backend traceback.
 */
function errorToText(error) {
    const parts = [];
    if (typeof error.message === 'string' && error.message) {
        parts.push(error.message);
    }
    if (typeof error.stack === 'string' && error.stack) {
        parts.push(error.stack);
    }
    if (typeof error.html === 'string' && error.html) {
        parts.push(htmlToText(error.html));
    }
    return parts.join('\n\n');
}

async function copyToClipboard(text) {
    if (navigator.clipboard && window.isSecureContext) {
        try {
            await navigator.clipboard.writeText(text);
            return;
        } catch (e) {
            // Permission can be denied, e.g. inside an iframe: use the fallback
        }
    }
    const textarea = document.createElement('textarea');
    textarea.value = text;
    textarea.style.position = 'fixed';
    textarea.style.opacity = '0';
    document.body.appendChild(textarea);
    textarea.select();
    try {
        if (!document.execCommand('copy')) {
            throw new Error('Copy command was rejected');
        }
    } finally {
        document.body.removeChild(textarea);
    }
}

export {errorToText, copyToClipboard};
