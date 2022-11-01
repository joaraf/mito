// Copyright (c) Mito

import React, { useState } from 'react';
import MitoAPI from '../../jupyter/api';
import { overwriteAnalysisToReplayToMitosheetCall } from '../../jupyter/jupyterUtils';
import { MitoError, UIState, UserProfile } from '../../types';
import DefaultModal from '../DefaultModal';
import TextButton from '../elements/TextButton';
import { ModalEnum } from './modals';
import GetSupportButton from '../elements/GetSupportButton';



/*
    This modal displays to the user when:
    1. the analysis that they are replaying does not exist on their computer
    2. the analysis errors during replay for some other reason
*/
const ErrorReplayedAnalysisModal = (
    props: {
        setUIState: React.Dispatch<React.SetStateAction<UIState>>;
        mitoAPI: MitoAPI,
        userProfile: UserProfile,

        header: string,
        message: string,
        error: MitoError | undefined,

        oldAnalysisName: string;
        newAnalysisName: string;
    }): JSX.Element => {

    const [viewTraceback, setViewTraceback] = useState(false);

    return (
        <DefaultModal
            header={props.header}
            modalType={ModalEnum.Error}
            wide
            viewComponent={
                <>
                    <div className='text-align-left text-body-1' onClick={() => setViewTraceback((viewTraceback) => !viewTraceback)}>
                        {props.message} {' '}
                        {props.error?.traceback && 
                            <span className='text-body-1-link'>
                                Click to view full traceback.
                            </span>
                        }
                    </div>
                    {props.error?.traceback && viewTraceback &&
                        <div className='text-align-left text-overflow-hidden text-overflow-scroll mt-5px' style={{height: '200px', border: '1px solid var(--mito-purple)', borderRadius: '2px', padding: '5px'}}>
                            <pre>{props.error.traceback}</pre>
                        </div>
                    }
                </>
            }
            buttons={
                <>
                    <GetSupportButton 
                        userProfile={props.userProfile} 
                        setUIState={props.setUIState} 
                        mitoAPI={props.mitoAPI}
                        onClick={() => {
                            void props.mitoAPI.log('clicked_get_support_button')
                            return true;
                        }}
                    />
                    <TextButton
                        variant='dark'
                        width='medium'
                        onClick={() => {    
                            overwriteAnalysisToReplayToMitosheetCall(
                                props.oldAnalysisName,
                                props.newAnalysisName,
                                props.mitoAPI
                            )
                            
                            props.setUIState((prevUIState) => {
                                return {
                                    ...prevUIState,
                                    currOpenModal: {type: ModalEnum.None}
                                }
                            })}
                        }
                    >
                        Start New Analysis
                    </TextButton>
                </> 
            }
        />
    )    
};

export default ErrorReplayedAnalysisModal;