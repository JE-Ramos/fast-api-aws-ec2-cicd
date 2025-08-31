# Branch Protection Rules Configuration

To enable proper PR review process, configure these branch protection rules in GitHub:

## Main Branch Protection

1. Go to **Settings** → **Branches** → **Add rule**
2. **Branch name pattern:** `main`
3. **Protection settings:**
   - ✅ Require a pull request before merging
   - ✅ Require approvals: **1**
   - ✅ Dismiss stale PR approvals when new commits are pushed
   - ✅ Require review from code owners (if using CODEOWNERS file)
   - ✅ Require status checks to pass before merging
   - ✅ Require branches to be up to date before merging
   - **Required status checks:**
     - `Static Code Analysis`
     - `Unit Tests`
     - `Integration Tests` 
     - `Build Validation`
     - `PR Review Summary`
   - ✅ Require conversation resolution before merging
   - ✅ Include administrators (recommended)

## Develop Branch Protection

1. **Branch name pattern:** `develop`
2. **Protection settings:**
   - ✅ Require a pull request before merging
   - ✅ Require approvals: **1**
   - ✅ Require status checks to pass before merging
   - ✅ Require branches to be up to date before merging
   - **Required status checks:**
     - `Static Code Analysis`
     - `Unit Tests`
     - `Integration Tests`
     - `Build Validation`
     - `PR Review Summary`

## Automatic Deployments

With these rules in place:
- **Develop branch** → Automatically deploys to staging when PR is merged
- **Main branch** → Automatically deploys to production when PR is merged

## Status Check Names

The required status checks correspond to job names in `.github/workflows/pr-checks.yml`:
- `Static Code Analysis` → `static-analysis`
- `Unit Tests` → `unit-tests` 
- `Integration Tests` → `integration-tests`
- `Build Validation` → `build-validation`
- `PR Review Summary` → `pr-summary`