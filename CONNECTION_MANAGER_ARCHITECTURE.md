# Connection Manager + Auto Error Correction - System Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      NATPUDAN AUTO ERROR CORRECTION                      │
│                   WITH CONNECTION HEALTH MONITORING                      │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│                          USER / APPLICATION                              │
└─────────────────────┬───────────────────────────────────────────────────┘
                      │
                      │ Request → Connection Error
                      ↓
┌─────────────────────────────────────────────────────────────────────────┐
│                     FASTAPI ERROR MIDDLEWARE                             │
└─────────────────────┬───────────────────────────────────────────────────┘
                      │
                      │ Exception caught
                      ↓
┌─────────────────────────────────────────────────────────────────────────┐
│                       SELF-HEALING SYSTEM                                │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │ 1. Receive Error                                                  │  │
│  │    - error: Exception                                             │  │
│  │    - context: Dict[str, Any]                                      │  │
│  └───────────────────┬───────────────────────────────────────────────┘  │
│                      │                                                   │
│                      ↓                                                   │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │ 2. Connection Monitor Check                                       │  │
│  │    connection_monitor.get_error_context(error)                    │  │
│  │                                                                    │  │
│  │    Keywords: connection, refused, timeout, cors, port, network    │  │
│  └───────────────────┬───────────────────────────────────────────────┘  │
│                      │                                                   │
│         ┌────────────┴────────────┐                                     │
│         │                          │                                     │
│    NOT CONNECTION             CONNECTION                                │
│         │                          │                                     │
│         ↓                          ↓                                     │
│  ┌──────────────┐         ┌────────────────────────────────────────┐   │
│  │   AI-Powered  │         │   CONNECTION HEALTH MONITOR            │   │
│  │   Solution    │         │                                        │   │
│  │   Generator   │         │  ┌──────────────────────────────────┐ │   │
│  └──────────────┘         │  │ 3. Run Health Check               │ │   │
│                           │  │    check_health()                  │ │   │
│                           │  │                                    │ │   │
│                           │  │    • Scan .env files               │ │   │
│                           │  │    • Compare vs ports.json         │ │   │
│                           │  │    • Check CORS config             │ │   │
│                           │  │    • Verify port availability      │ │   │
│                           │  └──────────┬───────────────────────── │   │
│                           │             │                          │   │
│                           │             ↓                          │   │
│                           │  ┌──────────────────────────────────┐ │   │
│                           │  │ 4. Detect Issues                 │ │   │
│                           │  │                                  │ │   │
│                           │  │  Issues:                         │ │   │
│                           │  │  • Port mismatch in .env.dev:    │ │   │
│                           │  │    8000 != 8001                  │ │   │
│                           │  │  • WebSocket URL mismatch        │ │   │
│                           │  └──────────┬───────────────────────┘ │   │
│                           │             │                          │   │
│                           │             ↓                          │   │
│                           │  ┌──────────────────────────────────┐ │   │
│                           │  │ 5. Auto-Fix                      │ │   │
│                           │  │    auto_fix(health_check)        │ │   │
│                           │  │                                  │ │   │
│                           │  │  For each mismatch:              │ │   │
│                           │  │    1. Read .env file             │ │   │
│                           │  │    2. Regex replace wrong URL    │ │   │
│                           │  │    3. Write back atomically      │ │   │
│                           │  │    4. Validate fix worked        │ │   │
│                           │  │    5. Log success                │ │   │
│                           │  └──────────┬───────────────────────┘ │   │
│                           │             │                          │   │
│                           │             ↓                          │   │
│                           │  ┌──────────────────────────────────┐ │   │
│                           │  │ 6. Return Fix Result             │ │   │
│                           │  │                                  │ │   │
│                           │  │  fixes_attempted: 2              │ │   │
│                           │  │  fixes_successful: 2             │ │   │
│                           │  │  fixes_failed: 0                 │ │   │
│                           │  └──────────────────────────────────┘ │   │
│                           └────────────────────────────────────────┘   │
│                                          │                             │
│                                          ↓                             │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │ 7. Update Metrics                                                 │  │
│  │    • successful_fixes++                                           │  │
│  │    • connection_fixes_successful++                                │  │
│  │    • last_connection_check = now()                                │  │
│  └───────────────────────────────────────────────────────────────────┘  │
└─────────────────────┬───────────────────────────────────────────────────┘
                      │
                      │ Return success result
                      ↓
