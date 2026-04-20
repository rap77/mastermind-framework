"""Tests for Rust strategy."""

from core.strategies.rust import RustStrategy


def test_rust_validate_with_cargo(tmp_path):
    """Test validation with cargo available."""
    # Create Cargo.toml
    (tmp_path / "Cargo.toml").write_text('[package]\nname = "test"\nversion = "0.1.0"')

    strategy = RustStrategy(tmp_path, {"package_manager": "cargo", "tests": ["tests/"]})
    is_valid, error = strategy.validate()

    # Either valid (cargo installed) or has error
    assert is_valid or error is not None


def test_rust_analyze_code(tmp_path):
    """Test code analysis for Rust files."""
    # Create test files
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "main.rs").write_text("// Main\nfn main() {}\n")
    (tmp_path / "src" / "lib.rs").write_text("// Lib\n")

    strategy = RustStrategy(tmp_path, {"package_manager": "cargo", "tests": []})
    result = strategy.analyze_code()

    assert result["files"] >= 2
    assert result["lines_of_code"] > 0


def test_rust_analyze_deps(tmp_path):
    """Test dependency analysis."""
    (tmp_path / "Cargo.toml").write_text('[package]\nname = "test"\n')

    strategy = RustStrategy(tmp_path, {"package_manager": "cargo", "tests": []})
    result = strategy.analyze_deps()

    # Should succeed or skip gracefully
    assert result["status"] in ["success", "skipped"]


def test_rust_get_coverage(tmp_path):
    """Test coverage returns None."""
    strategy = RustStrategy(tmp_path, {"package_manager": "cargo", "tests": []})
    coverage = strategy.get_coverage()

    # Coverage is not implemented for Rust
    assert coverage is None
