from typing import Dict, List, Any
import git


class GitService:
    def __init__(self, repo_path: str):
        """Initialize GitService with the path to the Git repository"""
        self.repo = git.Repo(repo_path)

    def get_branch_changes(
        self, branch_name: str, base_branch: str = "main"
    ) -> List[Dict[str, Any]]:
        """
        Get all changes in a branch compared to the base branch

        Args:
            branch_name: Name of the feature branch
            base_branch: Name of the base branch (default: main)

        Returns:
            List of changes with file content and metadata
        """
        try:
            # Get the diff between branches
            diff = self.repo.git.diff(f"{base_branch}...{branch_name}", "--unified=0")

            # Parse the diff to get file changes
            changes = []
            current_file = None
            current_changes = []

            for line in diff.split("\n"):
                if line.startswith("diff --git"):
                    # Save previous file changes if any
                    if current_file and current_changes:
                        changes.append(
                            {
                                "file_path": current_file,
                                "changes": "\n".join(current_changes),
                                "author": self._get_last_author(current_file),
                            }
                        )
                    # Start new file
                    current_file = line.split()[-1].lstrip("b/")
                    current_changes = []
                elif line.startswith("+++") or line.startswith("---"):
                    continue
                else:
                    current_changes.append(line)

            # Add the last file
            if current_file and current_changes:
                changes.append(
                    {
                        "file_path": current_file,
                        "changes": "\n".join(current_changes),
                        "author": self._get_last_author(current_file),
                    }
                )

            return changes

        except git.GitCommandError as e:
            raise ValueError(f"Error getting branch changes: {str(e)}")

    def _get_last_author(self, file_path: str) -> str:
        """Get the last author who modified the file"""
        try:
            blame = self.repo.git.blame("--porcelain", file_path)
            # Extract author from blame output
            author_line = next(
                line for line in blame.split("\n") if line.startswith("author ")
            )
            return author_line.replace("author ", "")
        except:
            return "Unknown"

    def get_commit_changes(self, commit_hash: str) -> List[Dict[str, Any]]:
        """
        Get changes from a specific commit

        Args:
            commit_hash: The commit hash to analyze

        Returns:
            List of changes with file content and metadata
        """
        try:
            commit = self.repo.commit(commit_hash)
            changes = []

            for file_diff in commit.diff(commit.parents[0]):
                changes.append(
                    {
                        "file_path": file_diff.b_path,
                        "changes": file_diff.diff.decode("utf-8"),
                        "author": commit.author.name,
                    }
                )

            return changes

        except git.GitCommandError as e:
            raise ValueError(f"Error getting commit changes: {str(e)}")

    def get_branch_commits(
        self, branch_name: str, base_branch: str = "main"
    ) -> List[str]:
        """Get all commit hashes in a branch that aren't in the base branch"""
        try:
            commits = self.repo.git.log(
                f"{base_branch}..{branch_name}", "--pretty=format:%H"
            ).split("\n")
            return commits if commits and commits[0] else []
        except git.GitCommandError as e:
            raise ValueError(f"Error getting branch commits: {str(e)}")
