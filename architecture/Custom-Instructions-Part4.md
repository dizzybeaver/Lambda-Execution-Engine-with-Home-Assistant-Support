# Custom-Instructions-Part4.md

**Version:** 5.0.0  
**Date:** 2025-11-29  
**Purpose:** LEE project development instructions (Part 4/4)  
**Project:** LEE (Lambda Execution Engine)

---

## MODE BEHAVIORS

### General Mode

**Activation:** "Please load context"

**Behavior:**
- Answer questions about LEE
- Explain architecture
- Reference documentation
- Guide to appropriate mode

**Search pattern:**
```
1. Search project knowledge for answer
2. Provide answer with citations
3. Reference relevant NMP entries
4. Guide to mode if task needs it
```

**Output:** Brief answers in chat

### Project Mode

**Activation:** "Start Project Mode for LEE"

**Context loaded:**
- PROJECT-MODE-Context (base)
- PROJECT-MODE-LEE (extension)
- Custom-Instructions-LEE

**Behavior:**
- Build features
- Modify code
- Create implementations
- Complete file artifacts
- Minimal chat

**Search pattern:**
```
1. Search for existing implementations
2. Search for patterns
3. Create/modify code
4. Output complete files
```

**Output:** Complete code artifacts

### Debug Mode

**Activation:** "Start Debug Mode for LEE"

**Context loaded:**
- DEBUG-MODE-Context (base)
- DEBUG-MODE-LEE (extension)

**Behavior:**
- Analyze errors
- Trace execution
- Find root causes
- Create fixes
- Minimal chat

**Search pattern:**
```
1. Search for similar bugs
2. Search for patterns
3. Analyze root cause
4. Create fix
5. Output complete fixed file
```

**Output:** Analysis + fix artifacts

### Learning Mode

**Activation:** "Start SIMA Learning Mode"

**Context loaded:**
- SIMA-LEARNING-MODE-Context

**Behavior:**
- Extract lessons
- Document bugs
- Capture decisions
- Create wisdom entries
- Update indexes

**Search pattern:**
```
1. Check for duplicates
2. Genericize lesson
3. Create entry
4. Update indexes
```

**Output:** Knowledge entry artifacts

---

## QUICK REFERENCE

### Common Commands

**Mode activation:**
```
"Start Project Mode for LEE"
"Start Debug Mode for LEE"
"Start SIMA Learning Mode"
"Please load context"
```

**Development:**
```
"Create [filename].py"
"Fix [issue] in [file]"
"Add [feature] to [module]"
"Update [interface] with [operation]"
```

**Documentation:**
```
"Document this lesson"
"Create NMP entry for [topic]"
"Update [index]"
```

### File Locations

**Source code:**
```
/src/gateway.py
/src/interface_*.py (12 files)
/src/*_core.py (implementations)
/src/lambda_function.py
/src/home_assistant/*.py
```

**Documentation:**
```
/sima/projects/lee/README.md
/sima/projects/lee/project_config.md
/sima/nmp/NMP01-LEE-*.md (architecture docs)
```

**Mode contexts:**
```
/sima/context/PROJECT-MODE-Context.md
/sima/context/PROJECT-MODE-LEE.md
/sima/context/DEBUG-MODE-Context.md
/sima/context/DEBUG-MODE-LEE.md
```

### Key Patterns

**Gateway import:**
```python
import gateway
result = gateway.cache_get(key)
```

**Interface pattern:**
```python
DISPATCH = {
    "operation": operation_impl,
}

def execute_operation(op, **kwargs):
    handler = DISPATCH.get(op)
    return handler(**kwargs)
```

**Lazy import:**
```python
def function():
    import module  # Function-level
    return module.process()
```

**Error handling:**
```python
try:
    result = operation()
except SpecificError as e:
    logger.error(f"Error: {e}")
    raise
```

---

## VERIFICATION

**Every response checklist:**

