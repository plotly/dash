import CookieStorage from 'core/storage/Cookie';
import {DebugLevel, LogLevel} from 'core/Logger';

import {Edge} from 'dash-table/derived/edges/type';

const DASH_DEBUG = 'dash_debug';
const DASH_LOG = 'dash_log';

interface ISearchParams {
    get: (key: string) => string | null;
}

export default class Environment {
    private static readonly _supportsCssVariables = Boolean(
        window.CSS?.supports?.('.some-selector', 'var(--some-var)')
    );
    private static readonly _activeEdge: Edge =
        Environment._supportsCssVariables
            ? '1px solid var(--accent)'
            : '1px solid hotpink';

    public static get searchParams(): ISearchParams {
        return (
            (typeof URL !== 'undefined' &&
                URL.prototype &&
                URL.prototype.constructor &&
                new URL(window.location.href).searchParams) || {get: () => null}
        );
    }

    public static get debugLevel(): DebugLevel {
        const debug =
            this.searchParams.get(DASH_DEBUG) || CookieStorage.get(DASH_DEBUG);

        return debug
            ? (DebugLevel as any)[debug] || DebugLevel.NONE
            : DebugLevel.NONE;
    }

    public static get logLevel(): LogLevel {
        const log =
            this.searchParams.get(DASH_LOG) || CookieStorage.get(DASH_LOG);

        return log ? (LogLevel as any)[log] || LogLevel.ERROR : LogLevel.ERROR;
    }

    public static get defaultEdge(): Edge {
        return '1px solid #d3d3d3';
    }

    public static get activeEdge(): Edge {
        return Environment._activeEdge;
    }

    public static get supportsCssVariables(): boolean {
        return Environment._supportsCssVariables;
    }
}
