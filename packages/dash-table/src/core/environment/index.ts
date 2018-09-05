import { DebugLevel, LogLevel } from 'core/Logger';
import CookieStorage from 'core/storage/Cookie';

const DASH_DEBUG = 'dash_debug';
const DASH_LOG = 'dash_log';

export default class Environment {
    private static get searchParams() {
        return new URL(window.location.href).searchParams;
    }

    public static get debugLevel(): DebugLevel {
        const debug = this.searchParams.get(DASH_DEBUG) || CookieStorage.get(DASH_DEBUG);

        return debug ?
            (DebugLevel as any)[debug] || DebugLevel.NONE :
            DebugLevel.NONE;
    }

    public static get logLevel(): LogLevel {
        const log = this.searchParams.get(DASH_LOG) || CookieStorage.get(DASH_LOG);

        return log ?
            (LogLevel as any)[log] || LogLevel.ERROR :
            LogLevel.ERROR;
    }
}