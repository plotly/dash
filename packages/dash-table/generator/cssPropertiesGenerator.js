const props = [
    'alignContent',
    'alignItems',
    'alignmentAdjust',
    'alignmentBaseline',
    'alignSelf',
    'animationDelay',
    'animationDirection',
    'animationIterationCount',
    'animationName',
    'animationPlayState',
    'appearance',
    'backfaceVisibility',
    'background',
    'backgroundAttachment',
    'backgroundBlendMode',
    'backgroundColor',
    'backgroundComposite',
    'backgroundImage',
    'backgroundOrigin',
    'backgroundPosition',
    'backgroundRepeat',
    'baselineShift',
    'behavior',
    'border',
    'borderBottom',
    'borderBottomColor',
    'borderBottomLeftRadius',
    'borderBottomRightRadius',
    'borderBottomStyle',
    'borderBottomWidth',
    'borderCollapse',
    'borderColor',
    'borderCornerShape',
    'borderImageSource',
    'borderImageWidth',
    'borderLeft',
    'borderLeftColor',
    'borderLeftStyle',
    'borderLeftWidth',
    'borderRight',
    'borderRightColor',
    'borderRightStyle',
    'borderRightWidth',
    'borderSpacing',
    'borderStyle',
    'borderTop',
    'borderTopColor',
    'borderTopLeftRadius',
    'borderTopRightRadius',
    'borderTopStyle',
    'borderTopWidth',
    'borderWidth',
    'bottom',
    'boxAlign',
    'boxDecorationBreak',
    'boxDirection',
    'boxFlex',
    'boxFlexGroup',
    'boxLineProgression',
    'boxLines',
    'boxOrdinalGroup',
    'boxShadow',
    'breakAfter',
    'breakBefore',
    'breakInside',
    'clear',
    'clip',
    'clipRule',
    'color',
    'columnCount',
    'columnFill',
    'columnGap',
    'columnRule',
    'columnRuleColor',
    'columnRuleWidth',
    'columns',
    'columnSpan',
    'columnWidth',
    'counterIncrement',
    'counterReset',
    'cue',
    'cueAfter',
    'cursor',
    'direction',
    'display',
    'fill',
    'fillOpacity',
    'fillRule',
    'filter',
    'flex',
    'flexAlign',
    'flexBasis',
    'flexDirection',
    'flexFlow',
    'flexGrow',
    'flexItemAlign',
    'flexLinePack',
    'flexOrder',
    'flexShrink',
    'flexWrap',
    'float',
    'flowFrom',
    'font',
    'fontFamily',
    'fontKerning',
    'fontSize',
    'fontSizeAdjust',
    'fontStretch',
    'fontStyle',
    'fontSynthesis',
    'fontVariant',
    'fontVariantAlternates',
    'fontWeight',
    'gridArea',
    'gridColumn',
    'gridColumnEnd',
    'gridColumnStart',
    'gridRow',
    'gridRowEnd',
    'gridRowPosition',
    'gridRowSpan',
    'gridTemplateAreas',
    'gridTemplateColumns',
    'gridTemplateRows',
    'height',
    'hyphenateLimitChars',
    'hyphenateLimitLines',
    'hyphenateLimitZone',
    'hyphens',
    'imeMode',
    'justifyContent',
    'layoutGrid',
    'layoutGridChar',
    'layoutGridLine',
    'layoutGridMode',
    'layoutGridType',
    'left',
    'letterSpacing',
    'lineBreak',
    'lineClamp',
    'lineHeight',
    'listStyle',
    'listStyleImage',
    'listStylePosition',
    'listStyleType',
    'margin',
    'marginBottom',
    'marginLeft',
    'marginRight',
    'marginTop',
    'marqueeDirection',
    'marqueeStyle',
    'mask',
    'maskBorder',
    'maskBorderRepeat',
    'maskBorderSlice',
    'maskBorderSource',
    'maskBorderWidth',
    'maskClip',
    'maskOrigin',
    'maxFontSize',
    'maxHeight',
    'maxWidth',
    'minHeight',
    'minWidth',
    'opacity',
    'order',
    'orphans',
    'outline',
    'outlineColor',
    'outlineOffset',
    'overflow',
    'overflowStyle',
    'overflowX',
    'overflowY',
    'padding',
    'paddingBottom',
    'paddingLeft',
    'paddingRight',
    'paddingTop',
    'pageBreakAfter',
    'pageBreakBefore',
    'pageBreakInside',
    'pause',
    'pauseAfter',
    'pauseBefore',
    'perspective',
    'perspectiveOrigin',
    'pointerEvents',
    'position',
    'punctuationTrim',
    'quotes',
    'regionFragment',
    'restAfter',
    'restBefore',
    'right',
    'rubyAlign',
    'rubyPosition',
    'shapeImageThreshold',
    'shapeInside',
    'shapeMargin',
    'shapeOutside',
    'speak',
    'speakAs',
    'strokeOpacity',
    'strokeWidth',
    'tableLayout',
    'tabSize',
    'textAlign',
    'textAlignLast',
    'textDecoration',
    'textDecorationColor',
    'textDecorationLine',
    'textDecorationLineThrough',
    'textDecorationNone',
    'textDecorationOverline',
    'textDecorationSkip',
    'textDecorationStyle',
    'textDecorationUnderline',
    'textEmphasis',
    'textEmphasisColor',
    'textEmphasisStyle',
    'textHeight',
    'textIndent',
    'textJustifyTrim',
    'textKashidaSpace',
    'textLineThrough',
    'textLineThroughColor',
    'textLineThroughMode',
    'textLineThroughStyle',
    'textLineThroughWidth',
    'textOverflow',
    'textOverline',
    'textOverlineColor',
    'textOverlineMode',
    'textOverlineStyle',
    'textOverlineWidth',
    'textRendering',
    'textScript',
    'textShadow',
    'textTransform',
    'textUnderlinePosition',
    'textUnderlineStyle',
    'top',
    'touchAction',
    'transform',
    'transformOrigin',
    'transformOriginZ',
    'transformStyle',
    'transition',
    'transitionDelay',
    'transitionDuration',
    'transitionProperty',
    'transitionTimingFunction',
    'unicodeBidi',
    'unicodeRange',
    'userFocus',
    'userInput',
    'verticalAlign',
    'visibility',
    'voiceBalance',
    'voiceDuration',
    'voiceFamily',
    'voicePitch',
    'voiceRange',
    'voiceRate',
    'voiceStress',
    'voiceVolume',
    'whiteSpace',
    'whiteSpaceTreatment',
    'widows',
    'width',
    'wordBreak',
    'wordSpacing',
    'wordWrap',
    'wrapFlow',
    'wrapMargin',
    'wrapOption',
    'writingMode',
    'zIndex',
    'zoom'
];

