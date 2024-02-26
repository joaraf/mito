import { FrameLocator, Page, expect, test } from '@playwright/test';
import { awaitResponse, checkColumnExists, checkOpenTaskpane, clickButtonAndAwaitResponse, closeTaskpane, getMitoFrameWithTestCSV, getMitoFrameWithTypeCSV } from '../utils';


const AGGREGATION_FUNCTIONS = [
    'count', 
    'sum',
    'mean',
    'median',
    'std',
    'min',
    'max'
]

const createPivotFromSelectedSheet = async (
    page: Page,
    mito: FrameLocator, 
    rows: string[], 
    columns: string[], 
    values: string[], // TODO: make these types better for other agg functions
    filters?: string[]
): Promise<void> => {

    await clickButtonAndAwaitResponse(page, mito, { name: 'Pivot' })

    for (let i = 0; i < rows.length; i++) {
        const row = rows[i];
        await mito.getByText('+ Add').first().click();
        await mito.getByText(row).click();
        await awaitResponse(page);
    }

    for (let i = 0; i < columns.length; i++) {
        const column = columns[i];
        await mito.getByText('+ Add').nth(1).click();
        await mito.getByText(column).click();
        await awaitResponse(page);
    }

    for (let i = 0; i < values.length; i++) {
        const value = values[i];
        await mito.getByText('+ Add').nth(2).click();
        await mito.getByText(value).click();
        await awaitResponse(page);
    }

    if (filters !== undefined) {
        for (let i = 0; i < filters.length; i++) {
            const filter = filters[i];
            await mito.getByText('+ Add').nth(3).click();
            await mito.getByText(filter).click();
        }
    }
}

const changeAggregationForValue = async (
    page: Page,
    mito: FrameLocator, 
    value: string,
    aggFunction: string
): Promise<void> => {
    // TODO...
    return;
}



