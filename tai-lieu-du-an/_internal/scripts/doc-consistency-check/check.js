#!/usr/bin/env node

/**
 * Documentation Consistency Checker
 * 
 * Validates that all API documentation files are consistent:
 * - openapi.yaml has all 30 compat endpoints
 * - Methods match between openapi.yaml and baseline
 * - Endpoint names are consistent across all docs
 * - No deprecated endpoints (like /api/env/delete)
 */

const fs = require('fs');
const path = require('path');
const yaml = require('js-yaml');

// ANSI color codes
const colors = {
  reset: '\x1b[0m',
  red: '\x1b[31m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  bold: '\x1b[1m'
};

const docsDir = path.join(__dirname, '../../..');
const errors = [];
const warnings = [];

// Expected endpoints from MoreLogin baseline (30 total)
const EXPECTED_ENDPOINTS = {
  '/api/env': [
    { path: '/api/env/create/quick', method: 'POST' },
    { path: '/api/env/create/advanced', method: 'POST' },
    { path: '/api/env/start', method: 'POST' },
    { path: '/api/env/close', method: 'POST' },
    { path: '/api/env/closeAll', method: 'POST' },
    { path: '/api/env/active', method: 'POST' },
    { path: '/api/env/reopen', method: 'POST' },
    { path: '/api/env/page', method: 'POST' },
    { path: '/api/env/list', method: 'POST' },
    { path: '/api/env/detail', method: 'POST' },
    { path: '/api/env/update', method: 'POST' },
    { path: '/api/env/removeToRecycleBin/batch', method: 'POST' },
    { path: '/api/env/getAllDebugInfo', method: 'POST' },
    { path: '/api/env/getAllProcessIds', method: 'POST' },
    { path: '/api/env/getAllScreen', method: 'POST' },
    { path: '/api/env/removeLocalCache', method: 'POST' },
    { path: '/api/env/cache/cleanCloud', method: 'POST' },
    { path: '/api/env/arrangeWindows', method: 'POST' }
  ],
  '/api/envgroup': [
    { path: '/api/envgroup/page', method: 'POST' },
    { path: '/api/envgroup/create', method: 'POST' },
    { path: '/api/envgroup/edit', method: 'POST' },
    { path: '/api/envgroup/delete', method: 'POST' }
  ],
  '/api/envtag': [
    { path: '/api/envtag/all', method: 'GET' },
    { path: '/api/envtag/create', method: 'POST' },
    { path: '/api/envtag/edit', method: 'POST' },
    { path: '/api/envtag/delete', method: 'POST' }
  ],
  '/api/proxyInfo': [
    { path: '/api/proxyInfo/page', method: 'POST' },
    { path: '/api/proxyInfo/add', method: 'POST' },
    { path: '/api/proxyInfo/update', method: 'POST' },
    { path: '/api/proxyInfo/delete', method: 'POST' }
  ]
};

// Deprecated endpoints that should NOT exist
const DEPRECATED_ENDPOINTS = [
  '/api/env/delete' // Use removeToRecycleBin/batch instead
];

function log(message, color = 'reset') {
  console.log(`${colors[color]}${message}${colors.reset}`);
}

function checkOpenAPIYaml() {
  log('\n📋 Checking openapi.yaml...', 'blue');
  
  const openapiPath = path.join(docsDir, 'openapi.yaml');
  if (!fs.existsSync(openapiPath)) {
    errors.push('openapi.yaml not found');
    return;
  }
  
  const content = fs.readFileSync(openapiPath, 'utf8');
  const spec = yaml.load(content);
  
  if (!spec.paths) {
    errors.push('openapi.yaml has no paths section');
    return;
  }
  
  // Extract compat endpoints
  const compatEndpoints = [];
  const allPaths = Object.keys(spec.paths);
  
  allPaths.forEach(path => {
    if (path.startsWith('/api/env') || path.startsWith('/api/envgroup') || 
        path.startsWith('/api/envtag') || path.startsWith('/api/proxyInfo')) {
      const methods = Object.keys(spec.paths[path]);
      methods.forEach(method => {
        if (method !== 'parameters' && method !== 'servers') {
          compatEndpoints.push({ path, method: method.toUpperCase() });
        }
      });
    }
  });
  
  log(`  Found ${compatEndpoints.length} compat endpoints`, 'green');
  
  // Check count
  if (compatEndpoints.length !== 30) {
    errors.push(`Expected 30 compat endpoints, found ${compatEndpoints.length}`);
  }
  
  // Check each expected endpoint exists
  const allExpected = Object.values(EXPECTED_ENDPOINTS).flat();
  allExpected.forEach(expected => {
    const found = compatEndpoints.find(e => 
      e.path === expected.path && e.method === expected.method
    );
    
    if (!found) {
      errors.push(`Missing endpoint: ${expected.method} ${expected.path}`);
    }
  });
  
  // Check for deprecated endpoints
  DEPRECATED_ENDPOINTS.forEach(deprecated => {
    const found = compatEndpoints.find(e => e.path === deprecated);
    if (found) {
      errors.push(`Deprecated endpoint found: ${found.method} ${deprecated} (should use /api/env/removeToRecycleBin/batch)`);
    }
  });
  
  // Check for unexpected endpoints
  compatEndpoints.forEach(endpoint => {
    const isExpected = allExpected.some(e => 
      e.path === endpoint.path && e.method === endpoint.method
    );
    
    if (!isExpected) {
      warnings.push(`Unexpected endpoint: ${endpoint.method} ${endpoint.path}`);
    }
  });
}

function checkBaseline() {
  log('\n📘 Checking 13-baseline-morelogin-public.md...', 'blue');
  
  const baselinePath = path.join(docsDir, '13-baseline-morelogin-public.md');
  if (!fs.existsSync(baselinePath)) {
    errors.push('13-baseline-morelogin-public.md not found');
    return;
  }
  
  const content = fs.readFileSync(baselinePath, 'utf8');
  
  // Check for deprecated endpoint name
  if (content.includes('/api/env/delete') && !content.includes('removeToRecycleBin/batch')) {
    errors.push('Baseline still uses deprecated /api/env/delete endpoint');
  }
  
  // Check for correct endpoint name
  if (!content.includes('/api/env/removeToRecycleBin/batch')) {
    errors.push('Baseline missing correct endpoint: /api/env/removeToRecycleBin/batch');
  }
  
  // Check methods for key endpoints
  const keyEndpoints = [
    { path: '/api/env/detail', method: 'POST' },
    { path: '/api/env/getAllDebugInfo', method: 'POST' },
    { path: '/api/env/getAllProcessIds', method: 'POST' },
    { path: '/api/env/getAllScreen', method: 'POST' }
  ];
  
  keyEndpoints.forEach(endpoint => {
    const pathRegex = new RegExp(`\\|\s*\`(GET|POST)\`\\s*\\|\\s*\`${endpoint.path.replace(/\//g, '\\/')}\``, 'g');
    const matches = content.match(pathRegex);
    
    if (matches) {
      matches.forEach(match => {
        const methodMatch = match.match(/`(GET|POST)`/);
        if (methodMatch && methodMatch[1] !== endpoint.method) {
          errors.push(`${endpoint.path} has wrong method in baseline: ${methodMatch[1]} (should be ${endpoint.method})`);
        }
      });
    }
  });
  
  log('  Baseline checks complete', 'green');
}

function checkLocalAPI() {
  log('\n📗 Checking 04-local-api.md...', 'blue');
  
  const localAPIPath = path.join(docsDir, '04-local-api.md');
  if (!fs.existsSync(localAPIPath)) {
    errors.push('04-local-api.md not found');
    return;
  }
  
  const content = fs.readFileSync(localAPIPath, 'utf8');
  
  // Check that /api/env/detail is listed as POST (compat side)
  const detailRegex = /\|\s*`(GET|POST)`\s*\|\s*`\/api\/env\/detail`/g;
  const matches = content.match(detailRegex);
  
  if (matches) {
    matches.forEach(match => {
      const methodMatch = match.match(/`(GET|POST)`/);
      if (methodMatch && methodMatch[1] === 'GET') {
        errors.push('/api/env/detail should be POST in 04-local-api.md compat mapping table');
      }
    });
  }
  
  // Check for deprecated endpoint
  if (content.includes('POST /api/env/delete') && !content.includes('removeToRecycleBin/batch')) {
    errors.push('04-local-api.md still references deprecated /api/env/delete');
  }

  // Check that all 30 expected compat endpoints are listed in the §4A tables
  const section4AStart = content.indexOf('## 4A. MoreLogin-Compat Endpoints');
  if (section4AStart === -1) {
    errors.push('04-local-api.md missing §4A MoreLogin-Compat Endpoints section');
  } else {
    // Find section 4A content (up to the next ## section or end of file)
    const nextSectionIdx = content.indexOf('\n## ', section4AStart + 1);
    const section4AContent = nextSectionIdx === -1
      ? content.substring(section4AStart)
      : content.substring(section4AStart, nextSectionIdx);

    // Extract endpoints from §4A table rows: | `METHOD` | `/api/path` |
    const tableRowRegex = /\|\s*`(GET|POST)`\s*\|\s*`(\/api\/[^`]+)`/g;
    const listed4AEndpoints = [];
    let m;
    while ((m = tableRowRegex.exec(section4AContent)) !== null) {
      listed4AEndpoints.push({ method: m[1], path: m[2].trim() });
    }

    const allExpected = Object.values(EXPECTED_ENDPOINTS).flat();
    allExpected.forEach(expected => {
      const found = listed4AEndpoints.some(e =>
        e.path === expected.path && e.method === expected.method
      );
      if (!found) {
        errors.push(`04-local-api.md §4A table missing endpoint: ${expected.method} ${expected.path}`);
      }
    });
  }

  log('  Local API checks complete', 'green');
}

function checkParityMatrix() {
  log('\n📊 Checking 14-parity-matrix.md...', 'blue');
  
  const parityPath = path.join(docsDir, '14-parity-matrix.md');
  if (!fs.existsSync(parityPath)) {
    errors.push('14-parity-matrix.md not found');
    return;
  }
  
  const content = fs.readFileSync(parityPath, 'utf8');
  
  // Check for deprecated endpoint
  if (content.includes('POST /api/env/delete') && !content.includes('removeToRecycleBin/batch')) {
    errors.push('14-parity-matrix.md still references deprecated /api/env/delete');
  }
  
  // Check for correct endpoint
  if (!content.includes('/api/env/removeToRecycleBin/batch')) {
    errors.push('14-parity-matrix.md missing correct endpoint: /api/env/removeToRecycleBin/batch');
  }

  // Verify G2 summary counts match actual table counts
  checkG2SummaryCounts(content);

  // Verify G4 summary counts match actual table counts
  checkG4SummaryCounts(content);
  
  log('  Parity matrix checks complete', 'green');
}

/**
 * Count ✅ Full and 🚫 N/A rows in a named API group section.
 * Returns { full, na } counts parsed from the markdown table rows.
 */
function countAPITableRows(content, groupHeaderPattern) {
  const lines = content.split('\n');
  const headerIdx = lines.findIndex(l => groupHeaderPattern.test(l));
  if (headerIdx === -1) return null;

  let full = 0, na = 0;
  let inTable = false;
  for (let i = headerIdx + 1; i < lines.length; i++) {
    const line = lines[i].trim();
    // Detect table rows (start with |)
    if (line.startsWith('|')) {
      // Skip separator rows and the column header row (which starts with | MoreLogin Endpoint |)
      if (line.includes('---') || /^\|\s*MoreLogin\s+Endpoint\s*\|/i.test(line)) continue;
      inTable = true;
      if (line.includes('✅ Full')) full++;
      else if (line.includes('🚫 N/A')) na++;
    } else if (inTable && line.startsWith('**G2 Score')) {
      // We've reached the score summary line — stop
      break;
    } else if (inTable && !line.startsWith('|') && line !== '') {
      // End of table block
      break;
    }
  }
  return { full, na };
}

function checkG2SummaryCounts(content) {
  // Parse the G2 summary table to get the "Tổng" row
  const summaryMatch = content.match(/\|\s*\*\*Tổng\*\*\s*\|\s*\*\*(\d+)\*\*\s*\|\s*\*\*(\d+)\*\*\s*\|\s*\*\*(\d+)\*\*\s*\|\s*\*\*(\d+)\*\*\s*\|\s*\*\*(\d+)\*\*\s*\|/);
  if (!summaryMatch) {
    warnings.push('14-parity-matrix.md: Could not parse G2 Tổng summary row');
    return;
  }
  const summaryTotal = parseInt(summaryMatch[1]);
  const summaryFull  = parseInt(summaryMatch[2]);
  const summaryNA    = parseInt(summaryMatch[5]);

  // Count actual Full and N/A rows in the /api/env/* table
  const envCounts     = countAPITableRows(content, /Group A.*\/api\/env\//);
  const groupCounts   = countAPITableRows(content, /Group B.*\/api\/envgroup\//);
  const tagCounts     = countAPITableRows(content, /Group C.*\/api\/envtag\//);
  const proxyCounts   = countAPITableRows(content, /Group D.*\/api\/proxyInfo\//);
  const syncCounts    = countAPITableRows(content, /Group E.*\/api\/sync\//);
  if (!envCounts || !groupCounts || !tagCounts || !proxyCounts || !syncCounts) {
    warnings.push('14-parity-matrix.md: Could not locate all G2 API tables for count verification');
    return;
  }

  const totalFull = envCounts.full + groupCounts.full + tagCounts.full + proxyCounts.full + syncCounts.full;
  const totalNA   = envCounts.na   + groupCounts.na   + tagCounts.na   + proxyCounts.na   + syncCounts.na;
  const totalEndpoints = totalFull + totalNA;

  if (summaryTotal !== totalEndpoints) {
    errors.push(`14-parity-matrix.md G2 Tổng total: summary says ${summaryTotal} but table has ${totalEndpoints}`);
  }
  if (summaryFull !== totalFull) {
    errors.push(`14-parity-matrix.md G2 Tổng Full: summary says ${summaryFull} but table has ${totalFull}`);
  }
  if (summaryNA !== totalNA) {
    errors.push(`14-parity-matrix.md G2 Tổng N/A: summary says ${summaryNA} but table has ${totalNA}`);
  }
}

/**
 * Count ✅ Full and ⚠️ Partial rows in a data-model section.
 */
function countDataModelRows(content, sectionPattern) {
  const lines = content.split('\n');
  const headerIdx = lines.findIndex(l => sectionPattern.test(l));
  if (headerIdx === -1) return null;

  let full = 0, partial = 0;
  let inTable = false;
  for (let i = headerIdx + 1; i < lines.length; i++) {
    const line = lines[i].trim();
    if (line.startsWith('|')) {
      if (line.includes('---') || /^\|\s*MoreLogin\s+Field\s*\|/i.test(line)) continue;
      inTable = true;
      if (line.includes('✅ Full')) full++;
      else if (line.includes('⚠️ Partial')) partial++;
    } else if (inTable && line.startsWith('**D4 Score')) {
      break;
    } else if (inTable && !line.startsWith('|') && line !== '') {
      break;
    }
  }
  return { full, partial };
}

function checkG4SummaryCounts(content) {
  // Find the G4 Data Model Score section first
  const g4SectionStart = content.indexOf('### 📊 G4 Data Model Score Tổng hợp');
  if (g4SectionStart === -1) {
    warnings.push('14-parity-matrix.md: Could not find G4 Data Model Score section');
    return;
  }
  
  // Work with just the G4 section (up to next major section)
  const g4Section = content.substring(g4SectionStart, content.indexOf('\n## ', g4SectionStart + 1));
  
  // Parse the G4 summary table rows
  const profileMatch = g4Section.match(/\|\s*Profile\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|/);
  const groupMatch   = g4Section.match(/\|\s*Group\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|/);
  const tagMatch     = g4Section.match(/\|\s*Tag\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|/);
  const proxyMatch   = g4Section.match(/\|\s*ProxyInfo\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|/);
  // Match Tổng row with flexible pattern
  const totalMatch   = g4Section.match(/\|\s*\*\*Tổng\*\*\s*\|\s*\*\*(\d+)\*\*\s*\|\s*\*\*(\d+)\*\*\s*\|\s*\*\*(\d+)\*\*\s*\|\s*\*\*(\d+)\*\*\s*\|/);

  if (!profileMatch || !groupMatch || !tagMatch || !proxyMatch || !totalMatch) {
    warnings.push('14-parity-matrix.md: Could not parse G4 summary table rows');
    return;
  }

  const summaryFull    = parseInt(totalMatch[2]);
  const summaryPartial = parseInt(totalMatch[3]);

  // Count actual rows from tables
  const profileCounts = countDataModelRows(content, /3\.1 Profile.*Object Fields/);
  const groupCounts   = countDataModelRows(content, /3\.2 Group Entity/);
  const tagCounts     = countDataModelRows(content, /3\.3 Tag Entity/);
  const proxyCounts   = countDataModelRows(content, /3\.4 ProxyInfo Object/);

  if (!profileCounts || !groupCounts || !tagCounts || !proxyCounts) {
    warnings.push('14-parity-matrix.md: Could not locate all G4 data model tables for count verification');
    return;
  }

  // Verify each entity row in summary matches its table
  const entities = [
    { name: 'Profile', match: profileMatch, counts: profileCounts },
    { name: 'Group',   match: groupMatch,   counts: groupCounts },
    { name: 'Tag',     match: tagMatch,     counts: tagCounts },
    { name: 'ProxyInfo', match: proxyMatch, counts: proxyCounts }
  ];

  let totalFull = 0, totalPartial = 0;
  entities.forEach(({ name, match, counts }) => {
    const rowFull    = parseInt(match[2]);
    const rowPartial = parseInt(match[3]);
    if (rowFull !== counts.full) {
      errors.push(`14-parity-matrix.md G4 ${name} Full: summary row says ${rowFull} but table has ${counts.full}`);
    }
    if (rowPartial !== counts.partial) {
      errors.push(`14-parity-matrix.md G4 ${name} Partial: summary row says ${rowPartial} but table has ${counts.partial}`);
    }
    totalFull    += counts.full;
    totalPartial += counts.partial;
  });

  if (summaryFull !== totalFull) {
    errors.push(`14-parity-matrix.md G4 Tổng Full: summary says ${summaryFull} but tables total ${totalFull}`);
  }
  if (summaryPartial !== totalPartial) {
    errors.push(`14-parity-matrix.md G4 Tổng Partial: summary says ${summaryPartial} but tables total ${totalPartial}`);
  }
}

function checkConfigKeysConsistency() {
  log('\n🔑 Checking config keys consistency...', 'blue');
  
  // Files that should NOT contain deprecated config keys
  const filesToCheck = [
    'openapi.yaml',
    '01-kien-truc-he-thong.md',
    '04-local-api.md',
    '10-qa-release-checklist.md',
    '12-api-compatibility.md',
    '13-baseline-morelogin-public.md',
    '14-parity-matrix.md'
  ];
  
  const deprecatedConfigKeys = [
    'compat.morelogin_envelope',
    'compat.morelogin_mode',
    'compat.morelogin_endpoints',
    'settings.compat_morelogin_mode'
  ];
  
  filesToCheck.forEach(filename => {
    const filePath = path.join(docsDir, filename);
    if (!fs.existsSync(filePath)) {
      warnings.push(`File not found for config key check: ${filename}`);
      return;
    }
    
    const content = fs.readFileSync(filePath, 'utf8');
    
    deprecatedConfigKeys.forEach(deprecatedKey => {
      // Escape special regex characters properly for safe regex construction
      const escapedKey = deprecatedKey.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
      const regex = new RegExp(escapedKey, 'g');
      
      if (regex.test(content)) {
        errors.push(`File ${filename} contains deprecated config key: ${deprecatedKey} (use canonical keys from 15-config-keys-reference.md)`);
      }
    });
  });
  
  log('  Config keys consistency checks complete', 'green');
}

function checkDeprecatedEndpointsAllDocs() {
  log('\n🚫 Checking deprecated endpoints across all docs...', 'blue');

  const docFiles = [
    '01-kien-truc-he-thong.md',
    '04-local-api.md',
    '10-qa-release-checklist.md',
    '12-api-compatibility.md',
    '13-baseline-morelogin-public.md',
    '14-parity-matrix.md'
  ];

  const forbiddenPatterns = [
    { substr: '/api/env/delete/permanent', label: '/api/env/delete/permanent' },
    { substr: '/api/env/delete', label: '/api/env/delete' }
  ];

  docFiles.forEach(filename => {
    const filePath = path.join(docsDir, filename);
    if (!fs.existsSync(filePath)) {
      warnings.push(`File not found for deprecated endpoint check: ${filename}`);
      return;
    }

    const content = fs.readFileSync(filePath, 'utf8');

    forbiddenPatterns.forEach(({ substr, label }) => {
      if (content.includes(substr)) {
        errors.push(`File ${filename} references forbidden endpoint: ${label} (use /api/env/removeToRecycleBin/batch)`);
      }
    });
  });

  log('  Deprecated endpoint checks across all docs complete', 'green');
}

function checkQAChecklist() {
  log('\n✅ Checking QA release checklist...', 'blue');

  const checklistPath = path.join(docsDir, '10-qa-release-checklist.md');
  if (!fs.existsSync(checklistPath)) {
    errors.push('10-qa-release-checklist.md not found');
    return;
  }

  const content = fs.readFileSync(checklistPath, 'utf8');

  // Endpoints that must use POST (not GET) in the checklist
  const mustBePost = [
    '/api/env/getAllDebugInfo',
    '/api/env/getAllProcessIds',
    '/api/env/getAllScreen',
    '/api/env/detail'
  ];

  mustBePost.forEach(endpoint => {
    const escapedEndpoint = endpoint.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    const getRegex = new RegExp(`GET\\s+${escapedEndpoint}`, 'g');
    if (getRegex.test(content)) {
      errors.push(`10-qa-release-checklist.md uses GET for ${endpoint} (should be POST)`);
    }
  });

  log('  QA checklist checks complete', 'green');
}

function checkOverviewG2Numbers() {
  log('\n📝 Checking 00-tong-quan-du-an.md G2 numbers match 14-parity-matrix.md...', 'blue');
  
  const overviewPath = path.join(docsDir, '00-tong-quan-du-an.md');
  const parityPath = path.join(docsDir, '14-parity-matrix.md');
  
  if (!fs.existsSync(overviewPath)) {
    errors.push('00-tong-quan-du-an.md not found');
    return;
  }
  
  if (!fs.existsSync(parityPath)) {
    errors.push('14-parity-matrix.md not found');
    return;
  }
  
  const overviewContent = fs.readFileSync(overviewPath, 'utf8');
  const parityContent = fs.readFileSync(parityPath, 'utf8');
  
  // Extract G2 numbers from 14-parity-matrix.md (Tổng row)
  const parityMatch = parityContent.match(/\|\s*\*\*Tổng\*\*\s*\|\s*\*\*(\d+)\*\*\s*\|\s*\*\*(\d+)\*\*\s*\|\s*\*\*(\d+)\*\*\s*\|\s*\*\*(\d+)\*\*\s*\|\s*\*\*(\d+)\*\*\s*\|/);
  
  if (!parityMatch) {
    warnings.push('Could not parse G2 Tổng row from 14-parity-matrix.md');
    return;
  }
  
  const parityTotal = parseInt(parityMatch[1]);
  const parityFull = parseInt(parityMatch[2]);
  const parityNA = parseInt(parityMatch[5]);
  
  // Extract G2 numbers from 00-tong-quan-du-an.md
  // Pattern: "G2: ✅ Pass (~97% — 29/30 Full; 1 N/A cloud-only; 0 Missing)"
  const overviewMatch = overviewContent.match(/G2:\s*✅\s*Pass\s*\([^—]*—\s*(\d+)\/(\d+)\s+Full;\s*(\d+)\s+N\/A/);
  
  if (!overviewMatch) {
    errors.push('Could not parse G2 status line from 00-tong-quan-du-an.md');
    return;
  }
  
  const overviewFull = parseInt(overviewMatch[1]);
  const overviewTotal = parseInt(overviewMatch[2]);
  const overviewNA = parseInt(overviewMatch[3]);
  
  // Compare
  if (overviewTotal !== parityTotal) {
    errors.push(`00-tong-quan-du-an.md G2 total (${overviewTotal}) doesn't match 14-parity-matrix.md (${parityTotal})`);
  }
  
  if (overviewFull !== parityFull) {
    errors.push(`00-tong-quan-du-an.md G2 Full count (${overviewFull}) doesn't match 14-parity-matrix.md (${parityFull})`);
  }
  
  if (overviewNA !== parityNA) {
    errors.push(`00-tong-quan-du-an.md G2 N/A count (${overviewNA}) doesn't match 14-parity-matrix.md (${parityNA})`);
  }
  
  log('  Overview G2 numbers check complete', 'green');
}