┌─────────────────────────────────────────────────────────────────────────┐
│                          USER / APPLICATION                              │
│                                                                          │
│  Response:                                                               │
│  {                                                                       │
│    "error_type": "ConnectionError",                                     │
│    "solution_found": true,                                              │
│    "fix_applied": true,                                                 │
│    "fix_successful": true,                                              │
│    "fix_type": "connection_auto_fix",                                   │
│    "solution": {                                                        │
│      "fixes_successful": 2,                                             │
│      "details": ["Fixed 2 port mismatches"]                             │
│    }                                                                    │
│  }                                                                      │
└─────────────────────────────────────────────────────────────────────────┘


┌─────────────────────────────────────────────────────────────────────────┐
│                         CONFIGURATION FILES                              │
└─────────────────────────────────────────────────────────────────────────┘

config/ports.json                    frontend/.env.development
┌──────────────────┐                ┌──────────────────────────┐
│ {                │   ◄───────────┤ VITE_API_BASE_URL=        │
│   "services": {  │   validated    │ http://127.0.0.1:8001   │
│     "backend": { │                └──────────────────────────┘
│       "dev": 8001│                        ↑
│     }            │                        │ auto-fixed
│   },             │                        │
│   "urls": {      │                frontend/.env.local
│     "backend": { │                ┌──────────────────────────┐
│       "dev":     │   ◄───────────┤ VITE_API_BASE_URL=        │
│       "http://   │   validated    │ http://127.0.0.1:8001   │
│       127...8001"│                └──────────────────────────┘
│     }            │
│   }              │
│ }                │
└──────────────────┘
  Single Source
    of Truth


┌─────────────────────────────────────────────────────────────────────────┐
│                         MANUAL TRIGGERS                                  │
└─────────────────────────────────────────────────────────────────────────┘

PowerShell Scripts:                 API Endpoints:
┌──────────────────────────┐        ┌──────────────────────────────────┐
│ .\scripts\check-ports.ps1│        │ GET /api/connection/health       │
│           -Fix           │        │ POST /api/connection/auto-fix    │
│                          │        │ GET /api/connection/config       │
│ .\scripts\connection-    │        │ GET /api/connection/ports        │
│    manager.ps1 -Detailed │        └──────────────────────────────────┘
└──────────────────────────┘


┌─────────────────────────────────────────────────────────────────────────┐
│                         KEY FEATURES                                     │
└─────────────────────────────────────────────────────────────────────────┘

✅ Automatic Detection        Error keywords trigger connection check
✅ Instant Auto-Fix           .env files updated in milliseconds  
✅ Atomic Operations          File writes are safe and atomic
✅ Validation                 Fixes are validated before completing
✅ Metrics Tracking           All fixes logged and counted
✅ Manual Triggers            API + PowerShell for manual control
✅ Central Configuration      Single source of truth (ports.json)
✅ Learning System            Patterns tracked, recurring issues prevented
✅ Zero Downtime              Fixes applied without service restart
✅ Self-Documenting           All operations logged with details


┌─────────────────────────────────────────────────────────────────────────┐
│                         EXAMPLE SCENARIO                                 │
└─────────────────────────────────────────────────────────────────────────┘

Time: 16:00:00  │  Frontend tries to login
                ↓
Time: 16:00:01  │  POST /api/auth/login → ConnectionError
                │  (frontend calling port 8000, backend on 8001)
                ↓
Time: 16:00:01  │  Self-healing catches error
                ↓
Time: 16:00:01  │  Connection monitor detects "connection" keyword
                ↓
Time: 16:00:01  │  Runs health check
                │  → Found mismatch: .env.development has 8000
                ↓
Time: 16:00:02  │  Auto-fixes .env.development
                │  → Updated to 8001
                ↓
Time: 16:00:02  │  Returns success
                │  {
                │    "fix_successful": true,
                │    "fixes_successful": 1
                │  }
                ↓
Time: 16:00:02  │  User notified: "Issue auto-fixed, restart frontend"
                │  (Instead of generic connection error)

Total time: 2 seconds from error to fix! ⚡
```
