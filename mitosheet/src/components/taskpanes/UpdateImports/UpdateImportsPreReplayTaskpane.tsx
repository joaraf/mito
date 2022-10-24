import React, { useState } from "react";
import MitoAPI from "../../../jupyter/api";
import { overwriteAnalysisToReplayToMitosheetCall } from "../../../jupyter/jupyterUtils";
import { AnalysisData, UIState } from "../../../types";
import { isMitoError } from "../../../utils/errors";
import TextButton from "../../elements/TextButton";
import Col from "../../layout/Col";
import Row from "../../layout/Row";
import Spacer from "../../layout/Spacer";
import DefaultTaskpane from "../DefaultTaskpane/DefaultTaskpane";
import DefaultTaskpaneBody from "../DefaultTaskpane/DefaultTaskpaneBody";
import DefaultTaskpaneFooter from "../DefaultTaskpane/DefaultTaskpaneFooter";
import DefaultTaskpaneHeader from "../DefaultTaskpane/DefaultTaskpaneHeader";
import { TaskpaneType } from "../taskpanes";
import ImportCard from "./UpdateImportCard";
import { FailedReplayData, ReplacingDataframeState, StepImportData } from "./UpdateImportsTaskpane";
import { getErrorTextFromToFix, getOriginalAndUpdatedDataframeCreationDataPairs } from "./updateImportsUtils";


interface UpdateImportPreReplayTaskpaneProps {
    mitoAPI: MitoAPI;
    analysisData: AnalysisData;
    setUIState: React.Dispatch<React.SetStateAction<UIState>>;

    updatedStepImportData: StepImportData[] | undefined;
    setUpdatedStepImportData: React.Dispatch<React.SetStateAction<StepImportData[] | undefined>>;

    updatedIndexes: number[];
    setUpdatedIndexes: React.Dispatch<React.SetStateAction<number[]>>;

    displayedImportCardDropdown: number | undefined
    setDisplayedImportCardDropdown: React.Dispatch<React.SetStateAction<number | undefined>>

    setReplacingDataframeState: React.Dispatch<React.SetStateAction<ReplacingDataframeState | undefined>>;

    postUpdateInvalidImportMessages: Record<number, string | undefined>;
    setPostUpdateInvalidImportMessages: React.Dispatch<React.SetStateAction<Record<number, string | undefined>>>;
    
    failedReplayData: FailedReplayData;
    importDataAndErrors: ImportDataAndImportErrors | undefined

    invalidReplayError: string | undefined;
    setInvalidReplayError: React.Dispatch<React.SetStateAction<string | undefined>>;
}
    

export interface ImportDataAndImportErrors {
    importData: StepImportData[],
    invalidImportMessages: Record<number, string | undefined>
}

export const PRE_REPLAY_IMPORT_ERROR_TEXT = 'Please fix failed data imports to replay analysis.';
export const SUCCESSFUL_REPLAY_ANALYSIS_TEXT = 'Successfully replayed analysis on new data.'