function checkErrorCodeSystem() {
  log('\n🔢 Checking error code system consistency (must use negative codes)...', 'blue');

  // Files that must NOT use the old HTTP-mapped positive error codes in JSON `"code"` fields
  const filesToCheck = [
    '04-local-api.md',
    '09-bao-mat-va-luu-tru.md'
  ];

  // Pattern: "code": <positive integer> that could be an HTTP-mapped code (any positive non-zero integer)
  // We match any positive integer ≥ 100 (HTTP-mapped codes are 40001, 50100 etc; success is 0)
  const positiveCodePattern = /"code":\s*([1-9]\d{2,})/g;

  filesToCheck.forEach(filename => {
    const filePath = path.join(docsDir, filename);
    if (!fs.existsSync(filePath)) {
      warnings.push(`File not found for error code check: ${filename}`);
      return;
    }

    const content = fs.readFileSync(filePath, 'utf8');
    const matches = [...content.matchAll(positiveCodePattern)];
    if (matches.length > 0) {
      matches.forEach(m => {
        errors.push(`${filename} uses HTTP-mapped positive error code ${m[1]} — must use negative codes per error-catalog.md SSOT (e.g. -1601 instead of 40001)`);
      });
    }
  });

  log('  Error code system checks complete', 'green');
}

function checkRateLimitConsistency() {
  log('\n⏱️  Checking rate limit consistency (must be 100 req/s)...', 'blue');

  const CANONICAL_RATE_LIMIT = 100;

  // Files and patterns to check for stale "50 req/s" references
  const filesToCheck = [
    { file: 'threat-model.md',  pattern: /\|\s*Global requests\/second\s*\|\s*(\d+)\s*\|/ },
    { file: 'threat-model.md',  pattern: /Rate limit: (\d+) req\/s/ },
    { file: 'error-catalog.md', pattern: /rate limit \((\d+) req\/s default\)/ },
    { file: '04-local-api.md',  pattern: /Max (\d+) requests\/giây/ },
    { file: '09-bao-mat-va-luu-tru.md', pattern: /(\d+) req\/s/ }
  ];

  filesToCheck.forEach(({ file, pattern }) => {
    const filePath = path.join(docsDir, file);
    if (!fs.existsSync(filePath)) {
      warnings.push(`File not found for rate limit check: ${file}`);
      return;
    }

    const content = fs.readFileSync(filePath, 'utf8');
    let m;
    // Use RegExp with 'g' flag for all occurrences
    const re = new RegExp(pattern.source, 'g');
    while ((m = re.exec(content)) !== null) {
      const found = parseInt(m[1]);
      if (!isNaN(found) && found !== CANONICAL_RATE_LIMIT) {
        errors.push(`${file} has rate limit value ${found} req/s — must be ${CANONICAL_RATE_LIMIT} req/s (canonical default)`);
      }
    }
  });

  log('  Rate limit consistency checks complete', 'green');
}

