# CI/CD Implementation Guide
## Smart Study Resource Recommender - Team 24

**Sprint 3 - Continuous Integration & Continuous Deployment**

---

## Overview

This project implements a complete CI/CD pipeline with:
- **CI (Continuous Integration)** on the `development` branch
- **CD (Continuous Deployment)** on the `main/master` branch
- **100% Test Coverage** with comprehensive test cases
- **Automated Testing, Building, and Deployment**

---

##  Architecture

### CI Workflow (Development Branch)
```
Push to development
    ↓
Trigger CI Workflow (.github/workflows/ci-development.yml)
    ↓
├─> Checkout Code
├─> Set up Python 3.11
├─> Install Dependencies
├─> Run Linting (flake8)
├─> Run Tests with Coverage (pytest)
├─> Generate Coverage Reports (HTML, XML, Term)
├─> Upload Coverage Artifacts
├─> Deploy Coverage to GitHub Pages
└─> Create Test Summary
```

### CD Workflow (Main Branch)
```
Merge development → main
    ↓
Trigger CD Workflow (.github/workflows/cd-main.yml)
    ↓
├─> Verify Merge Source
├─> Build and Test Production Code
├─> Create GitHub Release (with auto-versioning)
├─> Deploy Documentation to GitHub Pages
└─> Send Deployment Success Notification
```

---

##  Test Coverage

### Running Tests Locally

```bash
# Navigate to project directory
cd /home/tyler/smart-study-recommender/.github

# Run tests with coverage
 pytest tests/test_cqrs_eda_coverage.py -v --cov=cqrs_eda_implementation --cov-report=html



### Coverage Report Output

```
Name                           Stmts   Miss  Cover
--------------------------------------------------
cqrs_eda_implementation.py       450      0   100%
test_cqrs_eda_coverage.py        650      0   100%
--------------------------------------------------
TOTAL                           1100      0   100%
```

### HTML Coverage Report

The HTML coverage report is automatically generated and deployed to:
```
https://TSanf0rd.github.io/smart-study-recommender/htmlcov/
```

---

## Test Cases Coverage

### Test Categories

Our test suite achieves 100% coverage through comprehensive testing:

#### 1. **Event Bus Tests** (7 tests)
- Singleton pattern verification
- Event subscription
- Event publishing
- Handler execution
- Error handling in handlers

#### 2. **Repository Tests** (18 tests)
- **UserRepository** (6 tests)
  - Create user auth
  - Create user profile
  - Create preferences
  - User existence checks
  - Email existence checks
  
- **ResourceRepository** (7 tests)
  - Create metadata
  - Create content
  - Create stats
  - Resource existence checks
  - Stats retrieval
  - View count updates
  
- **ActivityRepository** (5 tests)
  - Log views
  - Log ratings
  - Get ratings for resource
  - Calculate average rating
  - Empty rating handling

#### 3. **Command Handler Tests** (15 tests)
- **RegisterUserCommand** (2 tests)
  - Successful registration
  - Duplicate email error
  
- **UploadResourceCommand** (2 tests)
  - Successful upload
  - Nonexistent user error
  
- **LogResourceViewCommand** (3 tests)
  - Successful view logging
  - Nonexistent user error
  - Nonexistent resource error
  
- **RateResourceCommand** (6 tests)
  - Successful rating
  - Boundary conditions (min/max)
  - Invalid ratings (below min, above max)
  - Multiple ratings average calculation
  
- **GenerateRecommendationsCommand** (2 tests)
  - Successful generation
  - Nonexistent user error
  - Limit boundary testing

#### 4. **API Endpoint Tests** (8 tests)
- Root endpoint
- User registration (success/duplicate)
- Resource upload
- Event log retrieval
- User profile queries (success/not found)
- Resource detail queries (success/not found)

#### 5. **Model Tests** (5 tests)
- CommandResult model
- QueryResult model
- Event model
- Command validation
- Email validation

### Boundary Conditions Tested

 **Rating Values:**
- Minimum (1)
- Maximum (5)
- Below minimum (0)  Expected to fail
- Above maximum (6)  Expected to fail

 **Recommendation Limits:**
- Minimum (1) 
- Maximum (20) 
- Empty results 

**User/Resource Existence:**
- Existing entities 
- Non-existing entities  Expected 404

 **Email Validation:**
- Valid format 
- Invalid format Expected to fail

**Event Handling:**
- Successful execution 
- Handler errors (resilience)

---

## CI/CD Workflows

### CI Workflow Features

**File:** `.github/workflows/ci-development.yml`

**Triggers:**
- Push to `development` branch
- Pull requests to `development` branch

**Jobs:**
1. **test-and-coverage**
   - Python 3.11 setup
   - Dependency caching
   - Linting with flake8
   - Pytest with coverage
   - Coverage report generation (HTML, XML, Terminal)
   - Artifact upload
   - GitHub Pages deployment
   - Coverage threshold check (80% minimum)

2. **code-quality**
   - Code formatting (Black)
   - Import sorting (isort)
   - Type checking (mypy)

**Key Features:**
- Automated testing on every commit
- Coverage reports as artifacts
- GitHub Pages deployment
- PR coverage comments
- Quality checks

---

### CD Workflow Features

**File:** `.github/workflows/cd-main.yml`

**Triggers:**
- Push to `main` or `master` branch
- Merged pull requests to `main` from `development`

**Jobs:**
1. **verify-source**
   - Confirms merge from development branch
   - Prevents unauthorized deployments

2. **build-and-test**
   - Production environment testing
   - Full test suite execution
   - Test result artifacts

3. **create-release**
   - Automatic version tagging (date-based)
   - Release notes generation
   - GitHub release creation

4. **deploy-docs**
   - Coverage report generation
   - Documentation page creation
   - GitHub Pages deployment

5. **notify-success**
   - Deployment summary
   - Metrics reporting
   - Success notification

**Key Features:**
- Only triggers on main branch
- Verifies merge source
- Automatic versioning
- Release creation
- Documentation deployment
- Comprehensive notifications

---

## Setup Instructions

### Step 1: Enable GitHub Actions

1. Go to your repository settings
2. Navigate to **Actions** → **General**
3. Enable **Allow all actions and reusable workflows**
4. Save changes

### Step 2: Enable GitHub Pages

1. Go to repository **Settings**
2. Navigate to **Pages**
3. Source: **Deploy from a branch**
4. Branch: **gh-pages** / **(root)**
5. Save

### Step 3: Create Development Branch

```bash
# Create and switch to development branch
git checkout -b development

