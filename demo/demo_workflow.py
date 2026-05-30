# demo/demo_workflow.py
"""
SecAPI Developer Workflow Demonstration

This script guides you through the process of using SecAPI to secure a project.
It automatically sets up a mock project containing a hardcoded API key, scans it, 
and explains how to interact with the SecAPI vault.
"""

import os
import shutil

def setup_demo_environment():
    print("🎬 Setting up SecAPI Demo Environment...")
    
    # 1. Create a dummy project directory
    project_dir = "./demo_project"
    if os.path.exists(project_dir):
        shutil.rmtree(project_dir)
    os.makedirs(project_dir)

    # 2. Create a source file with hardcoded secrets
    source_file = os.path.join(project_dir, "main.py")
    with open(source_file, "w") as f:
        f.write('import os\n\n')
        f.write('# A typical application containing a hardcoded API key\n')
        f.write('stripe_key = "sk_test_' + '51NzABCDeFGHIJKLMNOPQRST" # Don\'t leak this!\n')
        f.write('print(f"Connecting to Stripe using key: {stripe_key[:10]}...")\n')

    # 3. Create a config file template
    config_file = "./secapi_config.yaml"
    if not os.path.exists(config_file):
        with open(config_file, "w") as f:
            f.write('security:\n  auto_rotate: true\n  rotate_interval_days: 30\n')

    print(f"✅ Setup complete! Created mock project in '{project_dir}'")
    print(f"📄 Mock file: '{source_file}' contains a hardcoded Stripe key.")
    print("\n------------------------------------------------------------")
    print("🚀 HOW TO RUN THE SECAPI WORKFLOW:")
    print("------------------------------------------------------------")
    print("1. Scan the mock project for leaked secrets:")
    print(f"   secapi check {project_dir}")
    print("\n2. Select option [1] (Replace with secure reference).")
    print("   - Enter a name for the key (e.g., 'stripe_prod_key').")
    print("   - Set a master password to encrypt your local vault.")
    print("\n3. Inspect the updated file:")
    print(f"   cat {source_file}")
    print("   (Observe that 'stripe_key = load_key(\"stripe_prod_key\")' is set and the import is added!)")
    print("\n4. View all keys stored in your local vault:")
    print("   secapi list")
    print("\n5. Retrieve or verify the value of your key:")
    print("   secapi load stripe_prod_key")
    print("------------------------------------------------------------\n")

if __name__ == "__main__":
    setup_demo_environment()
