import os
import sys

def patch_notifications_package():
    try:
        # Find the path to the notifications package
        import notifications
        package_path = os.path.dirname(notifications.__file__)
        base_models_path = os.path.join(package_path, 'base', 'models.py')
        
        print(f"Found notifications package at: {package_path}")
        print(f"Base models file: {base_models_path}")
        
        # Read the file content
        with open(base_models_path, 'r') as f:
            content = f.read()
        
        # Check if 'index_together' is in the file
        if 'index_together' in content:
            # Replace the line containing index_together
            modified_content = content.replace(
                "index_together = ('recipient', 'unread')", 
                "# index_together removed due to compatibility issues"
            )
            
            # Write the modified content back
            with open(base_models_path, 'w') as f:
                f.write(modified_content)
                
            print("Successfully patched notifications package by removing index_together")
            return True
        else:
            print("No 'index_together' found in the file. No changes made.")
            return False
    except Exception as e:
        print(f"Error patching notifications package: {e}")
        return False

if __name__ == "__main__":
    success = patch_notifications_package()
    sys.exit(0 if success else 1)