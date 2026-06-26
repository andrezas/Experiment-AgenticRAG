#!/usr/bin/env bash
#
# This script analyzes changed files in a Git repository using SonarQube.
# It copies only the changed files, starts SonarQube via Docker,
# runs the analysis, and then cleans up.
#
# Usage: ./run_sonarqube.sh <path_to_repository>
#

set -eo pipefail

# SonarQube Configuration
readonly SONAR_URL="http://localhost:9000"
readonly SONAR_API_URL="${SONAR_URL}/api"
readonly ADMIN_USER="admin"
readonly ADMIN_PASS="admin"
readonly NEW_PASS="Synchro@1234"
readonly TOKEN_NAME="ci-token-$(date +%s)" # Unique token name

# Git Configuration
readonly REPO_PATH="${1}"
readonly BASE_BRANCH="origin/dev"

# Directory for storing changed files
readonly WORKSPACE="${REPO_PATH}/sonar_workspace"

readonly DOCKER_CMD="docker compose -f ${REPO_PATH}/docker-compose.sonar.yml"

# Prints a message in a given color.
log() {
    local color_name="$1"
    local message="$2"
    local color_code

    case "${color_name}" in
        green)  color_code="\e[1;92m" ;;
        red)    color_code="\e[1;31m" ;;
        yellow) color_code="\e[1;33m" ;;
        blue)   color_code="\e[1;34m" ;;
        *)      color_code="\e[0m" ;;
    esac
    
    # Print the colored message, followed by a reset to default color
    echo -e "${color_code}${message}\e[0m"
}

 # Displays a spinner while a command is running.
run_with_spinner() {
    local message="$1"
    shift # Remove the message from the arguments list
    local cmd=("$@")
    local spinner="⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"
    local i=0

    # Execute the command in the background
    "${cmd[@]}" &
    local pid=$!

    local prev_trap
    prev_trap=$(trap -p EXIT || true)

    # Trap to kill the command if the script exits
    trap "kill $pid 2>/dev/null" EXIT

    while ps -p $pid > /dev/null; do
        printf "\r\e[1;33m%s %s\e[0m" "${spinner:i++%${#spinner}:1}" "$message"
        sleep 0.1
    done

    # Remove the trap and wait for the command to finish, capturing its exit code
    trap - EXIT

    # Restore previous EXIT trap (if any)
    if [[ -n "${prev_trap}" ]]; then
        eval "${prev_trap}"
    fi

    # Wait for the background command (to capture its exit code) and return it
    wait $pid
    return $?
}

check_dependencies() {
    log "blue" "Checking for required tools..."
    local missing_tools=0
    for tool in git docker curl jq; do
        if ! command -v "${tool}" &> /dev/null; then
            log "red" "Error: '${tool}' is not installed or not in PATH."
            missing_tools=1
        fi
    done
    [[ ${missing_tools} -eq 0 ]] || exit 1
}

detect_current_branch() {
    if [[ ! -d "${REPO_PATH}" ]]; then
        CURRENT_BRANCH="unknown"
        return 1
    fi

    # Prefer readable branch name; if detached, fall back to short SHA
    CURRENT_BRANCH=$(git -C "${REPO_PATH}" rev-parse --abbrev-ref HEAD 2>/dev/null || true)
    if [[ -z "${CURRENT_BRANCH}" || "${CURRENT_BRANCH}" == "HEAD" ]]; then
        CURRENT_BRANCH=$(git -C "${REPO_PATH}" rev-parse --short HEAD 2>/dev/null || echo "detached-HEAD")
    fi
}

