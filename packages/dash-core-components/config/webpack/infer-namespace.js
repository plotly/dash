var path = require('path');

/**
 * Infers a module under build's namespace by taking the module's directory
 * (e.g. /home/user/dev/dash-core-components) and parsing the path,
 * using the last part of the path. Replaces dashes with underscores.
 *
 * Example `dash-core-components` -> `dash_core_components`
 *
 * @param   {string} modulePath The component suite path
 * @returns {string} The module's namespace
 */
module.exports = function (modulePath) {
    var parts = path.parse(modulePath);
    return parts.name.replace(/\-/g, '_');
};
