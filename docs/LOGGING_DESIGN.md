# Logging & Debugging Design

## Overview

Add structured logging to trace the query flow through the framework.

---

## Proposed Log Points

```
[ROUTER] Received query → routing to "network"
[COORDINATOR:network] Classifying query → selected "issues"
[SUBAGENT:issues] Retrieving from RAG (k=5)
[SUBAGENT:issues] Retrieved 3 documents
[SUBAGENT:issues] Generating response
[SUBAGENT:issues] Detected referral → "api_ref"
[COORDINATOR:network] Handling referral → "api_ref"
[SUBAGENT:api_ref] Retrieving from RAG (k=5)
...
```

---

## Implementation Design

### 1. Create Logger Module

**New file: `src/mit/logging.py`**

```python
import logging
import sys

def get_logger(name: str) -> logging.Logger:
    """Get a logger with consistent formatting."""
    logger = logging.getLogger(f"mit.{name}")
    return logger

def setup_logging(level: str = "INFO"):
    """Configure logging for the framework."""
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
        datefmt="%H:%M:%S",
        stream=sys.stdout,
    )
```

### 2. Add Loggers to Components

| Component | Logger Name | Key Log Points |
|-----------|-------------|----------------|
| Router | `mit.router` | Query received, module selected |
| Coordinator | `mit.coordinator.{name}` | Classification, routing, referral |
| SubAgent | `mit.agent.{name}` | Retrieve, generate, response |
| RAG | `mit.rag` | Search queries, results count |

### 3. Log Levels

| Level | Usage |
|-------|-------|
| `DEBUG` | Detailed internal state (documents, prompts) |
| `INFO` | Flow tracking (which agent, which action) |
| `WARNING` | Referral cycles, missing collections |
| `ERROR` | Failures (API errors, missing config) |

---

## Files to Modify

| File | Changes |
|------|---------|
| `src/mit/logging.py` | **NEW** - Logger setup |
| `src/mit/config.py` | Add `log_level` setting |
| `src/mit/core/router.py` | Replace prints with logger |
| `src/mit/core/coordinator.py` | Add classification/routing logs |
| `src/mit/core/base_agent.py` | Add retrieve/generate logs |
| `src/mit/rag/vectorstore.py` | Add search logs |
| `src/mit/main.py` | Call `setup_logging()` on start |
| `scripts/ingest.py` | Replace prints with logger |

---

## Environment Variable

Add to `.env`:
```
MIT_LOG_LEVEL=INFO   # DEBUG, INFO, WARNING, ERROR
```

---

## Example Output

**INFO level:**
```
03:50:01 [mit.router] INFO: Query received, routing to "network"
03:50:01 [mit.coordinator.network] INFO: Classified → "issues"
03:50:02 [mit.agent.issues] INFO: Retrieved 3 documents
03:50:03 [mit.agent.issues] INFO: Response generated
```

**DEBUG level:**
```
03:50:01 [mit.router] DEBUG: Query: "How to fix 504 error?"
03:50:01 [mit.coordinator.network] DEBUG: Classification prompt sent
03:50:02 [mit.agent.issues] DEBUG: RAG query: "504 error fix"
03:50:02 [mit.agent.issues] DEBUG: Documents: [errors.md:L45, errors.md:L102]
```

---

## Summary

- Replace all `print()` with structured logging
- Enable `DEBUG` level for agent development
- Use `INFO` level for production monitoring
- Easy to enable/disable via environment variable

**Approve to proceed with implementation?**
