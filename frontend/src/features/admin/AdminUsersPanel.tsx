import { useCallback, useEffect, useState } from "react";
import { useLanguage } from "@/contexts/LanguageContext";
import { useAuth } from "@/contexts/AuthContext";
import { api, type AdminUser } from "@/lib/api";
import SlidegenConfirmDialog from "@/components/SlidegenConfirmDialog";

const copy = {
  en: {
    eyebrow: "ADMIN / USER MANAGEMENT",
    title: "Users",
    subtitle: "Manage admin access, reset a user's password, or start a fresh five-hour usage window.",
    passwordLabel: "Default reset password",
    passwordPlaceholder: "Enter at least 6 characters",
    passwordNote: "This password is used only for the selected reset and is not stored in the admin page.",
    passwordAction: "Set password",
    passwordConfirm: "Set the default password for",
    passwordDone: "Password reset successfully.",
    passwordError: "Unable to reset password.",
    usageAction: "Reset 5h",
    usageConfirm: "Reset usage and restart the five-hour window for",
    usageDone: "Usage reset. The five-hour window starts now.",
    usageError: "Unable to reset user usage.",
    loadError: "Unable to load users.",
    refresh: "Refresh",
    user: "User",
    plan: "Plan",
    role: "Role",
    admin: "Admin",
    userRole: "User",
    makeAdmin: "Make admin",
    removeAdmin: "Remove admin",
    adminConfirm: "Change admin access for",
    adminDone: "Admin access updated.",
    adminError: "Unable to update admin access.",
    selfAdminNote: "You cannot remove your own access.",
    usage: "Current usage",
    window: "Five-hour window",
    started: "Started",
    resets: "Resets",
    chat: "chat credits",
    messages: "messages",
    docs: "DOCX",
    active: "Active",
    inactive: "Inactive",
    empty: "No users found.",
    requiredPassword: "Enter a default password with at least 6 characters first.",
  },
  vi: {
    eyebrow: "ADMIN / QUẢN LÝ USER",
    title: "Quản lý user",
    subtitle: "Cấp quyền admin, đặt lại mật khẩu hoặc bắt đầu lại cửa sổ usage 5 giờ cho từng tài khoản.",
    passwordLabel: "Mật khẩu mặc định khi reset",
    passwordPlaceholder: "Nhập ít nhất 6 ký tự",
    passwordNote: "Mật khẩu này chỉ dùng cho lần reset đã chọn và không được lưu trên trang admin.",
    passwordAction: "Đặt mật khẩu",
    passwordConfirm: "Đặt mật khẩu mặc định cho",
    passwordDone: "Đã đặt lại mật khẩu.",
    passwordError: "Không thể đặt lại mật khẩu.",
    usageAction: "Reset 5 giờ",
    usageConfirm: "Reset usage và bắt đầu lại cửa sổ 5 giờ cho",
    usageDone: "Đã reset usage. Cửa sổ 5 giờ bắt đầu từ bây giờ.",
    usageError: "Không thể reset usage của user.",
    loadError: "Không thể tải danh sách user.",
    refresh: "Tải lại",
    user: "User",
    plan: "Plan",
    role: "Quyền",
    admin: "Admin",
    userRole: "User",
    makeAdmin: "Cấp admin",
    removeAdmin: "Gỡ admin",
    adminConfirm: "Thay đổi quyền admin cho",
    adminDone: "Đã cập nhật quyền admin.",
    adminError: "Không thể cập nhật quyền admin.",
    selfAdminNote: "Không thể tự gỡ quyền của chính mình.",
    usage: "Usage hiện tại",
    window: "Cửa sổ 5 giờ",
    started: "Bắt đầu",
    resets: "Reset lúc",
    chat: "credit chat",
    messages: "tin nhắn",
    docs: "DOCX",
    active: "Đang hoạt động",
    inactive: "Đã khóa",
    empty: "Chưa có user.",
    requiredPassword: "Hãy nhập mật khẩu mặc định có ít nhất 6 ký tự trước.",
  },
} as const;

function formatDate(value: string, language: "vi" | "en") {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "—";
  return new Intl.DateTimeFormat(language === "vi" ? "vi-VN" : "en-US", {
    dateStyle: "short",
    timeStyle: "short",
  }).format(date);
}