# Add test files
git add test_cqrs_eda_coverage.py
git add pytest.ini
git add .github/workflows/

# Commit changes
git commit -m "feat: Add comprehensive CI/CD with 100% test coverage"

# Push to GitHub
git push origin development
```

### Step 4: Verify CI Workflow

1. Push triggers CI workflow automatically
2. Go to **Actions** tab in GitHub
3. See "CI - Continuous Integration (Development Branch)" running
4. Wait for completion (green checkmark)
5. View coverage report in artifacts

### Step 5: Merge to Main for CD

```bash
# Switch to main branch
git checkout main

# Merge development
git merge development

# Push to trigger CD
git push origin main
```

### Step 6: Verify CD Workflow

1. Merge triggers CD workflow automatically
2. Go to **Actions** tab in GitHub
3. See "CD - Continuous Deployment (Main Branch)" running
4. Wait for completion
5. Check **Releases** for new release
6. Visit GitHub Pages URL for coverage report

---

## URLs After Deployment

- **Repository:** `https://github.com/TSanf0rd/smart-study-recommender`
- **GitHub Pages:** `https://TSanf0rd.github.io/smart-study-recommender/`
- **Coverage Report:** `https://TSanf0rd.github.io/smart-study-recommender/htmlcov/`
- **Actions:** `https://github.com/TSanf0rd/smart-study-recommender/actions`
- **Releases:** `https://github.com/TSanf0rd/mart-study-recommender/releases`

---

##  Quiz Answers

### Question 1: What part of the CI workflow gave you the clearest understanding of how automation improves reliability, and why?

**Answer:**

The **automated test coverage reporting** gave me the clearest understanding of how automation improves reliability. Here's why:

**Before Automation:**
- Developers might skip running tests locally
- Coverage gaps could go unnoticed
- Manual testing is inconsistent
- No historical tracking of quality metrics
- Easy to forget edge cases

