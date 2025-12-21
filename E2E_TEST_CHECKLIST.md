# END-TO-END FRONTEND TEST CHECKLIST
# ====================================
# Test Date: Dec 21, 2025
# Backend: http://127.0.0.1:8000
# Frontend: http://127.0.0.1:5173
# Admin Account: admin@admin.com / Admin@123

## TEST 1: Backend Health & Login
- [ ] Check /health endpoint → healthy
- [ ] Login page loads (http://127.0.0.1:5173/login)
- [ ] Backend status chip shows GREEN
- [ ] Enter admin@admin.com / Admin@123
- [ ] Click Login → should redirect to dashboard
- [ ] Dashboard loads successfully

## TEST 2: Navigation to User Management
- [ ] Click hamburger menu (top-left)
- [ ] Scroll down to "User Management" (admin section, red icon)
- [ ] Click "User Management" → should navigate to /admin/users
- [ ] Page title shows "User Management"
- [ ] Table loads with existing users (admin user should be visible)
- [ ] Search box visible
- [ ] "Create User" button visible and enabled

## TEST 3: List & Search Users
- [ ] Page shows admin@admin.com in table
- [ ] Search box: type "admin" → filters to show admin user only
- [ ] Clear search box → shows all users again
- [ ] Pagination shows at bottom (if more than 10 users)
- [ ] Click next page → loads next 10 users
- [ ] User roles show as chips (Admin = red, Doctor = blue, Staff = gray)
- [ ] Status shows as chips (Active = green, Inactive = gray)

## TEST 4: Create User
- [ ] Click "Create User" button
- [ ] Dialog opens with title "Create New User"
- [ ] Form fields visible:
     - Email
     - Full Name
     - Password
     - Confirm Password
     - Role (dropdown)
     - License Number (optional)
- [ ] Fill form with:
     - Email: testuser@example.com
     - Full Name: Test User
     - Password: TestPass@123
     - Confirm Password: TestPass@123
     - Role: Doctor
     - License Number: (leave blank)
- [ ] Click "Create" button
- [ ] Dialog closes
- [ ] New user appears in table
- [ ] User shows role "Doctor" (blue chip)
- [ ] User shows status "Active" (green chip)

## TEST 5: Edit User
- [ ] Find the test user in table
- [ ] Click pencil icon (Edit button)
- [ ] Edit dialog opens with title "Edit User: testuser@example.com"
- [ ] Fields pre-populated with current user data:
     - Full Name: Test User
     - Role: Doctor
     - License Number: (empty)
     - Status: Active
- [ ] Change Full Name to: "Dr. Test User Updated"
- [ ] Change Role to: Staff
- [ ] Change Status to: Inactive
- [ ] Click "Save" button
- [ ] Dialog closes
- [ ] Table updates:
     - Full Name now shows "Dr. Test User Updated"
     - Role now shows "Staff" (gray chip)
     - Status now shows "Inactive" (gray chip)

## TEST 6: Reset Password
- [ ] Find the test user in table
- [ ] Click lock icon (Reset Password button)
- [ ] Password dialog opens with title "Reset Password"
- [ ] Enter new password: NewPass@456
- [ ] Click "Set Password" button
- [ ] Dialog closes
- [ ] (Password was changed without navigating away)

## TEST 7: Delete User
- [ ] Find the test user in table
- [ ] Click trash icon (Delete button)
- [ ] Confirmation dialog appears:
     - Title: "Delete User"
     - Message: "Are you sure you want to delete testuser@example.com? This cannot be undone."
- [ ] Click "Delete" button
- [ ] Dialog closes
- [ ] User disappears from table
- [ ] Search for "testuser" → no results found (confirms deletion)

## TEST 8: Form Validation
- [ ] Click "Create User" button
- [ ] Leave all fields empty
- [ ] Click "Create" → error messages appear:
     - Email required
     - Full Name required
     - Password required
- [ ] Enter invalid email: "notanemail"
- [ ] Click "Create" → error: "Invalid email"
- [ ] Enter password: "short"
- [ ] Click "Create" → error: "Min 8 characters"
- [ ] Fill correctly and verify create succeeds

## TEST 9: Error Handling
- [ ] Try to create user with existing email (admin@admin.com)
- [ ] Error message appears: "Email already registered"
- [ ] Dialog stays open so user can retry

## TEST 10: Admin-Only Access
- [ ] Logout (click user menu → Logout)
- [ ] Create new browser tab, go to /admin/users directly
- [ ] Should redirect to login (route is protected)
- [ ] Login as staff user (if available, or create one)
- [ ] Try to access /admin/users directly
- [ ] Should be blocked/redirected (only admin can access)

## NOTES
- All actions should complete within 2-3 seconds (no hangs)
- Backend should handle concurrent requests without errors
- No JavaScript console errors should appear
- Page should not refresh unintentionally during operations
- All chips and colors should render correctly

## FINAL RESULT
- [ ] All 10 tests PASSED
- [ ] No errors in browser console
- [ ] No errors in backend logs
- [ ] Ready for commit and deploy
