#!/usr/bin/env bash
# Run a Sonar analysis from your laptop against the existing SonarCloud
# project. No Docker, no local server — just the scanner pushing results
# up to sonarcloud.io.
#
# Setup once:
#   pip install pysonar                          # or: brew install sonar-scanner
#   Create a token at https://sonarcloud.io/account/security
#   export SONAR_TOKEN=<your-token>
#
# Optional: scan a specific pull request
#   PR=170 scripts/run_sonar_local.sh
set -euo pipefail

if [[ -z "${SONAR_TOKEN:-}" ]]; then
    echo "ERROR: SONAR_TOKEN env var is not set." >&2
    echo "  Create a token at https://sonarcloud.io/account/security" >&2
    exit 1
fi

# Pick whichever scanner is on PATH (sonar-scanner is the Java CLI;
# pysonar is the Python wrapper from SonarSource — works the same).
if command -v sonar-scanner >/dev/null 2>&1; then
    SCANNER=sonar-scanner
elif command -v pysonar >/dev/null 2>&1; then
    SCANNER=pysonar
else
    echo "ERROR: neither sonar-scanner nor pysonar found on PATH." >&2
    echo "  Install one of:  pip install pysonar" >&2
    echo "                   brew install sonar-scanner" >&2
    exit 1
fi

# Generate coverage XML for sonar to ingest. `sonar-project.properties`
# already points at `coverage.xml`.
python -m pytest tests/ --cov=core_lib --cov-report=xml -q

PR_ARGS=()
if [[ -n "${PR:-}" ]]; then
    BRANCH=$(git rev-parse --abbrev-ref HEAD)
    BASE=$(git remote show origin | sed -n '/HEAD branch/s/.*: //p')
    PR_ARGS=(
        "-Dsonar.pullrequest.key=${PR}"
        "-Dsonar.pullrequest.branch=${BRANCH}"
        "-Dsonar.pullrequest.base=${BASE:-master}"
    )
fi

"${SCANNER}" \
    -Dsonar.host.url=https://sonarcloud.io \
    -Dsonar.token="${SONAR_TOKEN}" \
    ${PR_ARGS[@]+"${PR_ARGS[@]}"}

echo
echo "See results at https://sonarcloud.io/dashboard?id=shay-te_core-lib"