copy_changed_files() {
    log "yellow" "Identifying changed files against '${BASE_BRANCH}'..."
    # Navigate to the repository, or exit if it fails
    cd "${REPO_PATH}" || { log "red" "Could not access repository path: ${REPO_PATH}"; exit 1; }

    # Fetch the latest from origin to ensure the base branch is up-to-date
    git fetch origin

    local changed_files
    changed_files=$(git diff --name-only "${BASE_BRANCH}...HEAD")

    if [[ -z "${changed_files}" ]]; then
        log "green" "No files have changed. Nothing to analyze. Exiting."
        exit 0
    fi

    log "yellow" "Copying changed files to workspace: ${WORKSPACE}"
    rm -rf "${WORKSPACE}"
    mkdir -p "${WORKSPACE}"

    existing_files=$(echo "${changed_files}" | while read -r file; do
        [ -e "$file" ] && echo "$file"
    done)

    # Use rsync for efficient copying, preserving directory structure
    echo "${existing_files}" | rsync -av --files-from=- . "${WORKSPACE}"
    cp "${REPO_PATH}/sonar-project.properties" "${WORKSPACE}/sonar-project.properties"
    cp "${REPO_PATH}/coverage.xml" "${WORKSPACE}/coverage.xml"
    mkdir -p "${WORKSPACE}/tests"
    mkdir -p "${WORKSPACE}/src"
    rsync -a --exclude=".git/hooks" --exclude=".git/logs" "${REPO_PATH}/.git" "${WORKSPACE}/.git"

    cd - > /dev/null # Go back to the original directory quietly
}

start_sonarqube() {
    log "yellow" "Starting SonarQube containers..."
    ${DOCKER_CMD} up -d --remove-orphans
    log "blue" "SonarQube dashboard will be available at: ${SONAR_URL}"
    log "default" "Default credentials: ${ADMIN_USER} / ${NEW_PASS}"
}

wait_for_sonarqube() {
    local start_time
    start_time=$(date +%s)
    
    # Loop until the SonarQube API reports its status as "UP"
    until curl -sf "${SONAR_API_URL}/system/status" | jq -e '.status == "UP"' > /dev/null; do
        sleep 5
    done
    
    local end_time
    end_time=$(date +%s)
    local elapsed=$((end_time - start_time))
    printf "\r\033[K" # Clear the spinner line
    log "green" "SonarQube is UP! (Took ${elapsed}s)"
}

configure_sonarqube() {
    log "yellow" "Configuring SonarQube..."

    # Change the default admin password
    local change_pwd_resp
    change_pwd_resp=$(curl -s -o /tmp/change_pwd.json -w "%{http_code}" \
      -u "${ADMIN_USER}:${ADMIN_PASS}" \
      -X POST "${SONAR_API_URL}/users/change_password" \
      -d "login=${ADMIN_USER}" \
      -d "previousPassword=${ADMIN_PASS}" \
      -d "password=${NEW_PASS}")

    if [[ "$change_pwd_resp" -ne 204 ]]; then
        log "red" "Failed to change admin password (HTTP status: $change_pwd_resp). Response:"
        cat /tmp/change_pwd.json
        exit 1
    fi

    # Generate a new analysis token
    local token_resp_code
    token_resp_code=$(curl -s -o /tmp/token.json -w "%{http_code}" \
      -u "${ADMIN_USER}:${NEW_PASS}" \
      -X POST "${SONAR_API_URL}/user_tokens/generate" \
      -d "name=${TOKEN_NAME}" \
      -d "login=${ADMIN_USER}")

    if [[ "$token_resp_code" -ne 200 ]]; then
        log "red" "Failed to request token (HTTP status: $token_resp_code). Response:"
        cat /tmp/token.json
        exit 1
    fi

    SONAR_TOKEN=$(jq -r '.token' /tmp/token.json)
    if [[ -z "$SONAR_TOKEN" || "$SONAR_TOKEN" == "null" ]]; then
        log "red" "Failed to extract token from response:"
        jq . /tmp/token.json
        exit 1
    fi

    log "green" "SonarQube correctly configured"
}

run_scanner() {
    log "yellow" "Running SonarScanner analysis..."

    ${DOCKER_CMD} run --rm sonar-scanner \
        -Dsonar.projectBaseDir=/usr/src \
        -Dsonar.host.url=http://sonarqube:9000 \
        -Dsonar.token="${SONAR_TOKEN}"
    
    log "green" "SonarScanner analysis complete"
}

