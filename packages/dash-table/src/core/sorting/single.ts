import Logger from 'core/Logger';
import { SortSettings, ISortSetting, SortDirection } from 'core/sorting';

export default (
    settings: SortSettings,
    setting: ISortSetting
): SortSettings => {
    Logger.trace('single - updateSettings', settings, setting);

    return setting.direction === SortDirection.None ?
        [] :
        [setting];
};