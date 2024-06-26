# Configuration file for jupyter-notebook.
# This file was generated by calling `jupyter notebook --generate-config` and then copying that file to this location from ~/.jupyter

from tempfile import mkdtemp


c = get_config()  #noqa

c.NotebookApp.password = ''
c.NotebookApp.password_required = False

c.NotebookApp.port = 8888

c.NotebookApp.port_retries = 0
c.NotebookApp.open_browser = False

c.NotebookApp.root_dir = mkdtemp(prefix='galata-test-')
c.NotebookApp.token = ""
c.NotebookApp.disable_check_xsrf = True
c.LabApp.expose_app_in_browser = True