parse_sonar_properties() {
    local properties_file="${REPO_PATH}/sonar-project.properties"

    if [[ ! -f "$properties_file" ]]; then
        log "red" "Missing sonar-project.properties at ${properties_file}"
        exit 1
    fi

    PROJECT_KEY=$(grep -E '^sonar\.projectKey=' "$properties_file" | cut -d'=' -f2- | tr -d '[:space:]')
    PROJECT_NAME=$(grep -E '^sonar\.projectName=' "$properties_file" | cut -d'=' -f2- | tr -d '[:space:]')

    if [[ -z "$PROJECT_KEY" || -z "$PROJECT_NAME" ]]; then
        log "red" "Failed to extract projectKey or projectName from sonar-project.properties"
        exit 1
    fi
}


map_rating_to_letter() {
    case "$1" in
        1.0) echo "A" ;;
        2.0) echo "B" ;;
        3.0) echo "C" ;;
        4.0) echo "D" ;;
        5.0) echo "E" ;;
        *) echo "N/A" ;;
    esac
}


generate_markdown_report() {
    log "yellow" "Generating Markdown report..."

    local report_file="${REPO_PATH}/sonar-report.md"

    {
        echo "# 🧪 SonarQube Analysis Report"
        echo ""
        echo "This report summarizes the static code analysis performed by SonarQube on the branch ${CURRENT_BRANCH} compared to ${BASE_BRANCH}."
        echo ""

        # Project Info
        local project_json
        project_json=$(curl -s -u "${ADMIN_USER}:${NEW_PASS}" "${SONAR_API_URL}/components/show?component=${PROJECT_KEY}")
        local fetched_name
        fetched_name=$(echo "$project_json" | jq -r '.component.name // "-"')
        echo "## 📌 Project Info"
        echo ""
        echo "- **Project Name**: ${fetched_name}"
        echo "- **Project Key**: ${PROJECT_KEY}"
        echo ""

        # Quality Gate Status
        local gate_json
        gate_json=$(curl -s -u "${ADMIN_USER}:${NEW_PASS}" "${SONAR_API_URL}/qualitygates/project_status?projectKey=${PROJECT_KEY}")
        local gate_status
        gate_status=$(echo "$gate_json" | jq -r '.projectStatus.status')
        local gate_icon="❌"
        [[ "$gate_status" == "OK" ]] && gate_icon="✅"

        echo "## 🚦 Quality Gate Status"
        echo ""
        echo "- **Status**: ${gate_icon} ${gate_status}"
        echo ""

        # Key Metrics
        echo "## 📊 Metrics Summary"
        echo ""
        echo "| Metric        | Rating / Value     |"
        echo "|------------------|--------------------|"

        local metrics=(
            coverage
            duplicated_lines_density
            sqale_rating
            software_quality_maintainability_issues
            reliability_rating
            software_quality_reliability_issues
            security_rating
            software_quality_security_issues
            security_hotspots
            security_review_rating
        )
        local metric_keys=$(IFS=,; echo "${metrics[*]}")

        local measures_json=$(
            curl --fail -sS -u "${ADMIN_USER}:${NEW_PASS}" \
                "${SONAR_API_URL}/measures/component?component=${PROJECT_KEY}&metricKeys=${metric_keys}"
        ) || {
            echo "Error: failed to fetch measures from SonarQube API." >&2
            exit 2
        }

        declare -A metric_labels=(
            [coverage]="Coverage"
            [duplicated_lines_density]="Duplicated Lines"
            [sqale_rating]="Maintainability Rating"
            [software_quality_maintainability_issues]="Maintainability Issues"
            [reliability_rating]="Reliability Rating"
            [software_quality_reliability_issues]="Reliability Issues"
            [security_rating]="Security Rating"
            [software_quality_security_issues]="Security Issues"
            [security_hotspots]="Security Hotspots"
            [security_review_rating]="Security Hotspots Rating"
        )

        declare -A metric_values
        while IFS=$'\t' read -r metric value; do
            metric_values["$metric"]="$value"
        done < <(echo "$measures_json" | jq -r '.component.measures[] | [.metric, .value] | @tsv')

        for metric in "${metrics[@]}"; do
            if [[ -n "${metric_values[$metric]}" ]]; then
                label="${metric_labels[$metric]:-$metric}"
                value="${metric_values[$metric]}"

                case "$metric" in
                    *_rating)
                        echo "| ${label} | $(map_rating_to_letter "${value}") |"
                        ;;
                    coverage)
                        echo "| ${label} | ${value}% |"
                        ;;
                    *)
                        echo "| ${label} | ${value} |"
                        ;;
                esac
            fi
        done
        echo ""

        # Top Issues
        echo "## 🐞 Top Issues"
        echo ""
        echo "| Type        | Severity | File                            | Line | Message                             |"
        echo "|-------------|----------|---------------------------------|------|-------------------------------------|"

        local issues_json
        issues_json=$(curl -s -u "${ADMIN_USER}:${NEW_PASS}" \
            "${SONAR_API_URL}/issues/search?componentKeys=${PROJECT_KEY}&ps=20&s=SEVERITY&asc=false")

        echo "$issues_json" | jq -r '
        if (.issues // []) | length == 0 then
            "\nNo issues found."
        else
            .issues[] |
            "| \(.type) | \(.severity) | \(.component | split(":")[2]) | \(.line // "-") | \(.message | gsub("\n"; " ")) |"
        end
        '

        echo ""
        echo "## 🐞 Security Hotspots"
        echo ""
        echo "| Status      | Probability | File                            | Line | Message                             |"
        echo "|-------------|-------------|---------------------------------|------|-------------------------------------|"

        hotspots_json=$(curl -s -u "${ADMIN_USER}:${NEW_PASS}" \
        "${SONAR_API_URL}/hotspots/search?projectKey=${PROJECT_KEY}&ps=20&s=SEVERITY&asc=false")

        echo "$hotspots_json" | jq -r '
        if (.hotspots // []) | length == 0 then
            "\nNo hotspots found."
        else
            .hotspots[] |
            "| \(.status // "-") | \(.vulnerabilityProbability // "-") | \((.component // "") | split(":")[-1]) | \(.line // "-") | \(.message // "" | gsub("\n"; " ")) |"
        end
        '
    } > "${report_file}"

    log "green" "Markdown report saved to: ${report_file}"
}


