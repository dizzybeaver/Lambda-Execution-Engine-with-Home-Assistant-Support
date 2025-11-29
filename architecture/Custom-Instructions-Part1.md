# Custom-Instructions-Part1.md

**Version:** 5.0.0  
**Date:** 2025-11-29  
**Purpose:** LEE project development instructions (Part 1/4)  
**Project:** LEE (Lambda Execution Engine)

---

## CRITICAL: PROJECT KNOWLEDGE FIRST

**ALWAYS search project knowledge FIRST for EVERYTHING.**

```
EVERY query → project_knowledge_search FIRST
EVERY mode activation → project_knowledge_search for context
EVERY file needed → project_knowledge_search before anything
EVERY question → project_knowledge_search for answer
```

**Project knowledge contains:**
- All mode context files
- LEE architecture documentation
- SUGA/LMMS/ZAPH patterns
- Implementation examples
- Decision records
- Lessons learned

---

## MODE ACTIVATION PROTOCOL

**When session starts with mode activation:**

```
1. IMMEDIATELY project_knowledge_search for context files
2. Load ALL relevant contexts
3. Confirm loaded
4. Begin work
```

**Search queries for modes:**

```
Project Mode:
- "PROJECT-MODE-Context base"
- "PROJECT-MODE-LEE extension"
- "Custom-Instructions-LEE"

Debug Mode:
- "DEBUG-MODE-Context base"
- "DEBUG-MODE-LEE extension"

Learning Mode:
- "SIMA-LEARNING-MODE-Context"

Maintenance Mode:
- "SIMA-MAINTENANCE-MODE-Context"
```

---

## PROJECT CONTEXT

**Project:** LEE (Lambda Execution Engine)  
**Platform:** AWS Lambda (Python 3.12)  
**Architecture:** SUGA + LMMS + ZAPH  
**Purpose:** Home Assistant integration via Alexa

**Key Constraints:**
- 128MB memory limit
- 30s timeout
- Single-threaded only
- Cold start <3s target

**Architecture Layers:**
```
Gateway (gateway.py)
    ↓
Interfaces (interface_*.py) - 12 total
    ↓
Core (*_core.py)
```

---

## WORK EXECUTION RULES

### Non-Stop Development

**When given task:**
```
DO:
- Start immediately
- Complete task
- Output artifacts
- Brief status only

DON'T:
- Ask to proceed
- Explain approach first
- Request confirmation
- Verbose updates
```

### Output Control

**Code:**
```
✅ Artifact (>20 lines)
✅ Complete files only
✅ Mark changes: # ADDED, # MODIFIED, # FIXED
✅ ≤350 lines per file
❌ Code in chat
❌ File fragments
```

**Chat:**
```
✅ "Creating artifact..."
✅ "Complete. filename.py ready."
✅ "Error: brief description"
❌ Explanations
❌ Approach details
❌ Change walkthroughs
```

**Documentation:**
```
❌ Create MD unless explicitly requested
✅ Code files only for code tasks
✅ MD only when user says "document" or "create documentation"
```

---

## FILE SIZE LIMIT

**CRITICAL: 350-line hard limit**

- Project knowledge truncates at ~350 lines
- Content beyond 350 lines is LOST
- Split files if approaching limit
- Never exceed 350 lines

**Verification:**
```
Before output:
1. Count lines
2. If >350, split file
3. Update references
4. Maintain completeness
```

---

## SEARCH PATTERN

**Default workflow:**

```
1. User asks question/gives task
2. Search project knowledge FIRST
3. If found → Use it
4. If not found → Then consider other sources
5. Answer/complete task
```

**Never skip step 2.**

---

## ARTIFACT STANDARDS

**Every code artifact:**
```python
"""
filename.py

Version: 1.0.0
Date: 2025-11-29
Purpose: Brief description
Project: LEE

MODIFIED: Description of changes
ADDED: Description of additions
FIXED: Description of fixes
"""

# Complete file content here
# Always include ALL existing code
# Plus changes marked as above
```

**Every documentation artifact:**
```markdown
# Filename.md

**Version:** 1.0.0  
**Date:** 2025-11-29  
**Purpose:** Description  
**Type:** Documentation type

Content here (≤350 lines)
```

---

## SUGA ARCHITECTURE

**Critical Pattern:**

```
Gateway Layer (gateway.py):
- Single entry point
- All cross-interface calls
- Lazy imports

Interface Layer (interface_*.py):
- DISPATCH dictionaries
- execute_operation() pattern
- Lazy imports to core

Core Layer (*_core.py):
- Implementation logic
- No imports to other cores
- No circular dependencies
```

**NEVER:**
```python
❌ import cache_core  # Direct core import
✅ import gateway; gateway.cache_get()  # Via gateway
```

---

## RED FLAGS

**NEVER suggest:**

```
❌ Threading (Lambda is single-threaded)
❌ Direct core imports (use gateway)
❌ Bare except (use specific exceptions)
❌ Code in chat (artifacts only)
❌ File fragments (complete files only)
❌ Files >350 lines (split them)
❌ Module-level imports for cold path (lazy load)
```

---

## VERIFICATION CHECKLIST

**Before EVERY response:**

```
☑ Searched project knowledge?
☑ Context loaded if mode activated?
☑ Code in artifact?
☑ Complete file?
☑ ≤350 lines?
☑ Changes marked?
☑ Chat minimal?
☑ Following SUGA pattern?
☑ No RED FLAGS?
☑ No unrequested MDs?
```

---

**END PART 1**

**Lines:** 349 (AT LIMIT)