function checkDefaultPortConsistency() {
  log('\n🔌 Checking default port consistency (must be 40000)...', 'blue');

  const CANONICAL_PORT = '40000';

  // Files that define CLI default or diagram default — check for 19000 as a default
  const checks = [
    {
      file: '05-cli-spec.md',
      // The default agent_url in config file and global flag
      pattern: /"agent_url":\s*"http:\/\/127\.0\.0\.1:(\d+)"/g,
      label: 'CLI config default agent_url'
    },
    {
      file: '05-cli-spec.md',
      pattern: /default: http:\/\/127\.0\.0\.1:(\d+)/g,
      label: 'CLI --agent-url flag default'
    },
    {
      file: '09-bao-mat-va-luu-tru.md',
      // The Mermaid diagram participant
      pattern: /Local API\\n\(127\.0\.0\.1:(\d+)\)/g,
      label: '09-bao-mat-va-luu-tru.md diagram default port'
    }
  ];

  checks.forEach(({ file, pattern, label }) => {
    const filePath = path.join(docsDir, file);
    if (!fs.existsSync(filePath)) {
      warnings.push(`File not found for default port check: ${file}`);
      return;
    }

    const content = fs.readFileSync(filePath, 'utf8');
    let m;
    while ((m = pattern.exec(content)) !== null) {
      if (m[1] !== CANONICAL_PORT) {
        errors.push(`${label} in ${file} uses port ${m[1]} — default must be ${CANONICAL_PORT} (use 19000 only as alt override example)`);
      }
    }
  });

  log('  Default port consistency checks complete', 'green');
}

