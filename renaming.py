parent = r'C:\Users\dbulygin\Dropbox\pythonProject\recordings'

import os

for path, dirs, files in os.walk(parent):
    for f in files:
        os.rename(os.path.join(path, f), os.path.join(path, f.replace(' ', '_')))