function displayPlan(tier: string) {
  return tier.charAt(0).toUpperCase() + tier.slice(1);
}

export default function AdminUsersPanel() {
  const { language } = useLanguage();
  const { user: currentUser } = useAuth();
  const t = copy[language];
  const [users, setUsers] = useState<AdminUser[]>([]);
  const [defaultPassword, setDefaultPassword] = useState("");
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState("");
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [pendingAction, setPendingAction] = useState<{
    type: "password" | "usage" | "admin";
    user: AdminUser;
    isAdmin?: boolean;
  } | null>(null);

  const loadUsers = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      setUsers(await api.getAdminUsers());
    } catch (loadError) {
      setError(loadError instanceof Error ? loadError.message : t.loadError);
    } finally {
      setLoading(false);
    }
  }, [t.loadError]);

  useEffect(() => {
    void loadUsers();
  }, [loadUsers]);

  const handlePasswordReset = (user: AdminUser) => {
    if (defaultPassword.length < 6) {
      setError(t.requiredPassword);
      setMessage("");
      return;
    }
    setPendingAction({ type: "password", user });
  };

  const confirmPasswordReset = async () => {
    const action = pendingAction;
    setPendingAction(null);
    if (!action || action.type !== "password") return;
    const user = action.user;
    setBusy(`password:${user.id}`);
    setError("");
    setMessage("");
    try {
      await api.resetAdminUserPassword(user.id, defaultPassword);
      setMessage(`${t.passwordDone} ${user.email}`);
    } catch (resetError) {
      setError(resetError instanceof Error ? resetError.message : t.passwordError);
    } finally {
      setBusy("");
    }
  };

  const handleUsageReset = (user: AdminUser) => {
    setPendingAction({ type: "usage", user });
  };

  const handleAdminRole = (user: AdminUser) => {
    if (user.id === currentUser?.id && user.is_admin) {
      setError(t.selfAdminNote);
      setMessage("");
      return;
    }
    setPendingAction({ type: "admin", user, isAdmin: !user.is_admin });
  };

  const confirmUsageReset = async () => {
    const action = pendingAction;
    setPendingAction(null);
    if (!action || action.type !== "usage") return;
    const user = action.user;
    setBusy(`usage:${user.id}`);
    setError("");
    setMessage("");
    try {
      const refreshed = await api.resetAdminUserUsage(user.id);
      setUsers((current) => current.map((item) => item.id === refreshed.id ? refreshed : item));
      setMessage(`${t.usageDone} ${user.email}`);
    } catch (resetError) {
      setError(resetError instanceof Error ? resetError.message : t.usageError);
    } finally {
      setBusy("");
    }
  };

  const confirmAdminRole = async () => {
    const action = pendingAction;
    setPendingAction(null);
    if (!action || action.type !== "admin" || action.isAdmin === undefined) return;
    const managedUser = action.user;
    setBusy(`admin:${managedUser.id}`);
    setError("");
    setMessage("");
    try {
      const refreshed = await api.updateAdminRole(managedUser.id, action.isAdmin);
      setUsers((current) => current.map((item) => item.id === refreshed.id ? refreshed : item));
      setMessage(`${t.adminDone} ${managedUser.email}`);
    } catch (roleError) {
      setError(roleError instanceof Error ? roleError.message : t.adminError);
    } finally {
      setBusy("");
    }
  };

  return (
    <div className="admin-users-content">
      <div className="admin-users-header">
        <div>
          <p className="workspace-eyebrow">{t.eyebrow}</p>
          <h2>{t.title}</h2>
          <p className="guide-lead">{t.subtitle}</p>
        </div>
        <div className="admin-users-password-box">
          <label htmlFor="admin-default-password">{t.passwordLabel}</label>
          <input
            id="admin-default-password"
            type="password"
            value={defaultPassword}
            placeholder={t.passwordPlaceholder}
            onChange={(event) => setDefaultPassword(event.target.value)}
            autoComplete="new-password"
          />
          <small>{t.passwordNote}</small>
        </div>
        <button type="button" className="admin-usage-reset admin-users-refresh" onClick={() => void loadUsers()} disabled={loading || Boolean(busy)}>
          {t.refresh}
        </button>
      </div>

      {loading ? <div className="admin-usage-state">Loading...</div> : users.length === 0 ? (
        <div className="admin-usage-state">{t.empty}</div>
      ) : (
        <div className="admin-users-table-wrap">
          <table className="admin-users-table">
            <thead>
              <tr>
                <th>{t.user}</th>
                <th>{t.plan}</th>
                <th>{t.role}</th>
                <th>{t.usage}</th>
                <th>{t.window}</th>
                <th aria-label="Actions" />
              </tr>
            </thead>
            <tbody>
              {users.map((user) => (
                <tr key={user.id}>
                  <td>
                    <strong>{user.full_name || user.username}</strong>
                    <small>{user.email}</small>
                    <em className={user.is_active ? "is-active" : "is-inactive"}>{user.is_active ? t.active : t.inactive}</em>
                  </td>
                  <td><span className="admin-users-plan">{displayPlan(user.subscription_tier)}</span></td>
                  <td>
                    <span className={`admin-users-role ${user.is_admin ? "is-admin" : ""}`}>
                      {user.is_admin ? t.admin : t.userRole}
                    </span>
                  </td>
                  <td>
                    <div className="admin-users-usage"><strong>{user.chat_usage}</strong> {t.chat}</div>
                    <div className="admin-users-usage"><strong>{user.chat_message_count}</strong> {t.messages} · <strong>{user.docx_usage}</strong> {t.docs}</div>
                  </td>
                  <td>
                    <div className="admin-users-window"><span>{t.started}</span>{formatDate(user.usage_window_started_at, language)}</div>
                    <div className="admin-users-window"><span>{t.resets}</span>{formatDate(user.usage_reset_at, language)}</div>
                  </td>
                  <td>
                    <div className="admin-users-actions">
                      <button type="button" onClick={() => void handlePasswordReset(user)} disabled={Boolean(busy) || defaultPassword.length < 6}>
                        {busy === `password:${user.id}` ? "…" : t.passwordAction}
                      </button>
                      <button type="button" onClick={() => void handleUsageReset(user)} disabled={Boolean(busy)}>
                        {busy === `usage:${user.id}` ? "…" : t.usageAction}
                      </button>
                      <button
                        type="button"
                        onClick={() => void handleAdminRole(user)}
                        disabled={Boolean(busy) || (user.id === currentUser?.id && user.is_admin)}
                        title={user.id === currentUser?.id && user.is_admin ? t.selfAdminNote : undefined}
                      >
                        {busy === `admin:${user.id}` ? "…" : user.is_admin ? t.removeAdmin : t.makeAdmin}
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {message && <p className="admin-usage-message">{message}</p>}
      {error && <p className="admin-usage-error">{error}</p>}
      <SlidegenConfirmDialog
        open={Boolean(pendingAction)}
        onOpenChange={(open) => {
          if (!open) setPendingAction(null);
        }}
        title={pendingAction?.type === "password"
          ? t.passwordAction
          : pendingAction?.type === "admin"
            ? (pendingAction.isAdmin ? t.makeAdmin : t.removeAdmin)
            : t.usageAction}
        description={pendingAction?.type === "password"
          ? `${t.passwordConfirm} ${pendingAction.user.email}?`
          : pendingAction?.type === "admin"
            ? `${t.adminConfirm} ${pendingAction.user.email}?`
            : `${t.usageConfirm} ${pendingAction?.user.email || ""}?`}
        confirmLabel={pendingAction?.type === "password"
          ? t.passwordAction
          : pendingAction?.type === "admin"
            ? (pendingAction.isAdmin ? t.makeAdmin : t.removeAdmin)
            : t.usageAction}
        cancelLabel={language === "vi" ? "Hủy" : "Cancel"}
        onConfirm={() => void (
          pendingAction?.type === "password"
            ? confirmPasswordReset()
            : pendingAction?.type === "admin"
              ? confirmAdminRole()
              : confirmUsageReset()
        )}
        destructive={pendingAction?.type === "usage" || (pendingAction?.type === "admin" && !pendingAction.isAdmin)}
        busy={Boolean(busy)}
      />
    </div>
  );
}
