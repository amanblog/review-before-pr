#!/usr/bin/env python3
"""
Cross-platform diff generator with smart filtering and secret detection.
Equivalent to generate_diff.sh but works on Windows/Mac/Linux.

Usage:
    python generate_diff.py <base-branch> <feature-branch> [output-file]
    python generate_diff.py --staged [output-file]
    python generate_diff.py --local [output-file]

Options:
    --allow-secrets    Disable secret detection (use with caution)
    --no-filter        Disable noise filtering (include all files)
"""

import sys
import subprocess
import json
import argparse
from pathlib import Path
from typing import List, Dict, Optional, Tuple


class DiffGenerator:
    """Generate filtered git diffs with secret detection"""
    
    # Default exclusion patterns (industry standard)
    DEFAULT_EXCLUDES = [
        # Lock files
        '**/*lock.json', '**/*lock.yaml', '**/*.lock',
        '**/package-lock.json', '**/yarn.lock', '**/pnpm-lock.yaml',
        '**/Gemfile.lock', '**/poetry.lock', '**/Cargo.lock',
        '**/composer.lock', '**/Pipfile.lock', '**/go.sum',
        
        # Binary & media files
        '**/*.svg', '**/*.png', '**/*.jpg', '**/*.jpeg',
        '**/*.gif', '**/*.ico', '**/*.webp', '**/*.pdf',
        '**/*.woff', '**/*.woff2', '**/*.ttf', '**/*.eot',
        
        # Minified/compiled files
        '**/*.min.js', '**/*.min.css', '**/*.bundle.js',
        '**/*.chunk.js', '**/*.chunk.css',
        
        # Build outputs & dependencies
        'dist/**', 'build/**', 'out/**', '.next/**',
        'node_modules/**', 'vendor/**', 'target/**',
        '__pycache__/**', '*.pyc', '.venv/**',
        
        # Logs & temp files
        '*.log', '*.tmp', '*.cache', '.DS_Store',
    ]
    
    def __init__(self, allow_secrets: bool = False, no_filter: bool = False):
        self.allow_secrets = allow_secrets
        self.no_filter = no_filter
        self.repo_root = self._get_repo_root()
        self.review_dir = self.repo_root / ".review"
        self.config = self._load_config()
        self.excludes = [] if no_filter else self._build_excludes()
    
    def _get_repo_root(self) -> Path:
        """Get git repository root"""
        try:
            result = subprocess.run(
                ['git', 'rev-parse', '--show-toplevel'],
                capture_output=True,
                text=True,
                check=True
            )
            return Path(result.stdout.strip())
        except subprocess.CalledProcessError:
            print("Error: not inside a git repository.", file=sys.stderr)
            sys.exit(1)
    
    def _load_config(self) -> Dict:
        """Load .reviewrc or return defaults"""
        config_path = self.repo_root / ".reviewrc"
        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    config = json.load(f)
                print("Loading configuration from .reviewrc", file=sys.stderr)
                return config
            except json.JSONDecodeError as e:
                print(f"Warning: Invalid JSON in .reviewrc: {e}", file=sys.stderr)
                return {}
        return {}
    
    def _build_excludes(self) -> List[str]:
        """Build list of exclusion patterns"""
        excludes = self.DEFAULT_EXCLUDES.copy()
        
        # Add custom patterns from config
        if 'ignorePatterns' in self.config:
            custom_patterns = self.config['ignorePatterns']
            if isinstance(custom_patterns, list):
                excludes.extend(custom_patterns)
                print(f"Loaded {len(custom_patterns)} custom ignore patterns", file=sys.stderr)
        
        # Convert to git pathspec format. Use :(exclude) instead of :! to avoid
        # pathspec magic parsing issues (e.g. patterns like __pycache__/** can
        # cause :! to be misinterpreted and break exclusions including lock files).
        return [f':(exclude){pattern}' for pattern in excludes]
    
    def _setup_review_dir(self) -> None:
        """Create .review directory and update .gitignore"""
        self.review_dir.mkdir(exist_ok=True)
        
        gitignore = self.repo_root / ".gitignore"
        gitignore_entry = ".review/\n"
        
        if gitignore.exists():
            content = gitignore.read_text()
            if ".review/" not in content:
                with open(gitignore, 'a') as f:
                    f.write(gitignore_entry)
                print("Added .review/ to .gitignore", file=sys.stderr)
        else:
            gitignore.write_text(gitignore_entry)
            print("Created .gitignore with .review/", file=sys.stderr)
    
    def _run_git_diff(self, args: List[str], output_file: Path) -> bool:
        """Run git diff command and write to file"""
        cmd = ['git', '--no-pager', 'diff'] + args + self.excludes
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True,
                cwd=self.repo_root
            )
            
            if not result.stdout.strip():
                return False
            
            output_file.write_text(result.stdout, encoding='utf-8')
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"Error running git diff: {e}", file=sys.stderr)
            if e.stderr:
                print(e.stderr, file=sys.stderr)
            sys.exit(1)
    
    def _detect_secrets(self, diff_file: Path) -> bool:
        """Run secret detection on diff file. Returns True if secrets found."""
        if self.allow_secrets:
            return False
        
        secret_detector = self.repo_root / "scripts" / "filters" / "secret_detector.py"
        if not secret_detector.exists():
            # Secret detector not available, skip check
            return False
        
        try:
            result = subprocess.run(
                [sys.executable, str(secret_detector), str(diff_file)],
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                # Secrets detected
                print(result.stderr, file=sys.stderr)
                return True
            
            return False
            
        except Exception as e:
            print(f"Warning: Secret detection failed: {e}", file=sys.stderr)
            return False
    
    def _verify_branch(self, branch: str) -> bool:
        """Verify that a branch exists"""
        try:
            subprocess.run(
                ['git', 'rev-parse', '--verify', branch],
                capture_output=True,
                check=True,
                cwd=self.repo_root
            )
            return True
        except subprocess.CalledProcessError:
            return False
    
    def generate_staged(self, output_file: Optional[Path] = None) -> None:
        """Generate diff for staged changes"""
        output = output_file or (self.review_dir / "diff.txt")
        
        print(f"Writing staged diff to {output}", file=sys.stderr)
        
        if not self._run_git_diff(['--cached'], output):
            print("No staged changes.", file=sys.stderr)
            sys.exit(0)
        
        if self._detect_secrets(output):
            print("⚠️  Secrets detected! Review blocked. Use --allow-secrets to override (not recommended).", file=sys.stderr)
            sys.exit(1)
        
        line_count = len(output.read_text().splitlines())
        print(f"Done. {line_count} lines in {output}", file=sys.stderr)
    
    def generate_local(self, output_file: Optional[Path] = None) -> None:
        """Generate diff for all local changes (staged + unstaged)"""
        output = output_file or (self.review_dir / "diff.txt")
        
        print(f"Writing all local changes (vs HEAD) to {output}", file=sys.stderr)
        
        if not self._run_git_diff(['HEAD'], output):
            print("No local changes (working tree clean).", file=sys.stderr)
            sys.exit(0)
        
        if self._detect_secrets(output):
            print("⚠️  Secrets detected! Review blocked. Use --allow-secrets to override (not recommended).", file=sys.stderr)
            sys.exit(1)
        
        line_count = len(output.read_text().splitlines())
        print(f"Done. {line_count} lines in {output}", file=sys.stderr)
    
    def generate_branch(self, base: str, feature: str, output_file: Optional[Path] = None) -> None:
        """Generate diff between two branches"""
        output = output_file or (self.review_dir / "diff.txt")
        
        # Verify branches exist
        if not self._verify_branch(base):
            print(f"Error: base branch '{base}' not found.", file=sys.stderr)
            sys.exit(1)
        
        if not self._verify_branch(feature):
            print(f"Error: feature branch '{feature}' not found.", file=sys.stderr)
            sys.exit(1)
        
        print(f"Writing diff {base}..{feature} to {output}", file=sys.stderr)
        
        if not self._run_git_diff([f'{base}..{feature}'], output):
            print(f"No changes between {base} and {feature}.", file=sys.stderr)
            sys.exit(0)
        
        if self._detect_secrets(output):
            print("⚠️  Secrets detected! Review blocked. Use --allow-secrets to override (not recommended).", file=sys.stderr)
            sys.exit(1)
        
        line_count = len(output.read_text().splitlines())
        print(f"Done. {line_count} lines in {output}", file=sys.stderr)


def main():
    parser = argparse.ArgumentParser(
        description='Generate filtered git diffs for code review',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  %(prog)s main feature-branch              # Diff between branches
  %(prog)s --staged                         # Staged changes only
  %(prog)s --local                          # All local changes
  %(prog)s --staged --allow-secrets         # Skip secret detection
  %(prog)s main feature --no-filter         # Include all files
        '''
    )
    
    parser.add_argument('--staged', action='store_true',
                        help='Generate diff for staged changes only')
    parser.add_argument('--local', action='store_true',
                        help='Generate diff for all local changes (staged + unstaged)')
    parser.add_argument('--allow-secrets', action='store_true',
                        help='Disable secret detection (use with caution)')
    parser.add_argument('--no-filter', action='store_true',
                        help='Disable noise filtering (include all files)')
    parser.add_argument('base', nargs='?',
                        help='Base branch name')
    parser.add_argument('feature', nargs='?',
                        help='Feature branch name')
    parser.add_argument('output', nargs='?', type=Path,
                        help='Output file path (default: .review/diff.txt)')
    
    args = parser.parse_args()
    
    # Create generator
    generator = DiffGenerator(
        allow_secrets=args.allow_secrets,
        no_filter=args.no_filter
    )
    generator._setup_review_dir()
    
    # Determine mode
    if args.staged:
        generator.generate_staged(args.output)
    elif args.local:
        generator.generate_local(args.output)
    elif args.base and args.feature:
        generator.generate_branch(args.base, args.feature, args.output)
    else:
        parser.print_help()
        print("\nError: Must specify either --staged, --local, or <base> <feature>", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
