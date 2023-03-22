# Toolbox
Toolbox is a collection of useful modular coding packages aimed at making everyday operations easier.

## data_pull.py
Makes 1 to N synchronous or asynconous requests a piece of 🍰
```python
from toolbox import data_pull
from toolbox.session import Session, get_cert_location
````
## flatten
Flattens 1 to N deeply nested data sets into a flat array of strings.  You can also pass a list of keys to either exclude or include from the output.
```python
data = [{
  'apple':{'type': 'THIS', 'serial': '12345'},
  'banana': [1,2,3,4,5],
  'cookie': [{'another_type': 'THAT', 'another_serial': '67890'}],
  'eclaire': 'And Uh'
  }]

data_flat = []
for r in data:
  data_flat.append(flatten(r, exclude=['apple', 'cookie']))

# >>> [{'apple':"{'type': 'THIS', 'serial': '12345'}",
#      'banana_0': '1',
#      'banana_1': '2',
#      'banana_2': '3',
#      'banana_3': '4',
#      'banana_4': '5',
#      'cookie': "[{'another_type': 'THAT', 'another_serial': '67890'}]",
#      'eclaire': 'And Uh'}]

data_flat = []
for r in data:
  data_flat.append(flatten(r, include=['apple', 'cookie']))

# >>> [{'apple_type': 'THIS',
#      'apple_serial': '12345',
#      'cookie_0_another_type': 'THAT',
#      'cookie_0_another_serial': '67890'}]

data_flat = flatten(data[0]['apple'], name='apple')

# >>> {'apple_type': 'THIS', 'apple_serial': '12345'}
```
## jupyter_themes
Easily add style themes to boring Jupyter Notebooks 🔥
```python
# In Notebook Cell
from Ipython.display import display
from toolbox import jupyter_themes as jt
dispaly(jt.display_box)

# In nested Widget Container
from ipywidgets import widgets
from Ipython.display import display
from toolbox import jupyter_themes as jt

tab_nest = widgets.Tab()
tab_nest.children = [jt.display_box]  # Jupyter Themes widget container
jt.parent = tab_nest  # Needed so None and The Upside Down properly redraw page
tab_nest.set_title(0, "🖥 Display")
display(tab_nest)
```
## log_to_text_file
A more customizable logging package
```python
from toolbox.log_to_text_file import get_logger as logger
logging_path = <full log file path as string›  # './.logs/snuffy.log'
log = logger(__name__, logging_path)  # __name_ is python built-in for module name
log.debug('This is an DEBUG entry')
log.info('This is an INFO entry')
log.warning('This is an WARNING entry')
log.critical ('This is an CRITICAL entry')
```
## message_box
Easily display a pop up message in a Windows environment
```python
from toolbox import message_box as msgbox
from toolbox.message_box import show_msg

show_msg("Message with some extremely important info.",
         "Title", icon=msgbox.icon.EXCLAMATION,
         ontop=True)
```
## pkcs12_handler
Decrypt pkcs12 certificates for use in sessions.
```python
with pfx_to_pem('foo.p12', 'foo_password') as cert:
    resp = requests.post(url, cert=cert, data=payload)
```
## session
Creates a session using pkcs12 certificate.
```python
from toolbox.session import Session
# Copies certifcate to os.path.expanduser('~')+'/PKI'
session_module = Session("<base url>")
session = session_module.session
pw = session_module.pw
cert_path = session_module.cert_path
os_type = session_module.os_type
resp = session.get("<url>")
```
## sharepoint_files
Asynchronously fetches all PDF files from sharepoint directory.
Leverages [Office365 Rest](https://github.com/vgrem/Office365-REST-Python-Client)
```python
from toolbox.sharepoint_files import SharePoint

shpt = SharePoint(url_shrpt='https://your.sharepoint.com/sites/yoursite',
                  username_shrpt='yourSharePointUserName',
                  password_shrpt='yourSharePointPassword',
                  folder_url_shrpt= 'directoryWithPDFs')
resp = shpt.get_files()
```
## verify_modules
Auto installs missing package dependencies.
* Script will install package versions that don't match `required_modules`.
* :warning: **Errors due to typos or unavailable modules is not handled**
```python
from toolbox.verify_modules import verify_modules
required_modules = {
    'seaborn': '0.11.2',
    'matplotlib': '3.5.2',
    'bs4': '0.0.1'
}
verify_modules(required_modules)
```
# License
[MIT](LICENSE)
