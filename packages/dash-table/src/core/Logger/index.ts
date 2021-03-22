import DebugLevel from './DebugLevel';
import LogLevel from './LogLevel';

/*#if dev*/
import __isChrome from 'core/browser/isChrome';
/*#endif*/

const LogString: string[] = [];
LogString[LogLevel.TRACE] = 'trace';
LogString[LogLevel.INFO] = 'info';
LogString[LogLevel.WARNING] = 'warning';
LogString[LogLevel.ERROR] = 'error';
LogString[LogLevel.FATAL] = 'fatal';
LogString[LogLevel.NONE] = 'none';
LogString[DebugLevel.DEBUG] = 'debug';
LogString[DebugLevel.NONE] = 'trace';

let __logLevel: LogLevel = LogLevel.NONE;
let __debugLevel: DebugLevel = DebugLevel.NONE;

let __highlightPrefix: boolean;
/*#if dev */
__highlightPrefix = __isChrome;
/*#else*/
__highlightPrefix = false;
/*#endif*/

type LoggerFn = (...args: any[]) => void;

function logFn(
    level: LogLevel | DebugLevel,
    currentLevel: LogLevel | DebugLevel
): LoggerFn {
    if (level < currentLevel) {
        return () => {};
    }

    let fn: LoggerFn;
    let fnStyle = '';

    switch (level) {
        case LogLevel.TRACE:
        case LogLevel.INFO:
            fn = window.console.log;
            fnStyle = 'color: white; background-color: #3166A2;';
            break;
        case DebugLevel.DEBUG:
        case LogLevel.WARNING:
            fn = window.console.warn;
            fnStyle = 'color: white; background-color: #E9B606;';
            break;
        case LogLevel.ERROR:
        case LogLevel.FATAL:
            fn = window.console.error;
            fnStyle = 'color: white; background-color: #FF0000;';
            break;
        default:
            throw new Error(`Unknown log ${level}`);
    }

    const prefix = `${fnStyle && __highlightPrefix ? '%c' : ''}[${LogString[
        level
    ].toUpperCase()}]`;
    if (fnStyle && __highlightPrefix) {
        return fn.bind(window.console, prefix, fnStyle);
    } else {
        return fn.bind(window.console, prefix);
    }
}

interface ILogger {
    trace: LoggerFn;
    info: LoggerFn;
    warning: LoggerFn;
    error: LoggerFn;
    fatal: LoggerFn;
    debug: LoggerFn;

    setDebugLevel(level: DebugLevel): void;
    setLogLevel(level: LogLevel): void;
}

const logger: any = {
    setDebugLevel(level: DebugLevel) {
        __debugLevel = level;
    },

    setLogLevel(level: LogLevel) {
        __logLevel = level;
    }
};

Object.defineProperties(logger, {
    trace: {
        get: () => {
            return logFn(LogLevel.TRACE, __logLevel);
        },
        configurable: false,
        enumerable: false
    },
    info: {
        get: () => {
            return logFn(LogLevel.INFO, __logLevel);
        },
        configurable: false,
        enumerable: false
    },
    warning: {
        get: () => {
            return logFn(LogLevel.WARNING, __logLevel);
        },
        configurable: false,
        enumerable: false
    },
    error: {
        get: () => {
            return logFn(LogLevel.ERROR, __logLevel);
        },
        configurable: false,
        enumerable: false
    },
    fatal: {
        get: () => {
            return logFn(LogLevel.FATAL, __logLevel);
        },
        configurable: false,
        enumerable: false
    },
    debug: {
        get: () => {
            return logFn(DebugLevel.DEBUG, __debugLevel);
        },
        configurable: false,
        enumerable: false
    }
});

Object.freeze(logger);

export default logger as ILogger;

export {DebugLevel, LogLevel};