/* 
    This taskpane is displayed if the user replays an analysis
    that has some failed imports, that the user is then given
    the option to reconfigure to make them valid.
*/
const UpdateImportsPreReplayTaskpane = (props: UpdateImportPreReplayTaskpaneProps): JSX.Element => {

    const [loadingUpdate, setLoadingUpdate] = useState(false);
    const [displaySuccessMessage, setDisplaySuccessMessage] = useState(false);
    
    let updateImportBody: React.ReactNode = null;
    const loadingImportDataAndErrors = props.importDataAndErrors === undefined;

    if (props.importDataAndErrors === undefined) {
        updateImportBody = (
            <p>Loading previously imported data...</p>
        )
    } else {
        // We create an import card for each of the dataframes created within the original imports
        const originalAndUpdatedDataframeCreationPairs = getOriginalAndUpdatedDataframeCreationDataPairs(props.importDataAndErrors.importData, props.updatedStepImportData);
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
                    preUpdateInvalidImportMessage={props.importDataAndErrors?.invalidImportMessages[index]}
                    postUpdateInvalidImportMessage={props.postUpdateInvalidImportMessages[index]}
                />
            )
        })
    }


    const allErrorsUpdated = Object.keys(props.importDataAndErrors?.invalidImportMessages || {}).filter(index => !props.updatedIndexes.includes(parseInt(index))).length === 0;
    const invalidPostUpdate = Object.keys(props.postUpdateInvalidImportMessages).length > 0;

    const retryButtonDisabled = !allErrorsUpdated || invalidPostUpdate || loadingImportDataAndErrors || loadingUpdate;

    return (
        <DefaultTaskpane>
            <DefaultTaskpaneHeader 
                header="Change Imports to Replay Analysis"
                setUIState={props.setUIState}           
                notCloseable
            />
            <DefaultTaskpaneBody>
                {((props.invalidReplayError === PRE_REPLAY_IMPORT_ERROR_TEXT && !allErrorsUpdated) || (props.invalidReplayError !== undefined && props.invalidReplayError !== PRE_REPLAY_IMPORT_ERROR_TEXT)) && 
                    <p className="text-color-error">
                        {props.invalidReplayError}
                    </p>
                }
                {updateImportBody}
            </DefaultTaskpaneBody>
            <DefaultTaskpaneFooter>
                <Row justify="space-between">
                    <Col>
                        <TextButton
                            variant='light'
                            width='medium'
                            onClick={() => {    
                                overwriteAnalysisToReplayToMitosheetCall(
                                    props.failedReplayData.analysisName,
                                    props.analysisData.analysisName,
                                    props.mitoAPI
                                )
                                
                                props.setUIState((prevUIState) => {
                                    return {
                                        ...prevUIState,
                                        currOpenTaskpane: {type: TaskpaneType.NONE}
                                    }
                                })}
                            }
                            tooltip={"This will start a new analysis with no steps in this mitosheet."}
                        >
                            Start New Analysis
                        </TextButton>
                    </Col>
                    <Col span={12}>
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
                                    props.setPostUpdateInvalidImportMessages(_invalidImportIndexes);

                                    // If there are no invalid indexes, then we can update. Since this is
                                    // pre replay, we are replaying the analysis
                                    if (Object.keys(_invalidImportIndexes).length === 0) {

                                        props.setInvalidReplayError(undefined) // Clear the error

                                        const replayAnalysisError = await props.mitoAPI.updateReplayAnalysis(props.failedReplayData.analysisName, props.updatedStepImportData);
                                        // If there is an error replaying the analysis, we know it is not with 
                                        if (isMitoError(replayAnalysisError)) {
                                            props.setInvalidReplayError(getErrorTextFromToFix(replayAnalysisError.to_fix))
                                        } else {
                                            // Clear the error message if it exists
                                            props.setInvalidReplayError(undefined)
                                            // Show success message
                                            setDisplaySuccessMessage(true)
                                            // Since the stepIDs change when we replay the analysis on new data, we need to refresh
                                            // the importData so the user can update the imports again without throwing an error.
                                            const importData = await props.mitoAPI.getImportedFilesAndDataframesFromCurrentSteps();
                                            props.setUpdatedStepImportData(importData)
                                        }
                                    }
                                }

                                setLoadingUpdate(true);
                                await doUpdate();
                                setLoadingUpdate(false);

                            }}
                            disabled={retryButtonDisabled}
                            disabledTooltip={retryButtonDisabled ? "Please resolve all errors with above imports." : undefined}
                        >
                            <p>
                                {!loadingUpdate ? "Retry With Updated Imports" : "Updating Imports..."}
                            </p>
                        </TextButton>
                    </Col>
                </Row>
                {displaySuccessMessage && 
                    <p className='text-subtext-1'> 
                        {SUCCESSFUL_REPLAY_ANALYSIS_TEXT}
                    </p>
                }
                {!displaySuccessMessage && 
                    <Spacer px={16}/>
                }
            </DefaultTaskpaneFooter>
        </DefaultTaskpane>
    )
}

export default UpdateImportsPreReplayTaskpane;

