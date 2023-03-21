import asyncio
from getpass import getpass
import nest_asyncio
# from office365.runtime.auth.authentication_context import AuthenticationContext
from office365.runtime.auth.user_credential import UserCredential
from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.files.file import File
import sys
import time
import traceback
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

    def __init__(self, *args, **kwargs):
        """
        Use: shpt = SharePoint(url_shpt='https://your.sharepoint.com/sites/yoursite',
                               username_shpt='yourSharePointUserName',
                               password_shpt='yourSharePointPassword',
                               folder_url_shpt= 'directoryWithPDFs')

        Parameters
        ----------
        url_shpt : str,
            Base SharePoint team/site URL.
            e.g. 'https://smartronixonline.sharepoint.com/teams/Tarces3'
        username_shpt : str
            Your SharePoint username.
            e.g. JSmith@smxtech.com.
        password_shpt : str
            Your SharePoint password.
        folder_url_shpt : str
            Folder containing files to read.
        gui : class optional
            gui class containing a progress bar scaled from 0-1
            and uses .set(<flaot>)
        Returns
        -------
        None

        """
        self._url_shpt = kwargs.get('url_shpt', None)
        self._username_shpt = kwargs.get('username_shpt', None)
        self.__password_shpt = kwargs.get('password_shpt', "None")
        self._folder_url_shpt = kwargs.get('folder_url_shpt', None)
        self.file_ext = kwargs.get('file_ext', None)
        progress_bar = kwargs.get('progress_bar', None)
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
            if not self.__password_shpt:
                if self._loop_ran:
                    print('If not promted to retype your password '
                          'please restart the kernel and try again')
                self.__password_shpt = getpass(
                    "Enter your SharePoint Password:\n")

            self._ctx = ClientContext(self._url_shpt).with_credentials(
                UserCredential(self._username_shpt, self.__password_shpt))
            web = self._ctx.web
            self._ctx.load(web)
            self._ctx.execute_query()
            return
        except Exception as error:
            if 'Cannot get binary security token' in repr(error):
                print('Wrong username/password. Try again.\n')
                self._username_shpt = None
                while not self._username_shpt:
                    self._username_shpt = input(
                        'Enter your SharePoint Username:\n')
                self.__password_shpt = ''
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

    async def _main(self, file_ext: str, recursive=False):
        """
        Parameters
        ----------
        file_ext : str
            file extension to search for
        recursive : bool, optional
            Search sub-folders recursively. The default is False.

        Returns
        -------
        None.

        """
        root_folder = self._ctx.web.get_folder_by_server_relative_path(
            self._folder_url_shpt)
        files = root_folder.get_files(recursive).execute_query()
        # files also contains web assetts. So we must filter files to PDFs only
        files = [x for x in files if x.name.endswith(file_ext)]
        print(f'\nFound {len(files)} {file_ext} files in '
              f'{self._url_shpt}/{self._folder_url_shpt }\n')
        tasks = [asyncio.to_thread(self._task_coro, file)
                 for file in files]
        self._progressBar.total = len(tasks)
        self._files_bytes = await asyncio.gather(*tasks)

    def get_files(self, file_ext='pdf', recursive=False, **kwargs):
        """
        Gets all SharePoint files ending with specific extension
        Parameters
        ----------
        file_ext : str
            file extension to search for
        recursive : bool, optional
            Search sub-folders recursively. The default is False.

        Returns
        -------
        list
            List of files in bytes

        """
        # %% statics
        if not self._use_gui_progressBar:
            self._progressBar = tqdm(
                desc=f'Files from {self._folder_url_shpt }',
                position=0, leave=True)

        # %% Do Work!
        if self.file_ext:
            file_ext = self.file_ext
        start = time.time()
        try:
            asyncio.run(self._main(file_ext=file_ext))
            if not self._use_gui_progressBar:
                self._progressBar  # sets progressBar to 100% in case its delayed
                self._progressBar.close()
            else:
                self._progressBar.set(1)
            print(f"\nFinished in {time.time() - start:.2f} seconds")
            return self._files_bytes
        except Exception:
            err = traceback.format_exc()
            if "invalid username or password" in err:
                return "ERROR: invalid username or password"

    def upload_file(self, url_shpt, folder_url_shpt, username_shpt=None,
                    password_shpt=None, files_bytes=None, filename=None,
                    filepaths=None):
        """
        Uploads a bytes like object to SharePoint

        Parameters
        ----------
        shpt_url : str,
            Base SharePoint team/site URL.
            e.g. 'https://smartronixonline.sharepoint.com/teams/Tarces3'
        shpt_dir : str
            Folder containing files to read.
        file_bytes : list of tuples, optional
           [(<file bytes>, <filename>)] Used to upload file bytes
        filename : str, optional
            Name to save file as.
        filepaths : list of tuples, optional
            [(<filepath>, <filename>)] Used to upload local files

        Returns
        -------
        None.

        """
        if not username_shpt:
            username_shpt = self._username_shpt
        if not password_shpt:
            password_shpt = self.__password_shpt

        # TODO Utilize new tuple format for files and filenames
        ctx = ClientContext(url_shpt).with_credentials(
            UserCredential(self._username_shpt, self.__password_shpt))
        # target_folder = ctx.web.get_folder_by_server_relative_path(
        #     r"Shared Documents/General/RIPTAR/Data")
        target_folder = ctx.web.get_folder_by_server_relative_path(
            folder_url_shpt)
        # resp = target_folder.upload_file(filename, file_bytes).execute_query()  # noqa

        files = []
        if filepaths:
            for filepath, filename in filepaths:
                with open(filepath, 'rb') as file:
                    file_bytes = file.read()
                    files.append((file_bytes, filename))
        elif files_bytes:
            files = files_bytes
        else:
            print("Did not pass filepaths or file_bytes...")
            return

        for file, filename in files:
            try:
                resp = target_folder.upload_file(
                    filename, file).execute_query()
            except Exception:
                print(f"ERROR uploading {filename} to "
                      f"{url_shpt}/{folder_url_shpt}")
                continue

        print("Files have been uploaded to url: "
              f"{url_shpt}/{folder_url_shpt}/{filename}")
        return

    def update_property(self, property_name, value,
                        shpt_obj=None, server_relative_url=None):
        """
        Sets property of SharePoint object

        Parameters
        ----------
        shpt_file : obj
            Response object from office365_REST_Python_Client
        server_relative_url : str
            relative url path to SharePoint resource
        property_name : str
            Name of property to update
        value : str
            Value to update property to

        Returns
        -------
        None.

        """
        try:
            if shpt_obj:
                rel_url = shpt_obj['ServerRelativeUrl']
            elif server_relative_url:
                rel_url = server_relative_url
            else:
                err = 'No Relative URL provided'
                print(err)
                return None
            print(f'Updating {rel_url} custom property "{property_name}"')
            file = self._ctx.web.get_file_by_server_relative_url(
                rel_url).execute_query()
            properties = file.listItemAllFields
            properties.set_property(
                property_name, value).update().execute_query()
            return True
        except Exception:
            err = traceback.format_exc()
            print(err)


"""
How to Use:
    from toolbox.sharepoint_files import SharePoint
    shpt = SharePoint(url_shpt='https://your.sharepoint.com/sites/yoursite',
                      username_shpt='yourSharePointUserName',
                      password_shpt='yourSharePointPassword',
                      folder_url_shpt= 'directoryWithPDFs')
    resp = shpt.get_files()

Working with Office365 REST:
    https://github.com/vgrem/Office365-REST-Python-Client
"""
