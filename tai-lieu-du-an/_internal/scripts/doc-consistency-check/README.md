# Documentation Consistency Checker

Automated tool to validate consistency across BrowserManager API documentation files.

## What It Checks

1. **openapi.yaml completeness**
   - Verifies all 30 compat endpoints are present
   - Checks correct HTTP methods for each endpoint
   - Detects deprecated endpoints (e.g., `/api/env/delete`)

2. **Baseline consistency** (13-baseline-morelogin-public.md)
   - Validates endpoint names match MoreLogin standard
   - Checks HTTP methods are correct (POST not GET)
   - Ensures `/api/env/removeToRecycleBin/batch` is used instead of `/delete`

3. **Local API mapping** (04-local-api.md)
   - Verifies compat endpoint methods are correct
   - Checks mapping table consistency

4. **Parity matrix** (14-parity-matrix.md)
   - Validates endpoint names
   - Ensures no deprecated endpoints are referenced

## Usage

### Install dependencies

```bash
cd tai-lieu-du-an/scripts/doc-consistency-check
npm install
```

### Run the checker

```bash
npm run check
```

or directly:

```bash
node check.js
```

### Exit codes

- `0` - All checks passed
- `1` - Errors found (inconsistencies detected)
- `2` - Fatal error (script crashed)

## Integration with CI/CD

Add to your GitHub Actions workflow:

```yaml
- name: Check documentation consistency
  run: |
    cd tai-lieu-du-an/scripts/doc-consistency-check
    npm install
    npm run check
```

## Expected Output

### ✅ Success (all checks pass)

```
🔍 Starting Documentation Consistency Check...
📂 Documentation directory: /path/to/tai-lieu-du-an

📋 Checking openapi.yaml...
  Found 30 compat endpoints

📘 Checking 13-baseline-morelogin-public.md...
  Baseline checks complete

📗 Checking 04-local-api.md...
  Local API checks complete

📊 Checking 14-parity-matrix.md...
  Parity matrix checks complete

======================================================================
Documentation Consistency Check Results
======================================================================

✅ All checks passed! Documentation is consistent.
```

### ❌ Failure (inconsistencies found)

```
======================================================================
Documentation Consistency Check Results
======================================================================

❌ Found 3 error(s):
  1. Missing endpoint: POST /api/env/detail
  2. Baseline still uses deprecated /api/env/delete endpoint
  3. /api/env/getAllDebugInfo has wrong method in baseline: GET (should be POST)
```

## What to do if checks fail

1. **Missing endpoint**: Add the endpoint to `openapi.yaml`
2. **Wrong method**: Update the method in the affected file(s)
3. **Deprecated endpoint**: Replace with the correct endpoint name
4. **Inconsistency**: Sync the affected files to match the baseline

## Maintenance

To add new checks, edit `check.js` and add validation functions. Follow the pattern:

```javascript
function checkNewThing() {
  log('\n📌 Checking new thing...', 'blue');
  
  // Your validation logic here
  // Use errors.push('error message') to report errors
  // Use warnings.push('warning message') to report warnings
  
  log('  New thing checks complete', 'green');
}
```

Then call it in the main execution block.