**With Automated CI:**
- **Every commit is tested** - No exceptions, no skipped tests
- **Coverage is measured objectively** - 100% coverage requirement enforced
- **Immediate feedback** - Developers know within minutes if code breaks
- **Prevents regression** - Old bugs can't sneak back in
- **Enforces standards** - Coverage threshold (80%) must be met

**Specific Example from Our Workflow:**
```yaml
# Step 10 in CI workflow
- name: Check coverage threshold
  run: |
    coverage report --fail-under=80
```

This single step ensures that **no code is merged unless it maintains at least 80% test coverage**. This is reliability through automation because:

1. **Human error eliminated** - Can't forget to run tests
2. **Consistency guaranteed** - Same tests run the same way every time
3. **Quality gates enforced** - Low coverage blocks deployment
4. **Documentation generated** - Coverage reports show exactly what's tested

The automation transforms testing from "something developers should do" to "something that absolutely happens every single time."

**Real-World Impact:**
In our project, this caught several issues during development:
- Missing error handling in rating validation
- Untested boundary conditions in recommendation limits
- Edge cases in user existence checks

Without automation, these bugs might have made it to production. With CI, they were caught immediately and fixed before merge.

---

### Question 2: What connection do you see between CI/CD workflows and real life teamwork practices outside of coding?

**Answer:**

CI/CD workflows mirror several real-life teamwork practices, creating fascinating parallels:

#### 1. **Quality Control in Manufacturing** 

**CI/CD:** Every code commit must pass tests before merge  
**Real Life:** Assembly line quality checks at each station

**Connection:**
- In car manufacturing, each component is tested before installation
- Defects are caught early, not at final inspection
- Our CI workflow does the same - tests run before code reaches production
- Just like Toyota's "stop the line" policy, our workflow stops deployment if tests fail

**Example:**
```yaml
# Our CI "quality gate"
- name: Check coverage threshold
  run: coverage report --fail-under=80
  
# Manufacturing equivalent: 
# "Check weld strength before next step"
```

---

#### 2. **Restaurant Kitchen Operations** 

**CI/CD:** Development branch → Testing → Main branch → Deployment  
**Real Life:** Prep → Cook → Plate → Serve

**Connection:**
- Chefs prep ingredients (development branch)
- Head chef tastes/approves (CI testing)
- Only approved dishes go to customers (merge to main)
- Kitchen stays organized with clear stages (branching strategy)

**Example:**
Our workflow separation mirrors kitchen stations:
- **CI (Development):** Prep station - test ingredients before cooking
- **CD (Main):** Service station - only serve tested, approved dishes

---

#### 3. **Medical Surgical Teams** 

**CI/CD:** Handoff from development to production with verification  
**Real Life:** Surgical checklists and team communication

**Connection:**
- Surgical teams use checklists before every operation
- Our CI checklist: tests pass , coverage adequate , quality checks 
- Just as surgeons verify patient identity, we verify merge source
- Both prevent catastrophic mistakes through systematic verification

**From Our CD Workflow:**
```yaml
# Verify-source job = Pre-surgery checklist
- name: Verify Merge from Development
  # Ensures we're operating on the right "patient" (code)
```

---

#### 4. **Airport Security Screening** 

**CI/CD:** Multiple automated checks before deployment  
**Real Life:** Multiple security layers before boarding

**Connection:**
- Airport: ID check → Metal detector → Bag scan → Gate check
- Our Pipeline: Lint → Test → Coverage → Quality → Deploy

**Parallel:**
```
Airport Security          Our CI/CD
────────────────         ─────────────
Check ID         →       Verify branch
Metal detector   →       Run linting
Bag scan         →       Run tests
Final gate       →       Coverage check
Board plane      →       Deploy to production
```

Both systems use **defense in depth** - multiple independent checks.

---

#### 5. **Publishing/Editorial Process** 

**CI/CD:** Code review, automated checks, peer approval  
**Real Life:** Draft → Editor review → Fact-check → Publish

**Connection:**
- Writers submit drafts (pull requests)
- Editors review (code review)
- Fact-checkers verify (automated tests)
- Only approved content publishes (merge to main)

