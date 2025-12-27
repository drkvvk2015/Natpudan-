import React, { useEffect, useState } from "react";
import {
  listUsers,
  createUser,
  updateUser,
  deleteUser,
  setPassword,
  type UserOut,
  type UpdateUserPayload,
} from "../../services/adminUsers";
import {
  Box,
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  IconButton,
  MenuItem,
  Stack,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  TextField,
  Tooltip,
  Typography,
  Chip,
  Card,
  Alert,
  CircularProgress,
  Pagination,
  TableContainer,
  Paper,
  FormControl,
  InputLabel,
  Select,
} from "@mui/material";
import {
  Add as AddIcon,
  Delete as DeleteIcon,
  Edit as EditIcon,
  Key as KeyIcon,
  Refresh as RefreshIcon,
} from "@mui/icons-material";

const emptyForm = {
  email: "",
  password: "",
  confirmPassword: "",
  full_name: "",
  role: "staff" as "staff" | "doctor" | "admin",
  license_number: "",
};

const UserManagement: React.FC = () => {
  const [users, setUsers] = useState<UserOut[]>([]);
  const [allUsers, setAllUsers] = useState<UserOut[]>([]);
  const [q, setQ] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Pagination
  const [page, setPage] = useState(1);
  const pageSize = 10;
  const totalPages = Math.ceil(allUsers.length / pageSize);

  // Create dialog
  const [createOpen, setCreateOpen] = useState(false);
  const [createForm, setCreateForm] = useState(emptyForm);
  const [createErrors, setCreateErrors] = useState<Record<string, string>>({});

  // Edit dialog
  const [editOpen, setEditOpen] = useState(false);
  const [editingUser, setEditingUser] = useState<UserOut | null>(null);
  const [editForm, setEditForm] = useState<Partial<UserOut>>({});
  const [editErrors, setEditErrors] = useState<Record<string, string>>({});

  // Password dialog
  const [pwdOpen, setPwdOpen] = useState(false);
  const [pwdUserId, setPwdUserId] = useState<number | null>(null);
  const [pwdValue, setPwdValue] = useState("");
  const [pwdError, setPwdError] = useState("");

  // Delete confirmation
  const [deleteOpen, setDeleteOpen] = useState(false);
  const [userToDelete, setUserToDelete] = useState<UserOut | null>(null);

  async function load() {
    setLoading(true);
    setError(null);
    try {
      const data = await listUsers(q || undefined);
      setAllUsers(data);
      setPage(1);
    } catch (err) {
      const msg = err instanceof Error ? err.message : "Failed to load users";
      setError(msg);
      console.error(msg);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, [q]);

  // Paginate displayed users
  useEffect(() => {
    const start = (page - 1) * pageSize;
    const end = start + pageSize;
    setUsers(allUsers.slice(start, end));
  }, [allUsers, page]);

  // ========== Create User ==========
  const validateCreateForm = (): boolean => {
    const errors: Record<string, string> = {};
    if (!createForm.email?.trim()) errors.email = "Email required";
    else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(createForm.email))
      errors.email = "Invalid email";
    if (!createForm.password) errors.password = "Password required";
    else if (createForm.password.length < 8)
      errors.password = "Min 8 characters";
    if (createForm.password !== createForm.confirmPassword)
      errors.confirmPassword = "Passwords don't match";
    if (!createForm.full_name?.trim()) errors.full_name = "Full name required";
    setCreateErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleCreateOpen = () => {
    setCreateForm(emptyForm);
    setCreateErrors({});
    setCreateOpen(true);
  };

  const handleCreateSubmit = async () => {
    if (!validateCreateForm()) return;
    setLoading(true);
    try {
      await createUser({
        email: createForm.email,
        password: createForm.password,
        full_name: createForm.full_name,
        role: createForm.role,
        license_number: createForm.license_number,
        is_active: true,
      });
      setCreateOpen(false);
      await load();
    } catch (err) {
      const msg = err instanceof Error ? err.message : "Create failed";
      setCreateErrors({ submit: msg });
    } finally {
      setLoading(false);
    }
  };

  // ========== Edit User ==========
  const handleEditOpen = (user: UserOut) => {
    setEditingUser(user);
    setEditForm({ ...user });
    setEditErrors({});
    setEditOpen(true);
  };

  const handleEditSubmit = async () => {
    if (!editingUser) return;
    setLoading(true);
    try {
      // Filter out null values and only send defined fields to match UpdateUserPayload type
      const payload: UpdateUserPayload = {};
      if (editForm.full_name !== undefined)
        payload.full_name = editForm.full_name;
      if (editForm.role !== undefined) payload.role = editForm.role;
      if (
        editForm.license_number !== undefined &&
        editForm.license_number !== null
      ) {
        payload.license_number = editForm.license_number;
      }
      if (editForm.is_active !== undefined)
        payload.is_active = editForm.is_active;

      await updateUser(editingUser.id, payload);
      setEditOpen(false);
      await load();
    } catch (err) {
      const msg = err instanceof Error ? err.message : "Update failed";
      setEditErrors({ submit: msg });
    } finally {
      setLoading(false);
    }
  };

  // ========== Set Password ==========
  const handleOpenPwdDialog = (user: UserOut) => {
    setPwdUserId(user.id);
    setPwdValue("");
    setPwdError("");
    setPwdOpen(true);
  };

  const handleSetPassword = async () => {
    if (!pwdValue || pwdValue.length < 8) {
      setPwdError("Password must be at least 8 characters");
      return;
    }
    if (!pwdUserId) return;
    setLoading(true);
    try {
      await setPassword(pwdUserId, pwdValue);
      setPwdOpen(false);
      await load();
    } catch (err) {
      const msg = err instanceof Error ? err.message : "Failed to set password";
      setPwdError(msg);
    } finally {
      setLoading(false);
    }
  };

  // ========== Delete User ==========
  const handleDeleteOpen = (user: UserOut) => {
    setUserToDelete(user);
    setDeleteOpen(true);
  };

  const handleDeleteConfirm = async () => {
    if (!userToDelete) return;
    setLoading(true);
    try {
      await deleteUser(userToDelete.id);
      setDeleteOpen(false);
      await load();
    } catch (err) {
      const msg = err instanceof Error ? err.message : "Delete failed";
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box sx={{ p: 3 }}>
      <Card sx={{ mb: 3 }}>
        <Box
          sx={{
            p: 2,
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
          }}
        >
          <Typography variant="h5" sx={{ m: 0 }}>
            User Management
          </Typography>
          <Button
            variant="contained"
            color="primary"
            startIcon={<AddIcon />}
            onClick={handleCreateOpen}
            disabled={loading}
          >
            Create User
          </Button>
        </Box>
      </Card>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      <Card sx={{ mb: 3 }}>
        <Box sx={{ p: 2 }}>
          <TextField
            fullWidth
            placeholder="Search by email or name..."
            value={q}
            onChange={(e) => setQ(e.target.value)}
            variant="outlined"
            size="small"
          />
        </Box>
      </Card>

      {loading && !users.length ? (
        <Box sx={{ display: "flex", justifyContent: "center", p: 4 }}>
          <CircularProgress />
        </Box>
      ) : (
        <TableContainer component={Paper}>
          <Table size="small">
            <TableHead sx={{ backgroundColor: "#f5f5f5" }}>
              <TableRow>
                <TableCell>Email</TableCell>
                <TableCell>Full Name</TableCell>
                <TableCell>Role</TableCell>
                <TableCell align="center">Status</TableCell>
                <TableCell align="right">Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {users.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={5} align="center" sx={{ py: 4 }}>
                    No users found
                  </TableCell>
                </TableRow>
              ) : (
                users.map((u) => (
                  <TableRow key={u.id} hover>
                    <TableCell>{u.email}</TableCell>
                    <TableCell>{u.full_name}</TableCell>
                    <TableCell>
                      <Chip
                        label={
                          u.role === "admin"
                            ? "Admin"
                            : u.role === "doctor"
                            ? "Doctor"
                            : "Staff"
                        }
                        size="small"
                        color={
                          u.role === "admin"
                            ? "error"
                            : u.role === "doctor"
                            ? "info"
                            : "default"
                        }
                        variant="outlined"
                      />
                    </TableCell>
                    <TableCell align="center">
                      <Chip
                        label={u.is_active ? "Active" : "Inactive"}
                        size="small"
                        color={u.is_active ? "success" : "default"}
                      />
                    </TableCell>
                    <TableCell align="right">
                      <Tooltip title="Edit">
                        <IconButton
                          size="small"
                          color="primary"
                          onClick={() => handleEditOpen(u)}
                        >
                          <EditIcon />
                        </IconButton>
                      </Tooltip>
                      <Tooltip title="Reset Password">
                        <IconButton
                          size="small"
                          color="warning"
                          onClick={() => handleOpenPwdDialog(u)}
                        >
                          <KeyIcon />
                        </IconButton>
                      </Tooltip>
                      <Tooltip title="Delete">
                        <IconButton
                          size="small"
                          color="error"
                          onClick={() => handleDeleteOpen(u)}
                        >
                          <DeleteIcon />
                        </IconButton>
                      </Tooltip>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </TableContainer>
      )}

      {users.length > 0 && (
        <Box sx={{ display: "flex", justifyContent: "center", p: 2 }}>
          <Pagination
            count={totalPages}
            page={page}
            onChange={(_, newPage) => setPage(newPage)}
            disabled={loading}
          />
        </Box>
      )}

      {/* ========== CREATE USER DIALOG ========== */}
      <Dialog
        open={createOpen}
        onClose={() => setCreateOpen(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>Create New User</DialogTitle>
        <DialogContent
          sx={{ display: "flex", flexDirection: "column", gap: 2, pt: 2 }}
        >
          {createErrors.submit && (
            <Alert severity="error">{createErrors.submit}</Alert>
          )}

          <TextField
            label="Email"
            type="email"
            fullWidth
            value={createForm.email}
            onChange={(e) =>
              setCreateForm({ ...createForm, email: e.target.value })
            }
            error={!!createErrors.email}
            helperText={createErrors.email}
            disabled={loading}
          />

          <TextField
            label="Full Name"
            fullWidth
            value={createForm.full_name}
            onChange={(e) =>
              setCreateForm({ ...createForm, full_name: e.target.value })
            }
            error={!!createErrors.full_name}
            helperText={createErrors.full_name}
            disabled={loading}
          />

          <TextField
            label="Password"
            type="password"
            fullWidth
            value={createForm.password}
            onChange={(e) =>
              setCreateForm({ ...createForm, password: e.target.value })
            }
            error={!!createErrors.password}
            helperText={createErrors.password}
            disabled={loading}
          />

          <TextField
            label="Confirm Password"
            type="password"
            fullWidth
            value={createForm.confirmPassword}
            onChange={(e) =>
              setCreateForm({ ...createForm, confirmPassword: e.target.value })
            }
            error={!!createErrors.confirmPassword}
            helperText={createErrors.confirmPassword}
            disabled={loading}
          />

          <FormControl fullWidth>
            <InputLabel>Role</InputLabel>
            <Select
              value={createForm.role}
              label="Role"
              onChange={(e) =>
                setCreateForm({ ...createForm, role: e.target.value as any })
              }
              disabled={loading}
            >
              <MenuItem value="staff">Staff</MenuItem>
              <MenuItem value="doctor">Doctor</MenuItem>
              <MenuItem value="admin">Admin</MenuItem>
            </Select>
          </FormControl>

          <TextField
            label="License Number (optional)"
            fullWidth
            value={createForm.license_number}
            onChange={(e) =>
              setCreateForm({ ...createForm, license_number: e.target.value })
            }
            disabled={loading}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setCreateOpen(false)} disabled={loading}>
            Cancel
          </Button>
          <Button
            onClick={handleCreateSubmit}
            variant="contained"
            disabled={loading}
          >
            {loading ? <CircularProgress size={24} /> : "Create"}
          </Button>
        </DialogActions>
      </Dialog>

      {/* ========== EDIT USER DIALOG ========== */}
      <Dialog
        open={editOpen}
        onClose={() => setEditOpen(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>Edit User: {editingUser?.email}</DialogTitle>
        <DialogContent
          sx={{ display: "flex", flexDirection: "column", gap: 2, pt: 2 }}
        >
          {editErrors.submit && (
            <Alert severity="error">{editErrors.submit}</Alert>
          )}

          <TextField
            label="Full Name"
            fullWidth
            value={editForm.full_name || ""}
            onChange={(e) =>
              setEditForm({ ...editForm, full_name: e.target.value })
            }
            error={!!editErrors.full_name}
            helperText={editErrors.full_name}
            disabled={loading}
          />

          <FormControl fullWidth>
            <InputLabel>Role</InputLabel>
            <Select
              value={editForm.role || "staff"}
              label="Role"
              onChange={(e) =>
                setEditForm({ ...editForm, role: e.target.value as any })
              }
              disabled={loading}
            >
              <MenuItem value="staff">Staff</MenuItem>
              <MenuItem value="doctor">Doctor</MenuItem>
              <MenuItem value="admin">Admin</MenuItem>
            </Select>
          </FormControl>

          <TextField
            label="License Number"
            fullWidth
            value={editForm.license_number || ""}
            onChange={(e) =>
              setEditForm({ ...editForm, license_number: e.target.value })
            }
            disabled={loading}
          />

          <FormControl fullWidth>
            <InputLabel>Status</InputLabel>
            <Select
              value={
                editForm.is_active !== undefined ? editForm.is_active : true
              }
              label="Status"
              onChange={(e) =>
                setEditForm({
                  ...editForm,
                  is_active: e.target.value === "true",
                })
              }
              disabled={loading}
            >
              <MenuItem value="true">Active</MenuItem>
              <MenuItem value="false">Inactive</MenuItem>
            </Select>
          </FormControl>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setEditOpen(false)} disabled={loading}>
            Cancel
          </Button>
          <Button
            onClick={handleEditSubmit}
            variant="contained"
            disabled={loading}
          >
            {loading ? <CircularProgress size={24} /> : "Save"}
          </Button>
        </DialogActions>
      </Dialog>

      {/* ========== SET PASSWORD DIALOG ========== */}
      <Dialog
        open={pwdOpen}
        onClose={() => setPwdOpen(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>Reset Password</DialogTitle>
        <DialogContent
          sx={{ display: "flex", flexDirection: "column", gap: 2, pt: 2 }}
        >
          {pwdError && <Alert severity="error">{pwdError}</Alert>}
          <TextField
            label="New Password"
            type="password"
            fullWidth
            value={pwdValue}
            onChange={(e) => setPwdValue(e.target.value)}
            disabled={loading}
            autoFocus
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setPwdOpen(false)} disabled={loading}>
            Cancel
          </Button>
          <Button
            onClick={handleSetPassword}
            variant="contained"
            disabled={loading}
          >
            {loading ? <CircularProgress size={24} /> : "Set Password"}
          </Button>
        </DialogActions>
      </Dialog>

      {/* ========== DELETE CONFIRMATION DIALOG ========== */}
      <Dialog open={deleteOpen} onClose={() => setDeleteOpen(false)}>
        <DialogTitle>Delete User</DialogTitle>
        <DialogContent>
          Are you sure you want to delete <strong>{userToDelete?.email}</strong>
          ? This cannot be undone.
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteOpen(false)} disabled={loading}>
            Cancel
          </Button>
          <Button
            onClick={handleDeleteConfirm}
            color="error"
            variant="contained"
            disabled={loading}
          >
            {loading ? <CircularProgress size={24} /> : "Delete"}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default UserManagement;
