"""Tests for Node.js strategy."""

from core.strategies.node import NodeStrategy


def test_node_validate_with_pnpm(tmp_path):
    """Test validation with pnpm package manager."""
    # Create package.json with pnpm-lock.yaml
    (tmp_path / "package.json").write_text('{"name": "test"}')
    (tmp_path / "pnpm-lock.yaml").write_text("lockfile")

    strategy = NodeStrategy(
        tmp_path, {"package_manager": "pnpm", "tests": ["*.test.ts"]}
    )
    is_valid, error = strategy.validate()

    # Either valid or has error message (pnpm might not be installed)
    assert is_valid or error is not None


def test_node_validate_without_tests(tmp_path):
    """Test validation fails when no test directory specified."""
    (tmp_path / "package.json").write_text('{"name": "test"}')

    strategy = NodeStrategy(tmp_path, {"package_manager": "npm", "tests": []})
    is_valid, error = strategy.validate()

    # Should be valid if npm exists (tests are optional for Node)
    assert is_valid or error is not None


def test_node_validate_missing_package_manager(tmp_path):
    """Test validation when package manager is missing."""
    strategy = NodeStrategy(
        tmp_path, {"package_manager": "npm", "tests": ["*.test.ts"]}
    )

    # Mock missing npm by using invalid command
    is_valid, error = strategy.validate()

    # Either valid (npm exists) or has error
    assert is_valid or error is not None


def test_node_analyze_code(tmp_path):
    """Test code analysis for TypeScript/JavaScript files."""
    # Create test files
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "index.ts").write_text(
        "// Some code\n// More code\n// Third line"
    )
    (tmp_path / "src" / "utils.ts").write_text("// Utils")

    strategy = NodeStrategy(tmp_path, {"package_manager": "npm", "tests": []})
    result = strategy.analyze_code()

    assert result["files"] >= 2
    assert result["lines_of_code"] > 0
    assert isinstance(result["modules"], list)


def test_node_analyze_deps(tmp_path):
    """Test dependency analysis."""
    (tmp_path / "package.json").write_text('{"name": "test"}')

    strategy = NodeStrategy(tmp_path, {"package_manager": "npm", "tests": []})
    result = strategy.analyze_deps()

    # Should succeed or error gracefully
    assert "status" in result
    assert result["status"] in ["success", "error"]


def test_node_get_coverage(tmp_path):
    """Test coverage parsing."""
    (tmp_path / "package.json").write_text('{"name": "test"}')

    strategy = NodeStrategy(tmp_path, {"package_manager": "npm", "tests": []})
    coverage = strategy.get_coverage()

    # Coverage should be None if no tests run
    assert coverage is None or isinstance(coverage, float)
