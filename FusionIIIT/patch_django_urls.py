import os
import sys
import re

def patch_django_urls():
    try:
        # Find the main urls.py file
        urls_path = os.path.join('Fusion', 'urls.py')
        full_path = os.path.join(os.getcwd(), urls_path)
        
        print(f"Patching Django URLs in: {full_path}")
        
        # Read the file content
        with open(full_path, 'r') as f:
            content = f.read()
        
        # Replace the import statement
        modified_content = content.replace(
            "from django.conf.urls import include, url",
            "from django.urls import include, re_path as url"
        )
        
        # Write the modified content back
        with open(full_path, 'w') as f:
            f.write(modified_content)
            
        print("Successfully patched Django URLs by replacing url import with re_path")
        
        # Now find and patch all app urls.py files
        apps_dir = os.path.join(os.getcwd(), 'applications')
        patched_files = 0
        
        for root, dirs, files in os.walk(apps_dir):
            for file in files:
                if file == 'urls.py':
                    file_path = os.path.join(root, file)
                    print(f"Checking {file_path}")
                    
                    with open(file_path, 'r') as f:
                        file_content = f.read()
                    
                    if 'from django.conf.urls import' in file_content:
                        # Replace the import
                        new_content = re.sub(
                            r'from django\.conf\.urls import (.*?)url(.*?)\n',
                            r'from django.urls import \1re_path as url\2\n',
                            file_content
                        )
                        
                        # If no change was made but url is still imported
                        if new_content == file_content and 'from django.conf.urls import' in file_content:
                            new_content = file_content.replace(
                                "from django.conf.urls import",
                                "from django.urls import"
                            )
                            new_content = new_content.replace(
                                "import url",
                                "import re_path as url"
                            )
                        
                        with open(file_path, 'w') as f:
                            f.write(new_content)
                        
                        patched_files += 1
                        print(f"Patched {file_path}")
        
        print(f"Total patched files: {patched_files + 1}")
        return True
    except Exception as e:
        print(f"Error patching Django URLs: {e}")
        return False

if __name__ == "__main__":
    success = patch_django_urls()
    sys.exit(0 if success else 1)