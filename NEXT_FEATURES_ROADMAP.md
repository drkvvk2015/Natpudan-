# Next Features Roadmap — Post User Management

## Current Status
✅ Admin user management complete with full CRUD, pagination, search, validation  
✅ Data persistence verified  
✅ All changes committed and pushed to GitHub  

---

## Prioritized Feature Options

### 🥇 **Priority 1: User Activity & Audit Logs** (Recommended Next)
**Why**: Essential for compliance and debugging admin actions  
**Effort**: Medium (4-6 hours)  
**Impact**: High (required for production)

**Features**:
- Track all admin actions: user create/update/delete, password resets
- Audit log table: `id, admin_id, action, target_user_id, timestamp, details`
- View audit logs in admin dashboard (searchable, filterable by date range)
- Export audit logs to CSV for compliance
- Display "Last modified by" and "Last modified on" in user table

**Backend Work**:
- `backend/app/models.py`: Add `AuditLog` model with relationships
- `backend/app/api/admin_users.py`: Log all CRUD operations
- New endpoint: `GET /api/admin/audit-logs?user_id=X&action=create&start_date=Y&end_date=Z`
- Service: `backend/app/services/audit_service.py`

**Frontend Work**:
- New page: `frontend/src/pages/admin/AuditLogs.tsx`
- Table with: admin_email, action, target_user, timestamp, details
- Date range picker, action filter dropdown
- CSV export button
- Add "View Logs" link to user row action menu

---

### 🥈 **Priority 2: User Activity Dashboard** (Popular Request)
**Why**: Visibility into who's active, when they log in, session management  
**Effort**: Medium (5-7 hours)  
**Impact**: High (useful for monitoring)

**Features**:
- Track login events: `LoginEvent` model with user_id, timestamp, ip_address, user_agent
- Session management: know who's currently logged in, their last activity
- User activity timeline: "John logged in at 2:30 PM, viewed 5 patients, logged out at 3:45 PM"
- Dashboard widget: "Active users right now" (count + list)
- User detail page showing: last login, login count, last 10 logins with timestamps

**Backend Work**:
- `backend/app/models.py`: Add `LoginEvent` model
- `backend/app/api/auth_new.py`: Log login event on successful auth
- New endpoints:
  - `GET /api/admin/active-users` (currently logged in)
  - `GET /api/admin/users/{id}/activity` (login history + stats)

**Frontend Work**:
- Add activity section to UserManagement user detail modal
- New dashboard widget: "Active Users" with list
- Enhanced user table: add "Last Login" column

---

### 🥉 **Priority 3: Bulk User Operations** (Nice to Have)
**Why**: Reduce manual work for admins managing many users  
**Effort**: High (6-8 hours)  
**Impact**: Medium (convenience feature)

**Features**:
- CSV import: upload CSV with user data, create/update in bulk
- Bulk role change: select multiple users → change all to "doctor" at once
- Bulk status change: deactivate multiple users in one operation
- Progress bar for bulk operations (% complete, X of Y processed)
- Rollback on error: stop mid-operation if invalid data found

**Backend Work**:
- New endpoint: `POST /api/admin/users/bulk/import` (file upload)
- New endpoint: `PATCH /api/admin/users/bulk/roles` (multiple user IDs + new role)
- Service: `backend/app/services/bulk_operations_service.py`
- Validation: email uniqueness, password strength, role validity

**Frontend Work**:
- Add "Import CSV" button to UserManagement → opens file input
- Add "Bulk Actions" toolbar: select multiple users with checkboxes
- Bulk action menu: "Change Role", "Deactivate", "Delete All"
- Progress modal with real-time updates

---

### 💡 **Priority 4: Email Notifications** (Future Enhancement)
**Why**: Users can self-reset passwords, admins get alerts on sensitive actions  
**Effort**: High (7-9 hours)  
**Impact**: Medium (nice to have, requires SMTP setup)

**Features**:
- Welcome email when admin creates new user (with temp password)
- Password reset email with 24-hour token link
- Admin notification: "User created" → email admin digest
- Email templates: HTML + plaintext for all events

**Backend Work**:
- `backend/app/services/email_service.py` with SMTP integration
- Store `password_reset_token` in User model (with expiry)
- Endpoint: `POST /api/auth/send-password-reset` (sends email)
- Endpoint: `POST /api/auth/reset-password/{token}` (validates token, updates password)

**Frontend Work**:
- "Forgot Password?" link on login page
- Password reset form: enter email → sends link → user clicks → new password form

---

### 🎯 **Priority 5: Two-Factor Authentication (2FA)** (Production Requirement)
**Why**: Enhanced security for admin accounts  
**Effort**: Very High (8-10 hours)  
**Impact**: Very High (security critical)

**Features**:
- Enable/disable 2FA per user
- TOTP (Time-based One-Time Password) using Google Authenticator
- Backup codes for account recovery
- SMS as fallback (optional, requires service integration)

**Backend Work**:
- Add `totp_secret`, `backup_codes`, `two_factor_enabled` to User model
- Library: `pyotp` for TOTP generation/validation
- Endpoints: `POST /api/auth/2fa/setup`, `POST /api/auth/2fa/verify`, `POST /api/auth/2fa/disable`
- Login flow: check if 2FA enabled → prompt for TOTP code

**Frontend Work**:
- 2FA settings in user profile/settings page
- Setup wizard: show QR code, user scans with phone app, enters TOTP to verify
- Login form: second step for TOTP code
- Backup codes display and download

---

## Recommendation

### ✅ **Start with Priority 1: Audit Logs**
**Reasoning**:
- Builds on existing UserManagement component (familiar codebase)
- Enables compliance tracking (needed for healthcare app)
- Moderate complexity (not too hard, high value)
- Fast to implement (4-6 hours) and deploy
- Foundation for future features (activity dashboard can use same log table)

**Implementation plan**:
1. Add `AuditLog` model to `backend/app/models.py`
2. Create `audit_service.py` with `log_action()` method
3. Call `log_action()` in each user CRUD endpoint
4. Create `GET /api/admin/audit-logs` endpoint with filtering
5. Build `AuditLogs.tsx` page with table + search + export
6. Add menu item to Layout for "Audit Logs"
7. Test with sample logs from user creation/update/delete

**Time estimate**: 5-6 hours  
**Resources needed**: No external APIs, uses existing database

---

## Deployment Checklist (After Any Feature)

- [ ] All backend routes return proper error codes (400, 403, 404, 500)
- [ ] Frontend error handling for all API calls (try/catch, user-friendly messages)
- [ ] Database migrations (if new models added)
- [ ] Environment variables documented (.env.example)
- [ ] API endpoints documented in code comments
- [ ] Manual test in browser (login → navigate → CRUD → refresh → verify persistence)
- [ ] Automated tests added for critical paths
- [ ] Performance verified (no N+1 queries, pagination working)
- [ ] Git commit with clear message and changelog
- [ ] Push to clean-main2 (staging branch)
- [ ] Create PR to main branch with description
- [ ] Code review and merge

---

## Next Actions

1. **Option A (Recommended)**: Start Audit Logs feature
   ```powershell
   # Branch for new feature
   git checkout -b feature/audit-logs
   ```

2. **Option B**: Quick bug fixes or optimizations
   - Backend error logging improvements
   - Frontend form validation enhancements
   - Loading state optimization

3. **Option C**: Documentation/infrastructure
   - Update README with user management screenshots
   - Create deployment guide (Docker, production setup)
   - Add API documentation (OpenAPI/Swagger)

**What would you like to do next?**
