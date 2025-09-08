import os
import sys

def patch_markdown_deux_package():
    try:
        # Find the path to the markdown_deux package
        import markdown_deux
        package_path = os.path.dirname(markdown_deux.__file__)
        tags_path = os.path.join(package_path, 'templatetags', 'markdown_deux_tags.py')
        
        print(f"Found markdown_deux package at: {package_path}")
        print(f"Tags file: {tags_path}")
        
        # Read the file content
        with open(tags_path, 'r') as f:
            content = f.read()
        
        # Check if 'force_unicode' is in the file
        if 'force_unicode' in content:
            # Replace the import statement
            modified_content = content.replace(
                "from django.utils.encoding import force_unicode as force_text", 
                "from django.utils.encoding import force_str as force_text"
            )
            
            # Write the modified content back
            with open(tags_path, 'w') as f:
                f.write(modified_content)
                
            print("Successfully patched markdown_deux package by replacing force_unicode with force_str")
            return True
        else:
            print("No 'force_unicode' found in the file. No changes made.")
            return False
    except Exception as e:
        print(f"Error patching markdown_deux package: {e}")
        return False

if __name__ == "__main__":
    success = patch_markdown_deux_package()
    sys.exit(0 if success else 1)