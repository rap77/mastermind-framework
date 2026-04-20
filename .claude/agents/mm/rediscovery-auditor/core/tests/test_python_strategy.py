from core.strategies.python import PythonStrategy


def test_python_validate_with_uv(tmp_path):
    """Test validation with uv available."""
    # Create test structure
    (tmp_path / "tests").mkdir()
    (tmp_path / "pyproject.toml").write_text("[project]\nname='test'\n")

    strategy = PythonStrategy(tmp_path, {"tests": ["tests/"], "package_manager": "uv"})
    is_valid, error = strategy.validate()

    assert is_valid or error is not None  # Either valid or has error message


def test_python_validate_without_test_dir(tmp_path):
    """Test validation fails when no test directory."""
    (tmp_path / "pyproject.toml").write_text("[project]\nname='test'\n")

    strategy = PythonStrategy(tmp_path, {"tests": [], "package_manager": "uv"})
    is_valid, error = strategy.validate()

    assert not is_valid
    assert "test" in error.lower()


def test_python_run_tests_command(tmp_path):
    """Test that run_tests returns correct command structure."""
    (tmp_path / "tests").mkdir()
    (tmp_path / "pyproject.toml").write_text("[project]\nname='test'\n")

    # Test with uv
    strategy_uv = PythonStrategy(
        tmp_path, {"tests": ["tests/"], "package_manager": "uv"}
    )
    result_uv = strategy_uv.run_tests()

    assert "status" in result_uv
    assert "passing" in result_uv
    assert "failing" in result_uv

    # Test with pip
    strategy_pip = PythonStrategy(
        tmp_path, {"tests": ["tests/"], "package_manager": "pip"}
    )
    result_pip = strategy_pip.run_tests()

    assert "status" in result_pip


def test_python_analyze_deps(tmp_path):
    """Test dependency analysis."""
    (tmp_path / "tests").mkdir()
    (tmp_path / "pyproject.toml").write_text("[project]\nname='test'\n")

    strategy = PythonStrategy(tmp_path, {"tests": ["tests/"], "package_manager": "uv"})
    result = strategy.analyze_deps()

    assert "status" in result
    assert "outdated" in result


def test_python_analyze_code(tmp_path):
    """Test code analysis."""
    (tmp_path / "tests").mkdir()
    (tmp_path / "pyproject.toml").write_text("[project]\nname='test'\n")

    strategy = PythonStrategy(tmp_path, {"tests": ["tests/"], "package_manager": "uv"})
    result = strategy.analyze_code()

    assert "files" in result
    assert "lines_of_code" in result
    assert isinstance(result["files"], int)


def test_python_get_coverage(tmp_path):
    """Test coverage retrieval."""
    (tmp_path / "tests").mkdir()
    (tmp_path / "pyproject.toml").write_text("[project]\nname='test'\n")

    strategy = PythonStrategy(tmp_path, {"tests": ["tests/"], "package_manager": "uv"})
    coverage = strategy.get_coverage()

    # Coverage can be None if not available
    assert coverage is None or isinstance(coverage, float)
