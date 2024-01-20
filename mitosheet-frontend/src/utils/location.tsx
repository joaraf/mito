
/**
 * NOTE: the next two functions are key to the proper functioning of Mito in
 * these two environments. As such, anytime we are in JupyterLab, the 
 * isInJupyterLab MUST return true. We check a variety of these conditions
 * to see if this works (including in cases when mito is remote). 
 * 
 * If you change this code, make sure to test it with remove servers that 
 * have non-standard URL schemes.
 */

export const isInJupyterLab = (): boolean => {
    return window.location.pathname.startsWith('/lab') ||
        window.commands !== undefined ||
        (window as any)._JUPYTERLAB !== undefined
}
export const isInJupyterNotebook = (): boolean => {
    return window.location.pathname.startsWith('/notebooks') ||
        (window as any).Jupyter !== undefined
}

export const isInStreamlit = (): boolean => {
    
    // We are in streamlit if we are in an iframe that has a parent with
    // a class of "stApp"

    if (window.parent) {
        const parent = window.parent.document.querySelector('.stApp')
        if (parent) {
            return true
        }
    }
    return false
}

export const isInDash = (): boolean => {
    // Check if there is a div with the id _dash-app-content
    const dashAppContent = document.getElementById('_dash-app-content')
    if (dashAppContent) {
        return true
    }

    // Check for _dash-global-error-container
    const dashGlobalErrorContainer = document.getElementById('_dash-global-error-container')
    if (dashGlobalErrorContainer) {
        return true
    }

    return false;
}

export const isInDashboard = (): boolean => {
    return isInStreamlit() || isInDash()
}