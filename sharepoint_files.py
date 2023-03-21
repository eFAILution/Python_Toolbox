# -*- coding: utf-8 -*-

import asyncio
from getpass import getpass
import nest_asyncio
# from office365.runtime.auth.authentication_context import AuthenticationContext
from office365.runtime.auth.user_credential import UserCredential
from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.files.file import File
import sys
import time
import pdb

nest_asyncio.apply()

# %% varying imports
if getattr(sys, 'frozen', False):
    # If the application is run as a bundle, the PyInstaller bootloader
    # extends the sys module by a flag frozen=True and sets the app
    # path into variable _pyinstaller --onedir option
    # application_path = sys._MEIPASS
    # path into variable for pyinstaller --onefile option
    from tqdm.tk import tqdm
    # Close the splash screen.
    import pyi_splash
    pyi_splash.close()
# elif __name__ == 'toolbox.sharepoint_files':
#     from tqdm.tk import tqdm
else:
    from tqdm import tqdm


# %% inputs


class SharePoint:

    def __init__(self, url_shrpt, username_shrpt, password_shrpt,
                 folder_url_shrpt, progress_bar=None):
        """
        Use: shpt = SharePoint(url_shrpt='https://your.sharepoint.com/sites/yoursite',
                               username_shrpt='yourSharePointUserName',
                               password_shrpt='yourSharePointPassword',
                               folder_url_shrpt= 'directoryWithPDFs')

        Parameters
        ----------
        url_shrpt : str,
            Base SharePoint team/site URL.
            e.g. 'https://MyCompany.sharepoint.com/teams/AlphaTeam'
        username_shrpt : str
            Your SharePoint username.
            e.g. JSmith@MyCompany.com.
        password_shrpt : str
            Your SharePoint password.
        folder_url_shrpt : str
            Folder containing files to read.
        gui : class optional
            gui class containing a progress bar scaled from 0-1
            and uses .set(<float>)
        Returns
        -------
        None

        """
        self._url_shrpt = url_shrpt
        self._username_shrpt = username_shrpt
        self.__password_shrpt = password_shrpt
        self._folder_url_shrpt = folder_url_shrpt
        self._files_bytes = []
        self._files_count = 0
        self._loop_ran = False
        self.get_authentication()
        if progress_bar:
            self._use_gui_progressBar = True
            self._progressBar = progress_bar
        else:
            self._use_gui_progressBar = None

        # %% Authentication
    def get_authentication(self):
        try:
            if not self.__password_shrpt:
                if self._loop_ran:
                    print('If not promted to retype your password '
                          'please restart the kernel and try again')
                self.__password_shrpt = getpass(
                    "Enter your SharePoint Password:\n")

            self._ctx = ClientContext(self._url_shrpt).with_credentials(
                UserCredential(self._username_shrpt, self.__password_shrpt))
            web = self._ctx.web
            self._ctx.load(web)
            self._ctx.execute_query()
            return
        except Exception as error:
            if 'Cannot get binary security token' in repr(error):
                print('Wrong username/password. Try again.\n')
                self._username_shrpt = None
                while not self._username_shrpt:
                    self._username_shrpt = input(
                        'Enter your SharePoint Username:\n')
                self.__password_shrpt = ''
                self.get_authentication()

    # %% Extract Filenames

    def _enum_folder(self, parent_folder, fn):
        """
        :type parent_folder: Folder
        :type fn: (File)-> None
        """
        parent_folder.expand(["Files", "Folders"]).get().execute_query()
        for file in parent_folder.files:  # type: File
            fn(file)

        for folder in parent_folder.folders:  # # type: Folder
            self.enum_folder(folder, fn)

    def _task_coro(self, file):
        if not self._use_gui_progressBar:
            self._progressBar.update(1)
        else:
            self._progressBar.set(self._files_count/self._progressBar.total)
        self._files_count += 1
        data = file.to_json()
        file_bytes = file.read()
        data.update({'data': file_bytes})
        properties = file.listItemAllFields.get().execute_query().to_json()
        data.update({'listItemAllFields': properties})
        return data

    async def _main(self):
        root_folder = self._ctx.web.get_folder_by_server_relative_path(
            self._folder_url_shrpt)
        files = root_folder.get_files(True).execute_query()
        # files also contains web assetts. So we must filter files to PDFs only
        files = [x for x in files if x.name.endswith('.pdf')]
        print(f'\nFound {len(files)} files in '
              f'{self._url_shrpt}/{self._folder_url_shrpt }\n')
        tasks = [asyncio.to_thread(self._task_coro, file)
                 for file in files]
        self._progressBar.total = len(tasks)
        self._files_bytes = await asyncio.gather(*tasks)

    def get_files(self):
        """
        Gets all SharePoint files ending with '.pdf'

        Returns
        -------
        list
            List of files in bytes

        """
        # %% statics
        if not self._use_gui_progressBar:
            self._progressBar = tqdm(
                desc=f'Files from {self._folder_url_shrpt }',
                position=0, leave=True)

        # %% Do Work!
        start = time.time()
        asyncio.run(self._main())
        if not self._use_gui_progressBar:
            self._progressBar  # sets progressBar to 100% in case its delayed
            self._progressBar.close()
        else:
            self._progressBar.set(1)
        print(f"\nFinished in {time.time() - start:.2f} seconds")
        return self._files_bytes


"""
How to Use:
    from toolbox.sharepoint_files import SharePoint
    shpt = SharePoint(url_shrpt='https://your.sharepoint.com/sites/yoursite',
                      username_shrpt='yourSharePointUserName',
                      password_shrpt='yourSharePointPassword',
                      folder_url_shrpt= 'directoryWithPDFs')
    resp = shpt.get_files()

Working with Office365 REST:
    https://github.com/vgrem/Office365-REST-Python-Client
"""
