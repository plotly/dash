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
};

export function createPatchAnalysis(): PatchAnalysis {
    return {patchedProps: {}, freshIds: {}, writtenProps: {}};
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