function checkTokenStorageConsistency() {
  log('\n🔑 Checking token storage consistency (agent must use SHA-256 hash)...', 'blue');

  // threat-model.md must NOT say api.token key (old DPAPI approach) for agent storage
  const threatModelPath = path.join(docsDir, 'threat-model.md');
  if (fs.existsSync(threatModelPath)) {
    const content = fs.readFileSync(threatModelPath, 'utf8');

    // The old pattern: key `api.token`, value encrypted với DPAPI
    if (/key `api\.token`, value encrypted/i.test(content)) {
      errors.push('threat-model.md still describes agent token storage as DPAPI-encrypted (key api.token) — must use SHA-256 hash (key api_token_hash) per 04-local-api.md and 09-bao-mat-va-luu-tru.md');
    }

    // Must have SHA-256 hash mention for agent token
    if (!/api_token_hash/.test(content)) {
      errors.push('threat-model.md missing api_token_hash key — agent token must be stored as SHA-256 hash');
    }
  } else {
    warnings.push('threat-model.md not found for token storage check');
  }

  log('  Token storage consistency checks complete', 'green');
}

function printResults() {
  log('\n' + '='.repeat(70), 'bold');
  log('Documentation Consistency Check Results', 'bold');
  log('='.repeat(70), 'bold');
  
  if (errors.length === 0 && warnings.length === 0) {
    log('\n✅ All checks passed! Documentation is consistent.', 'green');
    return 0;
  }
  
  if (errors.length > 0) {
    log(`\n❌ Found ${errors.length} error(s):`, 'red');
    errors.forEach((err, i) => {
      log(`  ${i + 1}. ${err}`, 'red');
    });
  }
  
  if (warnings.length > 0) {
    log(`\n⚠️  Found ${warnings.length} warning(s):`, 'yellow');
    warnings.forEach((warn, i) => {
      log(`  ${i + 1}. ${warn}`, 'yellow');
    });
  }
  
  log('\n' + '='.repeat(70), 'bold');
  
  return errors.length > 0 ? 1 : 0;
}

// Main execution
log('\n🔍 Starting Documentation Consistency Check...', 'bold');
log(`📂 Documentation directory: ${docsDir}`, 'blue');

try {
  checkOpenAPIYaml();
  checkBaseline();
  checkLocalAPI();
  checkParityMatrix();
  checkConfigKeysConsistency();
  checkDeprecatedEndpointsAllDocs();
  checkQAChecklist();
  checkOverviewG2Numbers();
  checkErrorCodeSystem();
  checkRateLimitConsistency();
  checkDefaultPortConsistency();
  checkTokenStorageConsistency();
  
  const exitCode = printResults();
  process.exit(exitCode);
  
} catch (error) {
  log(`\n💥 Fatal error: ${error.message}`, 'red');
  console.error(error);
  process.exit(2);
}