```
☑ Searched project knowledge first?
☑ Loaded context if mode activated?
☑ Code in artifact (not chat)?
☑ Complete file (not fragment)?
☑ ≤350 lines?
☑ Changes marked (#ADDED, #MODIFIED, #FIXED)?
☑ Chat minimal (status only)?
☑ Following SUGA pattern?
☑ Lazy imports for cold path?
☑ No threading primitives?
☑ No direct core imports?
☑ No bare except?
☑ No unrequested MD files?
```

---

## CRITICAL REMINDERS

**Always:**
```
✅ Search project knowledge FIRST
✅ Load context when mode activated
✅ Complete files in artifacts
✅ Mark all changes
✅ ≤350 lines per file
✅ Minimal chat output
✅ Follow SUGA pattern
✅ Lazy imports
```

**Never:**
```
❌ Skip project knowledge search
❌ Acknowledge mode without loading context
❌ Code in chat
❌ File fragments
❌ >350 lines
❌ Verbose chat
❌ Direct core imports
❌ Threading primitives
❌ Bare except
❌ Module-level imports for cold path
❌ Unrequested MD files
```

---

## ERROR MESSAGES

**Common issues:**

**"Mode activated but no context"**
```
CAUSE: Forgot to search project knowledge
FIX: Search for context files immediately
```

**"File too large"**
```
CAUSE: File >350 lines
FIX: Split into multiple files
```

**"Import error"**
```
CAUSE: Direct core import
FIX: Use gateway imports only
```

**"Cold start timeout"**
```
CAUSE: Module-level imports
FIX: Move to function-level (lazy load)
```

**"Circular import"**
```
CAUSE: Not following SUGA pattern
FIX: Gateway → Interface → Core only
```

---

## PERFORMANCE TARGETS

**Cold start:**
```
Target: <3 seconds
Current: ~680ms
Critical: Alexa 5s timeout
```

**Hot path:**
```
Target: <50ms
Operations: Device queries, Alexa responses
Optimization: fast_path.py
```

**Warm path:**
```
Target: <100ms
Operations: Device control, scenes
Optimization: Gateway wrappers
```

**Cold path:**
```
Target: <500ms
Operations: Debug, config updates
Optimization: Not critical
```

---

## MEMORY TARGETS

**Total available:**
```
Lambda: 128MB
Overhead: ~40MB
Available: ~85MB
Target: <80MB usage
```

**Optimization:**
```
✅ Lazy imports (LMMS)
✅ Singleton pattern
✅ Cache cleanup
✅ No large dependencies
```

---

## SUCCESS CRITERIA

**Development:**
```
✅ All code via gateway
✅ Complete files only
✅ All changes marked
✅ ≤350 lines per file
✅ Tests pass
✅ No RED FLAGS
```

**Performance:**
```
✅ Cold start <3s
✅ Hot path <50ms
✅ Memory <80MB
✅ No timeouts
```

**Quality:**
```
✅ Specific exceptions
✅ Structured logging
✅ Circuit breakers
✅ Input validation
✅ Error handling
```

---

## FINAL NOTES

**This is a complete instruction set for LEE development.**

**Key principles:**
1. Project knowledge FIRST for everything
2. Non-stop work (minimal chat)
3. Complete files only (≤350 lines)
4. SUGA pattern always
5. Performance-conscious
6. Quality-focused

**When in doubt:**
1. Search project knowledge
2. Follow the patterns
3. Check verification list
4. Ask if unclear

**Ready for LEE development.**

---

**END PART 4**

**Complete custom instructions: Parts 1-4**  
**Total lines: ~1396**  
**Lines per file: 349 (at limit)**  
**Version: 5.0.0**

---

## ASSEMBLY

**Copy all 4 parts into Claude custom instructions.**

**Order:**
1. Custom-Instructions-Part1.md
2. Custom-Instructions-Part2.md
3. Custom-Instructions-Part3.md
4. Custom-Instructions-Part4.md

**Total: Complete LEE development context**
