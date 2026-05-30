import os
import pytest
from secapi.scanner import scan_directory, should_ignore, load_ignore_patterns
from secapi.fixer import update_file

def test_should_ignore(tmp_path):
    root = tmp_path

    # Create directory structure
    node_modules = root / "node_modules"
    node_modules.mkdir()
    (node_modules / "package.js").write_text("const secret = '123';")

    src = root / "src"
    src.mkdir()
    (src / "app.py").write_text("print('hello')")

    # Verify default ignore of node_modules
    assert should_ignore(str(node_modules / "package.js"), str(root), [])
    assert not should_ignore(str(src / "app.py"), str(root), [])

    # Verify custom ignore file loading
    ignore_file = root / ".secapiignore"
    ignore_file.write_text("# ignore file\n*.log\nignored_dir/*\n")

    patterns = load_ignore_patterns(str(root))
    assert "*.log" in patterns
    assert "ignored_dir/*" in patterns

    # Verify matching ignores
    log_file = src / "app.log"
    log_file.write_text("logs")
    assert should_ignore(str(log_file), str(root), patterns)

def test_scan_directory_regex(tmp_path):
    root = tmp_path

    # Clean file
    (root / "clean.py").write_text("a = 10\nprint(a)")

    # Dirty file with actual stripe secret and a load_key secure reference
    (root / "dirty.py").write_text(
        "my_stripe_key = \"sk_test_" + "51NzABCDeFGHIJKLMNOPQRST\"\n"
        "secure_stripe = load_key(\"my_stripe_key\")\n"
    )

    findings = scan_directory(str(root))

    # Should find 1 secret (stripe key on line 1) and skip line 2 (load_key)
    assert len(findings) == 1
    file_path, line_num, content, label = findings[0]
    assert "dirty.py" in file_path
    assert line_num == 1
    assert "sk_test_" in content
    assert label == "Stripe"

def test_smart_fixer(tmp_path):
    test_file = tmp_path / "app.py"
    test_file.write_text(
        "my_stripe_token = \"sk_test_" + "51NzABCDeFGHIJKLMNOPQ\"\n"
        "print(my_stripe_token)\n"
    )

    # Apply smart fix on line 1
    update_file(str(test_file), 1, "stripe_token")

    content = test_file.read_text()

    # 1. Verify import statement was prepended
    assert "from secapi.secure import load_key" in content

    # 2. Verify variable name was preserved (LHS unchanged) and string replaced (RHS updated)
    assert 'my_stripe_token = load_key("stripe_token")' in content
    assert 'print(my_stripe_token)' in content

def test_pre_commit_hook_install(tmp_path, monkeypatch):
    import os
    from secapi.hooks import install_pre_commit_hook

    # Move working directory to temporary directory
    monkeypatch.chdir(tmp_path)

    # 1. Should fail when not in a Git repository
    assert not install_pre_commit_hook()

    # 2. Should succeed when a .git folder is present
    os.makedirs(os.path.join(tmp_path, ".git"))
    assert install_pre_commit_hook()

    hook_file = os.path.join(tmp_path, ".git", "hooks", "pre-commit")
    assert os.path.exists(hook_file)

    with open(hook_file, 'r') as f:
        content = f.read()
    assert "SecAPI Pre-commit Hook" in content


def test_scan_single_file(tmp_path):
    dirty_file = tmp_path / "app.py"
    dirty_file.write_text("my_key = \"sk_test_" + "51NzABCDeFGHIJKLMNOPQRST\"\n")

    # Scan the file path directly
    findings = scan_directory(str(dirty_file))
    assert len(findings) == 1
    assert "app.py" in findings[0][0]
    assert findings[0][1] == 1
    assert findings[0][3] == "Stripe"


