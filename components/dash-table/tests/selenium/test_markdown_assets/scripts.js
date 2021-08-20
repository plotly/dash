window.hljs = {
    getLanguage: _ => false, // force auto-highlight
    highlightAuto: _ => {
        return {value: 'hljs override'};
    }
};
