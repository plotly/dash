/**
 * Captures CSS variables and key inherited properties from a container element for use in portaled content.
 * When content is portaled outside its normal DOM hierarchy (e.g., to document.body),
 * it loses access to CSS variables defined on parent elements and inherited properties.
 * This function extracts those so they can be applied as inline styles.
 */
export function captureCSSForPortal(
    containerRef: React.RefObject<HTMLElement>,
    prefix = '--Dash-'
): Record<string, string> {
    if (typeof window === 'undefined') {
        return {};
    }

    const element = containerRef.current || document.documentElement;
    const computedStyle = window.getComputedStyle(element);
    const styles: Record<string, string> = {};

    // Capture CSS variables (custom properties starting with prefix)
    for (let i = 0; i < computedStyle.length; i++) {
        const prop = computedStyle[i];
        if (prop.startsWith(prefix)) {
            styles[prop] = computedStyle.getPropertyValue(prop);
        }
    }

    // Capture key inherited properties
    const inheritedProps = ['font-family', 'font-size', 'color'];
    inheritedProps.forEach(prop => {
        const value = computedStyle.getPropertyValue(prop);
        if (value) {
            // Convert hyphenated CSS property names to camelCase for React
            const camelCaseProp = prop.replace(/-([a-z])/g, (_, letter) =>
                letter.toUpperCase()
            );
            styles[camelCaseProp] = value;
        }
    });

    return styles;
}