cleanup() {
    local exit_code=$1
    set +e

    log "yellow" "\nPerforming cleanup..."
    
    # Revoke the generated token if it exists
    if [[ -n "${SONAR_TOKEN-}" ]]; then
        log "blue" "Revoking SonarQube token..."
        curl -s -u "${ADMIN_USER}:${NEW_PASS}" -X POST \
          "${SONAR_API_URL}/user_tokens/revoke?name=${TOKEN_NAME}" > /dev/null
    fi
    
    # Stop and remove Docker containers
    log "blue" "Stopping SonarQube containers..."
    ${DOCKER_CMD} down --volumes
    
    # Remove the temporary workspace
    log "blue" "Removing workspace: ${WORKSPACE}"
    rm -rf "${WORKSPACE}"
    
    log "green" "Cleanup complete"

    exit ${exit_code}
}

main() {
    # Register the cleanup function to run on script exit (normal or error)
    trap 'cleanup $?' EXIT
    
    if [[ -z "${REPO_PATH}" ]]; then
        log "red" "Repository path not provided!"
        log "default" "Usage: $0 <repository_path>"
        exit 1
    fi

    check_dependencies
    detect_current_branch
    parse_sonar_properties
    copy_changed_files
    start_sonarqube
    run_with_spinner "Waiting for SonarQube to start..." wait_for_sonarqube
    configure_sonarqube
    run_scanner
    generate_markdown_report

    log "green" "\n✅ Analysis complete. SonarQube is still running at ${SONAR_URL}"
    log "yellow" "Press Ctrl+C to shut down containers and perform cleanup."

    # Wait indefinitely until a signal is caught by the trap.
    while true; do
        sleep 1
    done
}

main "$@"
