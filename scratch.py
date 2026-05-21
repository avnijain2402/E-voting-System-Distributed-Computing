import os
import shutil

# To make things easier, we'll create the templates and static directory via code implicitly if we use write_file appropriately or we can create directories here but using write_to_file with absolute paths creates directories automatically.

# Wait, the instruction says write_to_file will create the parent directories automatically. 
# So no python script needed for creating dirs, I can just create templates/login.html
