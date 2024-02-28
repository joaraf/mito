import Link from 'next/link';
import CodeBlock from '../CodeBlock/CodeBlock';
import ctaButtons from '../CTAButtons/CTAButtons.module.css'
import installInstructions from './InstallInstructions.module.css'
import pageStyles from '../../styles/Home.module.css';
import { CREATE_MITOSHEET_DOCS_LINK, MITO_INSTALLATION_DOCS_LINK } from '../Header/Header';
import { MITO_GITHUB_LINK } from '../GithubButton/GithubButton';
import { PLAUSIBLE_COPIED_MITOSHEET_HELLO_COMMAND, PLAUSIBLE_COPIED_PIP_INSTALL_COMMAND } from '../../utils/plausible';
import { classNames } from '../../utils/classNames';
import { DISCORD_LINK } from '../Footer/Footer';


const InstallInstructions = (props: {}): JSX.Element => {
    return (
        <>
            <h2 style={{textAlign: 'center'}}>
                Install <span className='text-highlight'><a className={pageStyles.link} href={MITO_GITHUB_LINK} target="_blank" rel="noreferrer">open-source</a></span> Mito <br/>
                in two simple steps
            </h2>
            <div className={installInstructions.install_instructions_container}>
                <CodeBlock prefix='$ ' paddingRight='7rem' className={PLAUSIBLE_COPIED_PIP_INSTALL_COMMAND}>
                    pip install mitosheet
                </CodeBlock>
                <CodeBlock prefix='$ ' paddingRight='7rem' className={PLAUSIBLE_COPIED_MITOSHEET_HELLO_COMMAND}>
                    python -m mitosheet hello
                </CodeBlock>
                <div className={classNames('text-primary', ctaButtons.pro_cta_text)}>
                    Then, check out our {" "}
                    <Link href={CREATE_MITOSHEET_DOCS_LINK}>
                        <a className={ctaButtons.cta_subbutton} target="_blank" rel="noreferrer">
                            documentation
                        </a>
                    </Link>
                    {" "}and {" "} 
                    <Link href={DISCORD_LINK}>
                        <a className={ctaButtons.cta_subbutton} target="_blank" rel="noreferrer">
                            discord.
                        </a>
                    </Link>
                </div>
            </div>
        </>
    )
}

export default InstallInstructions;