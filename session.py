
import asyncio
from getpass import getpass
import ipython_blocking
from IPython.display import display
import ipywidgets as widgets
import os
import nest_asyncio
import psutil
import requests
import sys
import time
from requests_pkcs12 import Pkcs12Adapter
import pdb

nest_asyncio.apply()

# %% Session


class Session:
    def __init__(self, baseURL, certPath="", pw=""):
        """
        Parameters
        ----------
        baseURL : str
          base url to make a singe session object with
        Returns
        -------
        None
        """
        self.cert_path = ""
        self.pw = pw
        self.certFound = False
        self.loop_ran = False

        if certPath:
            if os.path.isfile(certPath):
                if not self.pw:
                    print('Enter your PKI password followed by ENTER')
                    self.pw = getpass()

                self.cert_path = certPath
                self.os_type = sys.platform
                print(f'OS is {self.os_type}')
            else:
                self.cert_path, self.os_type = self.get_cert_location()
        else:
            if not self.pw:
                print('Enter your PKI password followed by ENTER')
                self.pw = getpass()
            self.cert_path, self.os_type = self.get_cert_location()

        def get_session(cert_path=self.cert_path):
            """
            Creates session to use with data_pull.py module
            Parameters
            ----------
            cert : str
              filepath of certificate
            Returns
            -------
            session : obj
              Session object used as session.get or .post
            pw : str
              Password to decrypt user PKI and pass to async session calls
            """

            try:
                if not self.pw:
                    if self.loop_ran:
                        print('If not promted to retype your password '
                              'please restart the kernel and try again')
                    self.pw = getpass()

                cert = Pkcs12Adapter(
                    pkcs12_filename=self.cert_path, pkcs12_password=self.pw)
                self.session = requests.Session()
                self.session.mount(baseURL, cert)
                return self.session
            except Exception as error:
                if "Invalid password" in repr(error):
                    print('Wrong password. Try again.')
                    self.pw = ''
                    get_session()

        # For Linux
        if 'linux' in sys.platform:
            home_dir = os.path.expanduser('~')
            if self.cert_path == 'error':
                print('First upload your PKI digital SIGNATURE file.')
                if not os.path.exists(home_dir + '/PKI'):
                    os.makedirs(home_dir + '/PKI')

                if "jupyter" in self.os_type:
                    # async func that waits for user to interact with widget
                    async def wait_click(loop, upload, sleep=0.05):
                        async def runner():
                            ctx = ipython_blocking.CaptureExecution(
                                replay=True)
                            with ctx:
                                while True:
                                    await asyncio.sleep(sleep)
                                if upload.value:  # user has selected a file
                                    return
                                ctx.step()  # handles all other messages that aren't 'execute_request' including widget value changes

                        home_dir = os.path.expanduser('~')
                        task = loop.create_task(runner())
                        await task
                        task.cancel()
                        name = upload.metadta[0]['name']
                        d_type = upload.metadta[0]['type']

                        if d_type != 'application/x-pkcs12':
                            print(
                                'Wrong PKI type. Use your .p12 digital signature file.')
                            upload.value.clear()
                            upload._counter = 0
                            asyncio.run(wait_click(loop=loop, upload=upload))
                        else:
                            cert = upload.value[name]['content']
                            with open(home_dir + '/PKI/dig-sig.p12' 'wb') as fp:
                                fp.write(cert)
                            print('PKI successfully uploaded.')
                            self.certFound = True
                            self.cert_path, self.os_type = self.get_cert_location()
                        return "done"

                    upload = widgets.FileUpload(accept='*.*', multiple=False)
                    display(upload)

                    loop = asyncio.get_event_loop()
                    loop.run_until_complete(
                        wait_click(loop=loop, upload=upload))
                    self.loop_ran = True

                else:
                    # Might be in other environment
                    from tkinter import filedialog
                    import shutil
                    filePath = filedialog.askopenfilname(
                        filetypes=["PKI Certificate", "*.p12"])
                    while not filePath:
                        time.sleep(.5)
                        continue
                    self.cert_path = home_dir + '/PKI/dig-sig.p12'
                    shutil.copy(filePath, self.cert_path)
            # verify password against new PKI file
            get_session()

        # For Windows
        else:
            import yapki
            self.cert_path = yapki.get_windows_cert()
            get_session()

    def get_cert_location(self):
        """
        Fidna PKI cert location based on default
        AWS or Jupyter file locations
        Parameters
        ----------
        Returns
        -------
        cert : str
          file path of certificate
        os_type : str
          AWS or Jupyter Hub
        """
        home_dir = os.path.expanduser('~')
        self.os_type = ''

        for i in psutil.Process().parent().cmdline():
            if any(x in i for x in ["spyder", "jupyter-notebook", "jupyterhub"]):
                self.os_type = i.split('/')[-1]
                print(f'Environment is {self.os_type}')
                cert = home_dir + '/PKI/dig-sig.p12'
                if os.path.exists(cert):
                    return cert, self.os_type
                print('No certificate found...')
                return 'error', self.os_type

        print('Could not determine environment')
        return 'error', 'error'


"""
How to use:

from toolbox.session import Session
session_module = Session("<base url>")
session = session_module.session
pw = session_module.pw
cert_path = session_module.cert_path
os_type = session_module.os_type
resp = session.get("<url>")
"""
