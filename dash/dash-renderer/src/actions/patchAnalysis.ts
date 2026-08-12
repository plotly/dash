/*
 * "What did the patch actually change?"
 *
 * Patches are applied with ramda's `assocPath`/`dissocPath`, which
 * shallow-clone every object along the path they touch. So after a patch the
 * only thing reference identity tells us is "this object is not on the path
 * the patch walked". It cannot distinguish a component the patch created from
 * a container that merely sits between the patched prop and the value that
 * changed, because both end up with a brand new `props` object
 *
 * * `freshIds`: components the patch inserted into the tree. New
 *   instances even when they reuse an id that was already on the page, so
 *   their initial callbacks must run and their persisted user edits must be
 *   restored
 * * `writtenProps`: props the patch wrote directly on a component that already
 *   existed (`p[0]['props']['value'] = 5`). The component was not recreated,
 *   but the server did provide a new value for that prop, which persistence
 *   needs to know about to detect a server override
 *
 * Everything else in the resulting tree was carried over from the previous
 * layout, whatever its `props` reference says
 */
export type PatchAnalysis = {
    /*
     * Props of the output component that were produced by a Patch. The rest of
     * this analysis only describes those props: other props of the same output
     * are regular values which fully replace what was there
     */
    patchedProps: {[property: string]: true};
    /* Stringified ids of the components the patch inserted. */
    freshIds: {[idStr: string]: true};
    /* Props the patch wrote on components that already existed. */
    writtenProps: {[idStr: string]: {[property: string]: true}};
    /*
     * For a property whose value is a list: how many items were added at the
     * tail (Append/Extend, at the top level of that property's value) by this
     * patch, if that's *all* this patch did to the list. `false` means the
     * patch also did something else to it (Insert/Prepend/Delete/Remove/
     * Clear/Reverse/Assign, or wrote into a nested location) - the old items
     * can no longer be assumed to have kept their positions, so the property
     * is not eligible for the append-only paths shortcut.
     */
    tailAppends: {[property: string]: number | false};
};

export function createPatchAnalysis(): PatchAnalysis {
    return {patchedProps: {}, freshIds: {}, writtenProps: {}, tailAppends: {}};
}

/*
 * The analysis, but only if `property` is one of the props it describes.
 * A callback can return a Patch for one prop and a full value for another, and
 * a full value is a fresh sub-tree in which nothing was carried over
 */
export function analysisForProp(
    analysis: PatchAnalysis | undefined,
    property: string
): PatchAnalysis | undefined {
    return analysis?.patchedProps[property] ? analysis : undefined;
}

/*
 * For consumers that look at several props of an output at once, the
 * analysis only applies if every one of them came from a Patch
 */
export function analysisForAllProps(
    analysis: PatchAnalysis | undefined,
    properties: (string | number)[]
): PatchAnalysis | undefined {
    return analysis &&
        properties.length &&
        properties.every(property => analysis.patchedProps[property])
        ? analysis
        : undefined;
}

/*
 * Was this component already in the layout before the patch?
 * Without an analysis the chunk did not come from a patch, so
 * nothing was carried over, so every component is new
 */
export function isCarriedOverByPatch(
    analysis: PatchAnalysis | undefined,
    idStr: string | undefined | null
): boolean {
    if (!analysis || !idStr) {
        return false;
    }
    return !analysis.freshIds[idStr];
}

/*
 * Stricter version of `isCarriedOverByPatch` for persistence where a component
 * was kept and the patch did not write any prop on. These components still hold
 * user edits in Redux, so persistence must leave it alone
 */
export function isUntouchedByPatch(
    analysis: PatchAnalysis | undefined,
    idStr: string | undefined | null
): boolean {
    if (!analysis || !idStr) {
        return false;
    }
    return !analysis.freshIds[idStr] && !analysis.writtenProps[idStr];
}

/*
 * Did the patch write directly on this prop of a component it did not
 * recreate? This can be true for a component whose own initial call stays
 * suppressed by `isCarriedOverByPatch`, it's not fresh, even though one of
 * its props changed, callbacks that depend on that prop as an Input
 * still need to run
 */
export function wasWrittenByPatch(
    analysis: PatchAnalysis | undefined,
    idStr: string | undefined | null,
    property: string
): boolean {
    if (!analysis || !idStr) {
        return false;
    }
    return Boolean(analysis.writtenProps[idStr]?.[property]);
}

/*
 * How many items this patch appended to the tail of `property`'s list, if
 * appending (Append/Extend) is *all* it did to that list - the shortcut
 * paths.js needs to compute paths only for the new items instead of
 * re-crawling every pre-existing one. 0 when the analysis doesn't cover this
 * property, or when the patch touched the list in some other way.
 */
export function tailAppendCount(
    analysis: PatchAnalysis | undefined,
    property: string
): number {
    const count = analysis?.tailAppends[property];
    return typeof count === 'number' ? count : 0;
}
