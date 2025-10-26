# Security Policy

## Supported Versions

We release patches for security vulnerabilities for the following versions:

| Version | Supported          |
| ------- | ------------------ |
| 0.4.x   | ✅ |
| 0.3.x   | ✅ |
| 0.2.x   | ❌                |
| 0.1.x   | ❌                |
| < 0.1   | ❌                |

## Reporting a Vulnerability

We take the security of Polyglot FFI seriously. If you believe you have found a security vulnerability, please report it to us as described below.

### Where to Report

**Please do NOT report security vulnerabilities through public GitHub issues.**

Instead, please report them via:

1. **GitHub Security Advisories (Preferred):**
   - Go to https://github.com/chizy7/polyglot-ffi/security/advisories
   - Click "Report a vulnerability"
   - Fill out the form with details

2. **Email:**
   - Send email to the maintainer at: [chizy@chizyhub.com](mailto:chizy@chizyhub.com)
   - Include "SECURITY" in the subject line

### What to Include

Please include the following information in your report:

- **Description:** A clear description of the vulnerability
- **Impact:** What an attacker could achieve by exploiting this
- **Steps to Reproduce:** Detailed steps to reproduce the vulnerability
- **Affected Versions:** Which versions are affected
- **Proof of Concept:** Code or commands demonstrating the issue (if applicable)
- **Suggested Fix:** If you have ideas on how to fix it (optional)

### What to Expect

- **Acknowledgment:** We'll acknowledge receipt within 48 hours
- **Initial Assessment:** We'll provide an initial assessment within 1 week
- **Updates:** We'll keep you informed of progress
- **Resolution:** We aim to release a fix within 30 days for critical issues
- **Credit:** We'll credit you in the security advisory (unless you prefer to remain anonymous)

### Security Update Process

When we receive a security report:

1. **Confirm** the vulnerability and determine affected versions
2. **Develop** a fix and create a security patch
3. **Test** the fix thoroughly
4. **Release** a new version with the security patch
5. **Publish** a security advisory on GitHub
6. **Notify** users through release notes and changelog

## Security Best Practices

When using Polyglot FFI:

### For Users

1. **Keep Updated:** Always use the latest stable version
   ```bash
   pip install --upgrade polyglot-ffi
   ```

2. **Validate Input:** Always validate OCaml interface files from untrusted sources

3. **Review Generated Code:** Review generated bindings before deploying to production

4. **Sandboxed Testing:** Test generated code in isolated environments first

5. **Dependencies:** Keep your dependencies updated
   ```bash
   pip list --outdated
   ```

### For Developers

1. **Code Review:** All code changes go through PR review

2. **Automated Scanning:** We use:
   - `safety` for dependency vulnerability scanning
   - `bandit` for security issue detection
   - GitHub Dependabot for automated updates

3. **Input Validation:** Always validate and sanitize user input

4. **Memory Safety:** Use proper memory management in generated C code
   - CAMLparam/CAMLreturn macros
   - Proper string ownership
   - GC-safe conversions

5. **Type Safety:** Leverage type systems to prevent errors
   - Python type hints
   - OCaml type constraints
   - C type declarations

## Known Security Considerations

### Generated C Code

The C stub code we generate includes:

- **Memory Management:** We use OCaml's GC-safe macros (CAMLparam, CAMLreturn)
- **String Handling:** Proper ownership and cleanup of string allocations
- **Null Pointer Checks:** Generated code includes appropriate null checks

### FFI Boundaries

When crossing language boundaries:

- **Type Marshalling:** Ensure proper type conversions at FFI boundaries
- **Error Handling:** Check return values and handle errors appropriately
- **Resource Cleanup:** Ensure resources are properly freed on both sides

### Build System

- **Dependency Integrity:** We use `pip` with hash verification in CI/CD
- **Supply Chain:** All dependencies are regularly updated and scanned
- **Reproducible Builds:** Our build process is deterministic

## Security Scanning

We use automated security scanning in our CI/CD pipeline:

```yaml
# Run on every PR and push
- safety check          # Check for known vulnerabilities
- bandit -r src/        # Static security analysis
- dependabot           # Automated dependency updates
```

You can run these locally:

```bash
# Install security tools
pip install safety bandit

# Check for vulnerabilities
safety check

# Run security linter
bandit -r src/
```

## Disclosure Policy

- **Coordinated Disclosure:** We follow a coordinated disclosure process
- **Embargo Period:** Typically 90 days to develop and release a fix
- **Public Advisory:** Published after fix is released
- **CVE Assignment:** We request CVEs for significant vulnerabilities

## Contact

For security-related questions or concerns:

- **GitHub:** https://github.com/chizy7/polyglot-ffi/security
- **Issues:** https://github.com/chizy7/polyglot-ffi/issues (for non-security bugs)

## Acknowledgments

We would like to thank the following researchers and contributors who have responsibly disclosed vulnerabilities:

- (None yet - you could be the first!)

## Additional Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [CWE Top 25](https://cwe.mitre.org/top25/archive/2023/2023_top25_list.html)
- [Python Security Best Practices](https://python.readthedocs.io/en/stable/library/security_warnings.html)
- [OCaml Security](https://ocaml.org/docs/security)

---

**Last Updated:** October 2025

Thank you for helping keep Polyglot FFI and our users safe!