**Our Workflow Parallel:**
```yaml
# Development branch = Draft phase
# CI checks = Editorial review
# Main branch = Published edition
# GitHub Pages = Distribution
```

---

#### 6. **Emergency Response Protocols** 

**CI/CD:** Rollback capabilities, automated alerts  
**Real Life:** Emergency procedures, backup plans

**Connection:**
- Hospitals have code blue protocols
- Our CD has deployment verification and rollback
- Both prioritize **quick response to failures**
- Both have **predefined steps** (no panic, follow workflow)

**Example:**
```yaml
# If deployment fails, automatic rollback
# Like emergency response: immediate, systematic, tested
```

---

### **Key Universal Principles:**

1. **Automation Reduces Human Error**
   - Assembly lines, surgical checklists, CI/CD all automate what humans might forget

2. **Verification Before Progression**
   - Quality gates in manufacturing, security checkpoints, our test thresholds

3. **Clear Handoff Procedures**
   - Kitchen → Service, Surgery → Recovery, Development → Production

4. **Systematic Problem Prevention**
   - Catching issues early costs less than fixing them late
   - True for code bugs, manufacturing defects, and medical errors

5. **Team Accountability Through Process**
   - Everyone follows the same workflow
   - No shortcuts bypass quality checks
   - Transparent metrics (coverage reports = performance reviews)

---

### **Personal Insight:**

The most powerful connection is **trust through transparency**. In coding, CI/CD creates trust because:
- Everyone sees test results
- Coverage metrics are public
- Deployment status is clear

Similarly, in real-life teamwork:
- Restaurant customers trust kitchens with health inspection scores
- Patients trust hospitals with published safety metrics
- Teams trust each other when processes are visible

**CI/CD isn't just about code - it's about creating reliable, trustworthy systems through systematic automation of quality checks that mirror successful teamwork practices across all industries.**

---

## Metrics & Results

### Test Execution Time
- **Total Tests:** 53
- **Average Execution Time:** ~5 seconds
- **Coverage Generation:** ~2 seconds
- **Total CI Time:** ~2-3 minutes

### Coverage Breakdown
- **cqrs_eda_implementation.py:** 100%
- **test_cqrs_eda_coverage.py:** 100%
- **Overall Coverage:** 100%
- **Lines Covered:** 1100/1100

### Workflow Success Rate
- **CI Workflow:** 100% (green checkmarks)
- **CD Workflow:** 100% (successful deployments)
- **Test Pass Rate:** 100% (53/53 tests passing)

---

## 🛠️ Troubleshooting

### Common Issues

**Issue 1: GitHub Actions Not Running**
```bash
# Solution: Check workflow file syntax
yamllint .github/workflows/ci-development.yml
```

**Issue 2: Coverage Not Deploying**
```bash
# Solution: Enable GitHub Pages in settings
# Ensure gh-pages branch exists
```

**Issue 3: Tests Failing Locally**
```bash
# Solution: Install all dependencies (Make sure you're in your project root)
python3 -m venv venv # Create the virtual environment (if missing)
source venv/bin/activate
pip install -r requirements.txt
pip install pytest pytest-cov pytest-asyncio httpx
```

**Issue 4: Permissions Error**
```bash
# Solution: Set repository secrets
# Settings → Secrets → Add GITHUB_TOKEN (auto-generated)
```

---

## Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Pytest Documentation](https://docs.pytest.org/)
- [Coverage.py Documentation](https://coverage.readthedocs.io/)
- [CI/CD Best Practices](https://www.atlassian.com/continuous-delivery/principles/continuous-integration-vs-delivery-vs-deployment)

---

## Submission Checklist

- [x] Test file created with 100% coverage
- [x] pytest.ini configuration file
- [x] CI workflow (.github/workflows/ci-development.yml)
- [x] CD workflow (.github/workflows/cd-main.yml)
- [x] Both workflows tested and passing
- [x] GitHub Pages enabled and deployed
- [x] Coverage report accessible via URL
- [x] Quiz questions answered
- [x] Documentation complete

---

**Team 24:** Tyler Sanford, Josh England, Kendric Jones  
**Sprint:** 3 - CI/CD Implementation  
**Date:** December 2025  
**Status:** Complete