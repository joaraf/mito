import React, { useState } from "react";
import MitoAPI from "../../../jupyter/api";
import { PopupLocation, PopupType, SheetData, UIState } from "../../../types";
import { isMitoError } from "../../../utils/errors";
import TextButton from "../../elements/TextButton";
import DefaultEmptyTaskpane from "../DefaultTaskpane/DefaultEmptyTaskpane";
import DefaultTaskpane from "../DefaultTaskpane/DefaultTaskpane";
import DefaultTaskpaneBody from "../DefaultTaskpane/DefaultTaskpaneBody";
import DefaultTaskpaneFooter from "../DefaultTaskpane/DefaultTaskpaneFooter";
import DefaultTaskpaneHeader from "../DefaultTaskpane/DefaultTaskpaneHeader";
import { TaskpaneType } from "../taskpanes";
import ImportCard from "./UpdateImportCard";
import { ImportDataAndImportErrors } from "./UpdateImportsPreReplayTaskpane";
import { ReplacingDataframeState, StepImportData } from "./UpdateImportsTaskpane";
import { getErrorTextFromToFix, getOriginalAndUpdatedDataframeCreationDataPairs } from "./updateImportsUtils";


interface UpdateImportPostReplayTaskpaneProps {
    mitoAPI: MitoAPI;
    sheetDataArray: SheetData[];
    setUIState: React.Dispatch<React.SetStateAction<UIState>>;

    updatedStepImportData: StepImportData[] | undefined;
    setUpdatedStepImportData: React.Dispatch<React.SetStateAction<StepImportData[] | undefined>>;

    updatedIndexes: number[];
    setUpdatedIndexes: React.Dispatch<React.SetStateAction<number[]>>;
    
    displayedImportCardDropdown: number | undefined
    setDisplayedImportCardDropdown: React.Dispatch<React.SetStateAction<number | undefined>>

    setReplacingDataframeState: React.Dispatch<React.SetStateAction<ReplacingDataframeState | undefined>>;

    invalidImportMessages: Record<number, string | undefined>;
    setInvalidImportMessages: React.Dispatch<React.SetStateAction<Record<number, string | undefined>>>;

    importDataAndErrors: ImportDataAndImportErrors | undefined;

    invalidReplayError: string | undefined;
    setInvalidReplayError: React.Dispatch<React.SetStateAction<string | undefined>>;
}
    

/* 
    This taskpane is displayed if the user wants to change the imported
    data after they have a full valid analysis.
*/
const UpdateImportsPostReplayTaskpane = (props: UpdateImportPostReplayTaskpaneProps): JSX.Element => {

    const [loadingUpdate, setLoadingUpdate] = useState(false);

    let updateImportBody: React.ReactNode = null;
    if (props.importDataAndErrors === undefined) {
        updateImportBody = (
            <p>Loading previously imported data...</p>
        )
    } else {

        // Show a different empty taskpane message depending if you passed a dataframe or not
        if ((props.importDataAndErrors?.importData.length || 0) === 0 && props.sheetDataArray.length === 0) {
            return <DefaultEmptyTaskpane setUIState={props.setUIState} message='Before changing imports, you need to import something.'/>
        } else if ((props.importDataAndErrors?.importData.length || 0) === 0) {
            return <DefaultEmptyTaskpane header='Update passed dataframes' setUIState={props.setUIState} message='You can change imports by changing the data passed to the mitosheet.sheet call above.' suppressImportLink/>

        }

        // We create an import card for each of the dataframes created within the original imports
        const originalAndUpdatedDataframeCreationPairs = getOriginalAndUpdatedDataframeCreationDataPairs(props.importDataAndErrors?.importData || [], props.updatedStepImportData);
        updateImportBody = originalAndUpdatedDataframeCreationPairs.map(([originalDfCreationData, updatedDfCreationData], index) => {
            return (
                <ImportCard 
                    key={index}
                    dataframeCreationIndex={index}
                    dataframeCreationData={originalDfCreationData}
                    isUpdated={props.updatedIndexes.includes(index)}
                    updatedDataframeCreationData={updatedDfCreationData}
                    displayedImportCardDropdown={props.displayedImportCardDropdown}
                    setDisplayedImportCardDropdown={props.setDisplayedImportCardDropdown}
                    setReplacingDataframeState={props.setReplacingDataframeState}
                    preUpdateInvalidImportMessage={undefined}
                    postUpdateInvalidImportMessage={props.invalidImportMessages[index]}
                />
            )
        })
    }
    
   

    const anyUpdated = props.updatedIndexes.length > 0;
    const invalidPostUpdate = Object.keys(props.invalidImportMessages).length > 0;

    const retryButtonDisabled = !anyUpdated || invalidPostUpdate || loadingUpdate;

    return (
        <DefaultTaskpane>
            <DefaultTaskpaneHeader 
                header="Change Imports"
                setUIState={props.setUIState}           
            />
            <DefaultTaskpaneBody>
                {props.invalidReplayError &&
                    <p className="text-color-error">
                        {props.invalidReplayError}
                    </p>
                }
                {updateImportBody}
            </DefaultTaskpaneBody>
            <DefaultTaskpaneFooter>
                <TextButton 
                    variant="dark"
                    onClick={async () => {
                        const doUpdate = async () => {
                            if (props.updatedStepImportData === undefined) {
                                return
                            }
                            const _invalidImportIndexes = await props.mitoAPI.getTestImports(props.updatedStepImportData);
                            if (_invalidImportIndexes === undefined) {
                                return;
                            }
                            props.setInvalidImportMessages(_invalidImportIndexes);

                            // If there are no invalid indexes, then we can update. Since this is
                            // post replay, we are updating the existing imports
                            if (Object.keys(_invalidImportIndexes).length === 0) {
                                const possibleMitoError = await props.mitoAPI.updateExistingImports(props.updatedStepImportData);
                                if (isMitoError(possibleMitoError)) {
                                    props.setInvalidReplayError(getErrorTextFromToFix(possibleMitoError.to_fix))
                                } else {
                                    props.setUIState((prevUIState) => {
                                        return {
                                            ...prevUIState,
                                            currOpenTaskpane: {type: TaskpaneType.NONE},
                                            currOpenPopups: {
                                                ...prevUIState.currOpenPopups,
                                                [PopupLocation.TopRight]: {
                                                    type: PopupType.EphemeralMessage, 
                                                    message: 'Successfully replayed analysis on new data'
                                                }
                                            }
                                        }
                                    })
                                }
                            }
                        }

                        setLoadingUpdate(true);
                        await doUpdate();
                        setLoadingUpdate(false);
                    }}
                    disabled={retryButtonDisabled}
                    disabledTooltip={(retryButtonDisabled) ? "Please resolve all errors with above imports." : undefined}
                >
                    <p>
                        {!loadingUpdate ? "Change Imports" : "Changing Imports..."}
                    </p>
                </TextButton>
            </DefaultTaskpaneFooter>
        </DefaultTaskpane>
    )
}

export default UpdateImportsPostReplayTaskpane;
