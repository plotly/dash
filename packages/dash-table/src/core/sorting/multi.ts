import * as R from 'ramda';

import Logger from 'core/Logger';
import { SortSettings, ISortSetting, SortDirection } from 'core/sorting';

export default (
    settings: SortSettings,
    setting: ISortSetting
): SortSettings => {
    Logger.trace('multi - updateSettings', settings, setting);

    settings = R.clone(settings);

    if (setting.direction === SortDirection.None) {
        const currentIndex = R.findIndex(s => s.columnId === setting.columnId, settings);

        if (currentIndex !== -1) {
            settings.splice(currentIndex, 1);
        }
    } else {
        const currentSetting = R.find(s => s.columnId === setting.columnId, settings);

        if (currentSetting) {
            currentSetting.direction = setting.direction;
        } else {
            settings.push(setting);
        }
    }

    return settings;
};