import zipfile
import os
import shutil

src = r'C:/Users/girish/Downloads/flutter_windows_3.41.4-stable.zip'
dst = r'C:/Users/girish/flutter/3.41.4'
shutil.rmtree(dst, ignore_errors=True)
os.makedirs(dst, exist_ok=True)
print('extracting')
with zipfile.ZipFile(src, 'r') as z:
    z.extractall(dst)
print('done', len(os.listdir(dst)))
