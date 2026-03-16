#!/usr/bin/env python3
"""
Secret detector for code review diffs.
Scans for common secret patterns (API keys, tokens, passwords) before sending to AI.
Based on patterns from GitGuardian, TruffleHog, and industry standards.
"""

import re
import sys
from pathlib import Path
from typing import List, Tuple, Dict

class SecretDetector:
    """Detect and report secrets in diffs"""
    
    # Industry-standard patterns (from GitGuardian, TruffleHog, GitHub Secret Scanning)
    PATTERNS: Dict[str, str] = {
        'aws_access_key': r'AKIA[0-9A-Z]{16}',
        'aws_secret_key': r'aws_secret_access_key\s*=\s*["\']?([A-Za-z0-9/+=]{40})["\']?',
        'github_token': r'ghp_[a-zA-Z0-9]{36}',
        'github_oauth': r'gho_[a-zA-Z0-9]{36}',
        'github_app_token': r'(ghu|ghs)_[a-zA-Z0-9]{36}',
        'github_refresh_token': r'ghr_[a-zA-Z0-9]{76}',
        'slack_token': r'xox[baprs]-[0-9a-zA-Z-]{10,72}',
        'slack_webhook': r'https://hooks\.slack\.com/services/T[a-zA-Z0-9_]+/B[a-zA-Z0-9_]+/[a-zA-Z0-9_]+',
        'generic_api_key': r'["\']?api[_-]?key["\']?\s*[:=]\s*["\']([a-zA-Z0-9_\-]{20,})["\']',
        'generic_secret': r'["\']?secret["\']?\s*[:=]\s*["\']([a-zA-Z0-9_\-]{20,})["\']',
        'jwt_token': r'eyJ[a-zA-Z0-9_-]*\.eyJ[a-zA-Z0-9_-]*\.[a-zA-Z0-9_-]*',
        'private_key_rsa': r'-----BEGIN (RSA|DSA|EC|OPENSSH) PRIVATE KEY-----',
        'private_key_pgp': r'-----BEGIN PGP PRIVATE KEY BLOCK-----',
        'google_api_key': r'AIza[0-9A-Za-z\-_]{35}',
        'google_oauth': r'ya29\.[0-9A-Za-z\-_]+',
        'stripe_key': r'sk_live_[0-9a-zA-Z]{24,}',
        'stripe_restricted': r'rk_live_[0-9a-zA-Z]{24,}',
        'twilio_api_key': r'SK[0-9a-fA-F]{32}',
        'mailgun_api_key': r'key-[0-9a-zA-Z]{32}',
        'sendgrid_api_key': r'SG\.[a-zA-Z0-9_-]{22}\.[a-zA-Z0-9_-]{43}',
        'heroku_api_key': r'[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}',
        'password_assignment': r'password\s*[:=]\s*["\']([^"\']{8,})["\']',
        'connection_string': r'(mongodb|mysql|postgresql|redis)://[^:]+:[^@]+@[^/]+',
        'npm_token': r'npm_[a-zA-Z0-9]{36}',
        'pypi_token': r'pypi-AgEIcHlwaS5vcmc[A-Za-z0-9\-_]{50,}',
    }
    
    # Patterns to ignore (common false positives)
    IGNORE_PATTERNS = [
        r'example',
        r'test',
        r'dummy',
        r'placeholder',
        r'your_api_key_here',
        r'YOUR_API_KEY',
        r'<API_KEY>',
        r'\$\{',  # Environment variable references
        r'process\.env',  # Environment variable access
    ]
    
    def __init__(self, diff_file: Path):
        self.diff_file = diff_file
        self.findings: List[Dict[str, any]] = []
    
    def scan(self) -> Tuple[bool, List[Dict[str, any]]]:
        """
        Scan diff for secrets.
        Returns: (has_secrets, findings_list)
        """
        try:
            content = self.diff_file.read_text(encoding='utf-8', errors='ignore')
        except Exception as e:
            print(f"Error reading diff file: {e}", file=sys.stderr)
            return False, []
        
        # Only scan added lines (starting with +)
        lines = content.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            # Skip if not an added line
            if not line.startswith('+'):
                continue
            
            # Remove the + prefix for pattern matching
            line_content = line[1:]
            
            # Check if line should be ignored
            if self._should_ignore(line_content):
                continue
            
            # Scan for each pattern
            for secret_type, pattern in self.PATTERNS.items():
                matches = re.finditer(pattern, line_content, re.IGNORECASE)
                for match in matches:
                    # Additional validation to reduce false positives
                    if self._is_likely_secret(match.group(0), secret_type):
                        self.findings.append({
                            'type': secret_type,
                            'line': line_num,
                            'match': match.group(0)[:50] + '...' if len(match.group(0)) > 50 else match.group(0),
                            'context': line_content.strip()[:100]
                        })
        
        return len(self.findings) > 0, self.findings
    
    def _should_ignore(self, line: str) -> bool:
        """Check if line matches ignore patterns"""
        line_lower = line.lower()
        for pattern in self.IGNORE_PATTERNS:
            if re.search(pattern, line_lower):
                return True
        return False
    
    def _is_likely_secret(self, match: str, secret_type: str) -> bool:
        """Additional validation to reduce false positives"""
        match_lower = match.lower()
        
        # Ignore common placeholder values
        if any(placeholder in match_lower for placeholder in ['example', 'test', 'dummy', 'xxx', '000']):
            return False
        
        # Ignore very short matches (likely not real secrets)
        if len(match) < 10:
            return False
        
        # For generic patterns, require more entropy
        if secret_type in ['generic_api_key', 'generic_secret']:
            # Check for reasonable entropy (not all same character)
            if len(set(match)) < 5:
                return False
        
        return True
    
    def report(self) -> None:
        """Print findings to stderr"""
        if not self.findings:
            return
        
        print("\n" + "="*70, file=sys.stderr)
        print("🔒 SECRET DETECTION ALERT", file=sys.stderr)
        print("="*70, file=sys.stderr)
        print(f"\nFound {len(self.findings)} potential secret(s) in the diff:\n", file=sys.stderr)
        
        for i, finding in enumerate(self.findings, 1):
            print(f"{i}. {finding['type'].replace('_', ' ').title()}", file=sys.stderr)
            print(f"   Line {finding['line']}: {finding['match']}", file=sys.stderr)
            print(f"   Context: {finding['context']}", file=sys.stderr)
            print("", file=sys.stderr)
        
        print("⚠️  RECOMMENDATION:", file=sys.stderr)
        print("   - Remove secrets from code", file=sys.stderr)
        print("   - Use environment variables instead", file=sys.stderr)
        print("   - Add secrets to .env (and .gitignore)", file=sys.stderr)
        print("   - If these are test/example values, add 'test' or 'example' to the string", file=sys.stderr)
        print("\n   To proceed anyway (not recommended): use --allow-secrets flag", file=sys.stderr)
        print("="*70 + "\n", file=sys.stderr)
    
    def save_report(self, output_dir: Path) -> None:
        """Save findings to a file"""
        if not self.findings:
            return
        
        report_file = output_dir / "security-warnings.txt"
        with open(report_file, 'w') as f:
            f.write("SECRET DETECTION REPORT\n")
            f.write("=" * 70 + "\n\n")
            f.write(f"Scan time: {Path(self.diff_file).stat().st_mtime}\n")
            f.write(f"Total findings: {len(self.findings)}\n\n")
            
            for i, finding in enumerate(self.findings, 1):
                f.write(f"{i}. {finding['type']}\n")
                f.write(f"   Line: {finding['line']}\n")
                f.write(f"   Match: {finding['match']}\n")
                f.write(f"   Context: {finding['context']}\n\n")
        
        print(f"Security report saved to: {report_file}", file=sys.stderr)


def main():
    if len(sys.argv) < 2:
        print("Usage: secret_detector.py <diff-file>", file=sys.stderr)
        sys.exit(1)
    
    diff_file = Path(sys.argv[1])
    
    if not diff_file.exists():
        print(f"Error: Diff file not found: {diff_file}", file=sys.stderr)
        sys.exit(1)
    
    detector = SecretDetector(diff_file)
    has_secrets, findings = detector.scan()
    
    if has_secrets:
        detector.report()
        detector.save_report(diff_file.parent)
        sys.exit(1)  # Non-zero exit code to block the review
    
    sys.exit(0)  # Clean exit


if __name__ == "__main__":
    main()
