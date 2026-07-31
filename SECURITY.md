# Security Policy

## Supported versions

Security fixes are provided for the latest released version.

## Reporting a vulnerability

Please use GitHub's private vulnerability reporting feature for this
repository. Do not open a public issue for an undisclosed vulnerability.

Because litecache stores arbitrary Python objects in process memory, callers
are responsible for avoiding secrets that should not remain resident in the
application process.