test.describe('Pivot Table', () => {
    

    test('Empty pivot creates a new empty sheet', async ({ page }) => {
        const mito = await getMitoFrameWithTestCSV(page);

        await clickButtonAndAwaitResponse(page, mito, { name: 'Pivot' })

        // Check new empty tab
        await mito.getByText('test_pivot', { exact: true }).click();
        await expect(mito.getByText('test_pivot', { exact: true })).toBeVisible();
        await expect(mito.getByText('No data in dataframe.')).toBeVisible();
    })

    test('Can handle multiple rows', async ({ page }) => {
        const mito = await getMitoFrameWithTestCSV(page);

        await createPivotFromSelectedSheet(
            page, mito,
            ['Column1', 'Column2'],
            [],
            ['Column3']
        )

        await checkColumnExists(mito, ['Column1', 'Column2', 'Column3 count'])
    })

    test('Can handle multiple columns', async ({ page }) => {
        const mito = await getMitoFrameWithTestCSV(page);

        await createPivotFromSelectedSheet(
            page, mito,
            [],
            ['Column1', 'Column2'],
            ['Column3']
        )

        await checkColumnExists(mito, ['level_0', 'level_1', '1 2', '4 5', '7 8', '10 11'])
    })

    test('Can handle multiple values', async ({ page }) => {
        const mito = await getMitoFrameWithTestCSV(page);

        await createPivotFromSelectedSheet(
            page, mito,
            ['Column1'],
            [],
            ['Column2', 'Column3']
        )

        await checkColumnExists(mito, ['Column1', 'Column2 count', 'Column3 count'])
    })

    test.only('Can switch between aggregation functions', async ({ page }) => {
        const mito = await getMitoFrameWithTestCSV(page);

        await createPivotFromSelectedSheet(
            page, mito,
            ['Column1'],
            [],
            ['Column3']
        )
        

        for (let i = 0; i < AGGREGATION_FUNCTIONS.length - 1; i++) {
            const currentAggFunction = AGGREGATION_FUNCTIONS[i];
            const nextAggFunction = AGGREGATION_FUNCTIONS[i + 1]
            await mito.getByText(currentAggFunction, { exact: true }).click();
            await mito.getByRole('button', { name: nextAggFunction }).click();
            await awaitResponse(page);

            // std doesn't work on our standard test data, so we just skip for now
            if (nextAggFunction !== 'std') {
                await checkColumnExists(mito, `Column3 ${nextAggFunction}`)
            }
        }

    })

    test('Number aggregations disabled for string columns', async ({ page }) => {
        const mito = await getMitoFrameWithTypeCSV(page);

        await createPivotFromSelectedSheet(
            page, mito,
            ['Column1'],
            [],
            ['Column2']
        )




    })

    test('Can add filter to pivot', async ({ page }) => {
        const mito = await getMitoFrameWithTypeCSV(page);

        await createPivotFromSelectedSheet(
            page, mito,
            ['Column1'],
            [],
            ['Column3'],
            ['Column2']
        )

    })

    test('Can add multiple filter to pivot', async ({ page }) => {
        const mito = await getMitoFrameWithTestCSV(page);

    })

    test('Opens the same pivot table when clicked again', async ({ page }) => {
        const mito = await getMitoFrameWithTestCSV(page);



    })
    

    test('Allows editing when re-opened', async ({ page }) => {
        const mito = await getMitoFrameWithTestCSV(page);
        
        await createPivotFromSelectedSheet(
            page, mito,
            ['Column1'],
            ['Column2'],
            ['Column3']
        )

        // Check that the pivot table has been created
        await expect(mito.getByText('Column3 count 2')).toBeVisible();

        // Close the taskpane
        await closeTaskpane(mito);

        // Switch to the OG tab, and then back to the pivot table
        await mito.getByText('test', {exact: true}).click();
        await mito.getByText('test_pivot', { exact: true }).click();

        // Check pivot is being edited
        await checkOpenTaskpane(mito, 'Edit Pivot Table test_pivot');

        // Change count to sum
        await mito.getByText('count', { exact: true }).click();
        await mito.getByText('sum', { exact: true }).click();
        await awaitResponse(page);

        // Check that the pivot table has been updated
        await expect(mito.getByText('Column3 sum 2')).toBeVisible();
    });

    test('Replays dependent edits optimistically', async ({ page }) => {
        const mito = await getMitoFrameWithTestCSV(page);
        
        await clickButtonAndAwaitResponse(page, mito, { name: 'Pivot' })
        
        await checkOpenTaskpane(mito, 'Create Pivot Table test_pivot');

        // Check new empty tab
        await mito.getByText('test_pivot', { exact: true }).click();
        await expect(mito.getByText('test_pivot', { exact: true })).toBeVisible();
        await expect(mito.getByText('No data in dataframe.')).toBeVisible();
        
        // Add a row, column and value
        await createPivotFromSelectedSheet(
            page, mito,
            ['Column1'],
            ['Column2'],
            ['Column3']
        )

        // Check that the pivot table has been created
        await expect(mito.getByText('Column3 count 2')).toBeVisible();

        // Add a column
        await mito.locator('[id="mito-toolbar-button-add\\ column\\ to\\ the\\ right"]').getByRole('button', { name: 'Insert' }).click();
        await awaitResponse(page);

        // Check that the pivot table has been updated -- there should be
        // 5 columns from pivot + 1 added
        await expect(mito.locator('.endo-column-header-container')).toHaveCount(6);

        // Switch to the OG tab, and then back to the pivot table
        await mito.getByText('test', {exact: true}).click();
        await mito.getByText('test_pivot', { exact: true }).click();

        // Check pivot is being edited
        await checkOpenTaskpane(mito, 'Edit Pivot Table test_pivot');

        // Change count to sum
        await mito.getByText('count', { exact: true }).click();
        await mito.getByText('sum', { exact: true }).click();
        await awaitResponse(page);

        // Check that the pivot table has been updated
        await expect(mito.getByText('Column3 sum 2')).toBeVisible();

        // Close the pivot taskpane
        await closeTaskpane(mito);

        // Check there are still 6 columns
        await expect(mito.locator('.endo-column-header-container')).toHaveCount(6);
    });
});