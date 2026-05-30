import os
import shutil
from secapi.scanner import scan_directory
from secapi.fixer import update_file

def verify():
    print("🚀 Running SecAPI Manual Verification Script...")

    # 1. Setup sandbox environment
    test_dir = "./test_sandbox"
    if os.path.exists(test_dir):
        shutil.rmtree(test_dir)
    os.makedirs(test_dir)

    dirty_file = os.path.join(test_dir, "app.py")
    with open(dirty_file, "w") as f:
        f.write('db_password = "sk_test_' + '51NzABCDeFGHIJKLMNOPQRST" # stripe secret\n')
        f.write('print(db_password)\n')

    print(f"📄 Created dirty source file: {dirty_file}")

    # 2. Run scanner
    findings = scan_directory(test_dir)
    print(f"🔍 Scan findings: {findings}")
    assert len(findings) == 1, f"Expected 1 finding, got {len(findings)}"
    path, line_num, content, label = findings[0]
    assert label == "Stripe", f"Expected Stripe label, got {label}"

    # 3. Apply smart fixer
    print("🔧 Running smart fixer on the dirty file...")
    update_file(dirty_file, line_num, "my_stripe_secret")

    # 4. Check modified file
    with open(dirty_file, "r") as f:
        updated_content = f.read()
    print("\n📝 Updated File Content:")
    print("-" * 50)
    print(updated_content, end="")
    print("-" * 50)

    assert "from secapi.secure import load_key" in updated_content, "Missing load_key import statement"
    assert 'db_password = load_key("my_stripe_secret")' in updated_content, "Failed to preserve variable name LHS"

    # Clean up
    shutil.rmtree(test_dir)
    print("\n✅ End-to-end verification completed successfully!")

if __name__ == "__main__":
    verify()
