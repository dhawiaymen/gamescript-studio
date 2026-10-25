# GameScript Studio v0.1.0

First public release for developers who want local, inspectable game tools. Original
source is MIT licensed. No subscription, account or cloud backend is required.

## Included

- Full source, examples, tests and English documentation.
- `gamescript-studio-0.1.0-windows-x64.zip`: portable x64 application folder.
- `windows-verification.json`: results from launching the extracted executable.
- `SHA256SUMS.txt`: archive and verification-record checksums.


## Stabilization

- Normalize integer-valued JSON settings before editing; huge integers now produce validation errors.
- Protect unsaved work, add Save as and built-in examples, retain rule selection after edits.
- Bound and clean up preview folders; isolate the runtime from changes to its input configuration.

## Verification and limitations

The release job runs only after the Windows/Ubuntu Python 3.11–3.13 test matrix and
Windows packaging checks succeed. The archive is integrity-checked, extracted to a
separate path with spaces, and its executable opens Tk and performs a real operation.
See the attached verification record and the Actions run for the tagged commit.

Executables are unsigned. Native hosted-runner testing is not manual certification
of all Windows 10/11 desktops, display scaling, GPU drivers or antivirus configurations.
Read the README limitations and troubleshooting guide before reporting a problem.

Development used AI assistance. No user, download or adoption figures are claimed.
