from mitoinstaller.commands import (get_jupyterlab_metadata,
                                    install_pip_packages)
from mitoinstaller.installer_steps.installer_step import InstallerStep


def install_step_test_pypi_mitosheet_check_dependencies():
    """
    This step checks that there are not installed extensions (or JupyterLab), and 
    then installs mitosheet from TestPyPi. 

    This is a useful command for testing the currently deployed staging version 
    of mitosheet.
    """

    jupyterlab_version, extension_names = get_jupyterlab_metadata()

    # If no JupyterLab is installed, we can continue with install, as
    # there are no conflict dependencies
    if jupyterlab_version is None and (extension_names is None or len(extension_names) == 0):
        return
    
    raise Exception('Installed JupyterLab: {jupyterlab_version}, Installed extensions {extension_names}'.format(jupyterlab_version=jupyterlab_version, extension_names=extension_names))


def install_step_test_pypi_mitosheet_install_mitosheet():
    install_pip_packages('mitosheet', test_pypi=True)


TEST_PYPI_MITOSHEET_INSTALLER_STEPS = [
    InstallerStep(
        'Checking to make sure JupyterLab and mitosheet are not installed',
        install_step_test_pypi_mitosheet_check_dependencies
    ),
    InstallerStep(
        'Installing mitosheet from TestPyPi',
        install_step_test_pypi_mitosheet_install_mitosheet
    ),
]
