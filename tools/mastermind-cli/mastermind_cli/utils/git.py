"""Git operations for MasterMind CLI."""

import os
from typing import Optional
from git import Repo, InvalidGitRepositoryError
from pathlib import Path


def get_repo(path: str = ".") -> Repo:
    """
    Get Git repository at path or its parents.

    Args:
        path: Starting path to search for repo

    Returns:
        Git Repo object

    Raises:
        ValueError: If not in a git repository
    """
    try:
        return Repo(path, search_parent_directories=True)
    except InvalidGitRepositoryError:
        raise ValueError(f"Not a git repository: {path}")


def git_commit(
    filepath: str, message: str, repo: Optional[Repo] = None
) -> str:
    """
    Create git commit for file change.

    Args:
        filepath: Path to file to commit (relative to repo root)
        message: Commit message
        repo: Git repo object (auto-detected if None)

    Returns:
        Commit SHA

    Raises:
        ValueError: If not in a git repository
    """
    if repo is None:
        repo = get_repo()

    # Get absolute path relative to repo root
    repo_root = repo.working_dir
    abs_path = os.path.abspath(filepath)
    rel_path = os.path.relpath(abs_path, repo_root)

    # Stage and commit
    repo.index.add([rel_path])
    commit = repo.index.commit(message)

    return commit.hexsha


def is_repo_dirty(repo: Optional[Repo] = None) -> bool:
    """Check if repo has uncommitted changes."""
    if repo is None:
        repo = get_repo()
    return repo.is_dirty()


def get_active_branch(repo: Optional[Repo] = None) -> str:
    """Get current branch name."""
    if repo is None:
        repo = get_repo()
    return repo.active_branch.name
