import sort, { updateSettings, SortDirection, SortSettings } from 'core/sorting';

describe('sort', () => {
    it('sorts', () => {
        const data = [[1], [3], [4], [2]];
        const sorted = sort(
            data,
            [{ columnId: 0, direction: SortDirection.Descending }]
        );

        expect(sorted.length).to.equal(data.length);
        expect(sorted[0][0]).to.equal(4);
        expect(sorted[1][0]).to.equal(3);
        expect(sorted[2][0]).to.equal(2);
        expect(sorted[3][0]).to.equal(1);
    });

    it('sorts undefined after when descending', () => {
        const data = [[1], [undefined], [3], [undefined], [4], [2], [undefined]];

        const sorted = sort(
            data,
            [{ columnId: 0, direction: SortDirection.Descending }]
        );

        expect(sorted.length).to.equal(data.length);
        expect(sorted[0][0]).to.equal(4);
        expect(sorted[1][0]).to.equal(3);
        expect(sorted[2][0]).to.equal(2);
        expect(sorted[3][0]).to.equal(1);
        expect(sorted[4][0]).to.equal(undefined);
        expect(sorted[5][0]).to.equal(undefined);
        expect(sorted[6][0]).to.equal(undefined);
    });

    it('sorts undefined after when ascending', () => {
        const data = [[1], [undefined], [3], [undefined], [4], [2], [undefined]];

        const sorted = sort(
            data,
            [{ columnId: 0, direction: SortDirection.Ascending }]
        );

        expect(sorted.length).to.equal(data.length);
        expect(sorted[0][0]).to.equal(1);
        expect(sorted[1][0]).to.equal(2);
        expect(sorted[2][0]).to.equal(3);
        expect(sorted[3][0]).to.equal(4);
        expect(sorted[4][0]).to.equal(undefined);
        expect(sorted[5][0]).to.equal(undefined);
        expect(sorted[6][0]).to.equal(undefined);
    });

    it('sorts null after when descending', () => {
        const data = [[1], [null], [3], [null], [4], [2], [null]];

        const sorted = sort(
            data,
            [{ columnId: 0, direction: SortDirection.Descending }]
        );

        expect(sorted.length).to.equal(data.length);
        expect(sorted[0][0]).to.equal(4);
        expect(sorted[1][0]).to.equal(3);
        expect(sorted[2][0]).to.equal(2);
        expect(sorted[3][0]).to.equal(1);
        expect(sorted[4][0]).to.equal(null);
        expect(sorted[5][0]).to.equal(null);
        expect(sorted[6][0]).to.equal(null);
    });

    it('sorts null after when ascending', () => {
        const data = [[1], [null], [3], [null], [4], [2], [null]];

        const sorted = sort(
            data,
            [{ columnId: 0, direction: SortDirection.Ascending }]
        );

        expect(sorted.length).to.equal(data.length);
        expect(sorted[0][0]).to.equal(1);
        expect(sorted[1][0]).to.equal(2);
        expect(sorted[2][0]).to.equal(3);
        expect(sorted[3][0]).to.equal(4);
        expect(sorted[4][0]).to.equal(null);
        expect(sorted[5][0]).to.equal(null);
        expect(sorted[6][0]).to.equal(null);
    });

    it('respects sort order - 1', () => {
        const data = [
            [1, 3],
            [2, 3],
            [0, 0],
            [0, 3],
            [0, 1],
            [2, 1],
            [1, 0],
            [1, 1],
            [2, 0]
        ];

        const sorted = sort(
            data,
            [
                { columnId: 0, direction: SortDirection.Descending },
                { columnId: 1, direction: SortDirection.Descending }
            ]
        );

        expect(sorted.length).to.equal(data.length);
        expect(sorted[0][0]).to.equal(2);
        expect(sorted[0][1]).to.equal(3);
        expect(sorted[1][0]).to.equal(2);
        expect(sorted[1][1]).to.equal(1);
        expect(sorted[2][0]).to.equal(2);
        expect(sorted[2][1]).to.equal(0);
    });

    it('respects sort order - 2', () => {
        const data = [
            [1, 3],
            [2, 3],
            [0, 0],
            [0, 3],
            [0, 1],
            [2, 1],
            [1, 0],
            [1, 1],
            [2, 0]
        ];

        const sorted = sort(
            data,
            [
                { columnId: 1, direction: SortDirection.Descending },
                { columnId: 0, direction: SortDirection.Ascending }
            ]
        );

        expect(sorted.length).to.equal(data.length);
        expect(sorted[0][0]).to.equal(0);
        expect(sorted[0][1]).to.equal(3);
        expect(sorted[1][0]).to.equal(1);
        expect(sorted[1][1]).to.equal(3);
        expect(sorted[2][0]).to.equal(2);
        expect(sorted[2][1]).to.equal(3);
    });
});

describe('sorting settings', () => {
    it('new descending', () => {
        const settings = updateSettings([], { columnId: 0, direction: SortDirection.Descending });

        expect(settings.length).to.equal(1);
        expect(settings[0].columnId).to.equal(0);
        expect(settings[0].direction).to.equal(SortDirection.Descending);
    });

    it('update to descending', () => {
        const settings = updateSettings(
            [{ columnId: 0, direction: SortDirection.Ascending }],
            { columnId: 0, direction: SortDirection.Descending }
        );

        expect(settings.length).to.equal(1);
        expect(settings[0].columnId).to.equal(0);
        expect(settings[0].direction).to.equal(SortDirection.Descending);
    });

    it('remove by setting to None', () => {
        const settings = updateSettings(
            [{ columnId: 0, direction: SortDirection.Ascending }],
            { columnId: 0, direction: SortDirection.None }
        );

        expect(settings.length).to.equal(0);
    });

    it('respects order', () => {
        const settings = updateSettings(
            [{ columnId: 0, direction: SortDirection.Ascending }],
            { columnId: 1, direction: SortDirection.Ascending }
        );

        expect(settings.length).to.equal(2);
        expect(settings[0].columnId).to.equal(0);
        expect(settings[1].columnId).to.equal(1);
    });

    it('respects order when removed and added back', () => {
        let settings: SortSettings = [{ columnId: 0, direction: SortDirection.Ascending }];

        settings = updateSettings(
            settings,
            { columnId: 1, direction: SortDirection.Ascending }
        );

        settings = updateSettings(
            settings,
            { columnId: 0, direction: SortDirection.None }
        );

        settings = updateSettings(
            settings,
            { columnId: 0, direction: SortDirection.Ascending }
        );

        expect(settings.length).to.equal(2);
        expect(settings[0].columnId).to.equal(1);
        expect(settings[1].columnId).to.equal(0);
    });
});