function toSnakeCase(name) {
    return name.replace(/[A-Z]/g, v => `_${v.toLowerCase()}`);
}

function toKebabCase(name) {
    return name.replace(/[A-Z]/g, v => `-${v.toLowerCase()}`);
}

const snakes = props.map(prop => [toSnakeCase(prop), prop]);
const kebabs = props.map(prop => [toKebabCase(prop), prop]);
const camels = props.map(prop => [prop, prop]);

const map = new Map();

snakes.forEach(([snake, camel]) => map.set(snake, camel));
kebabs.forEach(([kebab, camel]) => map.set(kebab, camel));
camels.forEach(([camel]) => map.set(camel, camel));

map.forEach((value, key) => console.log(value, key));
console.log(map.size);

const fs = require('fs');

var stream1 = fs.createWriteStream("src/dash-table/derived/style/py2jsCssProperties.ts");
stream1.once('open', () => {
    stream1.write('export type StyleProperty = string | number;\n');
    stream1.write('\n');
    stream1.write('export default new Map<string, string>([\n');

    let first = true;
    map.forEach((value, key) => {
        if (!first) {
            stream1.write(',\n');
        }

        first = false;
        stream1.write(`    ['${key}', '${value}']`);
    });
    stream1.write('\n]);')

    stream1.end();
});

var stream2 = fs.createWriteStream("src/dash-table/derived/style/IStyle.ts");
stream2.once('open', () => {
    stream2.write(`import { StyleProperty } from './ py2jsCssProperties';\n`);
    stream2.write('\n');
    stream2.write('export default interface IStyle {\n');
    camels.forEach(([key]) => {
        stream2.write(`    ${key}: StyleProperty;\n`);
    });
    stream2.write('}')

    stream2.end();
});

var stream3 = fs.createWriteStream("proptypes.js");
stream3.once('open', () => {
    let first = true;
    map.forEach((value, key) => {
        if (!first) {
            stream3.write(',\n');
        }

        first = false;
        if (key.indexOf('-') !== -1) {
            stream3.write(`    '${key}': PropTypes.oneOfType([PropTypes.string, PropTypes.number])`);
        } else {
            stream3.write(`    ${key}: PropTypes.oneOfType([PropTypes.string, PropTypes.number])`);
        }
    });
    stream3.write('\n')

    stream3.end();
});