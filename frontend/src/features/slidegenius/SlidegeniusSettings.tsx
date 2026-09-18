import { useEffect, useMemo, useRef, useState } from "react";
import { useBlocker } from "react-router-dom";
import { useAuth } from "@/contexts/AuthContext";
import { useLanguage } from "@/contexts/LanguageContext";
import { useTheme } from "@/contexts/ThemeContext";
import { api } from "@/lib/api";
import { useToast } from "@/hooks/use-toast";
import { publishNotificationsEnabled } from "@/lib/notificationSound";
import SlidegenConfirmDialog from "@/components/SlidegenConfirmDialog";
import "./slidegenius-settings.css";

type SettingsTab = "profile" | "account" | "appearance" | "security";
type ThemeChoice = "light" | "dark";

export default function SlidegeniusSettings() {
  const { user, updateUser } = useAuth();
  const { language, setLanguage, t } = useLanguage();
  const { theme, toggleTheme, autoTheme, setAutoTheme } = useTheme();
  const { toast } = useToast();
  const [activeTab, setActiveTab] = useState<SettingsTab>("profile");
  const [fullName, setFullName] = useState("");
  const [avatarUrl, setAvatarUrl] = useState("");
  const [bio, setBio] = useState("");
  const [profileLoading, setProfileLoading] = useState(true);
  const [draftLanguage, setDraftLanguage] = useState(language);
  const [draftTheme, setDraftTheme] = useState<ThemeChoice>(theme);
  const [draftAutoTheme, setDraftAutoTheme] = useState(autoTheme);
  const [notificationsEnabled, setNotificationsEnabled] = useState(true);
  const [currentPassword, setCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [showCurrent, setShowCurrent] = useState(false);
  const [showNew, setShowNew] = useState(false);
  const [showConfirm, setShowConfirm] = useState(false);
  const [saving, setSaving] = useState(false);
  const [unsavedDialogOpen, setUnsavedDialogOpen] = useState(false);
  const savedProfileRef = useRef({ fullName: "", avatarUrl: "", bio: "" });
  const savedAppearanceRef = useRef({
    language,
    theme,
    autoTheme,
    notificationsEnabled: true,
  });
  const proceedingRef = useRef(false);

  const userName = fullName || user?.full_name || user?.username || user?.email || "Slidegen user";
  const initials = useMemo(() => userName.slice(0, 2).toUpperCase(), [userName]);
  const hasProfileChanges = !profileLoading && (
    fullName !== savedProfileRef.current.fullName
    || avatarUrl !== savedProfileRef.current.avatarUrl
    || bio !== savedProfileRef.current.bio
  );
  const hasAppearanceChanges = !profileLoading && (
    draftLanguage !== savedAppearanceRef.current.language
    || draftTheme !== savedAppearanceRef.current.theme
    || draftAutoTheme !== savedAppearanceRef.current.autoTheme
    || notificationsEnabled !== savedAppearanceRef.current.notificationsEnabled
  );
  const hasPasswordChanges = Boolean(currentPassword || newPassword || confirmPassword);
  const hasUnsavedChanges = hasProfileChanges || hasAppearanceChanges || hasPasswordChanges;
  const unsavedCopy = language === "vi"
    ? {
        title: "Bạn có thay đổi chưa lưu",
        description: t.appearance_unsaved_warning,
        stay: "Ở lại",
        leave: "Rời đi",
      }
    : {
        title: "You have unsaved changes",
        description: t.appearance_unsaved_warning,
        stay: "Stay",
        leave: "Leave",
      };
  const blocker = useBlocker(hasUnsavedChanges);
  const blockerState = blocker.state;

  useEffect(() => {
    let active = true;
    Promise.all([api.getProfile(), api.getSettings()]).then(([profile, settings]) => {
      if (!active) return;
      const nextProfile = {
        fullName: profile.full_name ?? "",
        avatarUrl: profile.avatar_url ?? "",
        bio: profile.bio ?? "",
      };
      const nextLanguage = settings?.language === "en" || settings?.language === "vi"
        ? settings.language
        : savedAppearanceRef.current.language;
      const nextAutoTheme = settings?.theme === "system" ? true : savedAppearanceRef.current.autoTheme;
      const nextTheme = settings?.theme === "light" || settings?.theme === "dark"
        ? settings.theme
        : savedAppearanceRef.current.theme;
      const nextNotifications = typeof settings?.notifications_enabled === "boolean"
        ? settings.notifications_enabled
        : true;

      setFullName(nextProfile.fullName);
      setAvatarUrl(nextProfile.avatarUrl);
      setBio(nextProfile.bio);
      setDraftLanguage(nextLanguage);
      setDraftTheme(nextTheme);
      setDraftAutoTheme(nextAutoTheme);
      setNotificationsEnabled(nextNotifications);
      savedProfileRef.current = nextProfile;
      savedAppearanceRef.current = {
        language: nextLanguage,
        theme: nextTheme,
        autoTheme: nextAutoTheme,
        notificationsEnabled: nextNotifications,
      };
    }).catch(() => {
      // The local auth state remains usable when the profile endpoint is temporarily unavailable.
    }).finally(() => {
      if (active) setProfileLoading(false);
    });
    return () => { active = false; };
  }, []);

  useEffect(() => {
    setDraftLanguage(language);
  }, [language]);

  useEffect(() => {
    const handleBeforeUnload = (event: BeforeUnloadEvent) => {
      if (!hasUnsavedChanges) return;
      event.preventDefault();
      event.returnValue = "";
    };

    window.addEventListener("beforeunload", handleBeforeUnload);
    return () => window.removeEventListener("beforeunload", handleBeforeUnload);
  }, [hasUnsavedChanges]);

  useEffect(() => {
    if (blockerState === "blocked") setUnsavedDialogOpen(true);
    if (blockerState === "unblocked") {
      setUnsavedDialogOpen(false);
      proceedingRef.current = false;
    }
  }, [blockerState]);

  const handleUnsavedDialogChange = (open: boolean) => {
    setUnsavedDialogOpen(open);
    if (!open) {
      if (!proceedingRef.current && blocker.state === "blocked") blocker.reset();
      proceedingRef.current = false;
    }
  };

  const leaveWithUnsavedChanges = () => {
    proceedingRef.current = true;
    setUnsavedDialogOpen(false);
    blocker.proceed();
  };

  const handleSaveSettings = async () => {
    if (!hasUnsavedChanges || saving) return;

    if (hasPasswordChanges) {
      if (!currentPassword || !newPassword || !confirmPassword) {
        toast({ title: t.toast_password_error, variant: "destructive" });
        return;
      }
      if (newPassword.length < 6) {
        toast({ title: t.toast_password_short, variant: "destructive" });
        return;
      }
      if (newPassword !== confirmPassword) {
        toast({ title: t.toast_password_mismatch, variant: "destructive" });
        return;
      }
    }

    setSaving(true);
    try {
      const saveOperations: Promise<unknown>[] = [];
      if (hasProfileChanges) {
        saveOperations.push(api.updateProfile({ full_name: fullName, avatar_url: avatarUrl, bio }));
      }
      if (hasAppearanceChanges) {
        saveOperations.push(api.updateSettings({
          language: draftLanguage,
          theme: draftAutoTheme ? "system" : draftTheme,
          notifications_enabled: notificationsEnabled,
        }));
      }
      if (hasPasswordChanges) {
        saveOperations.push(api.changePassword(currentPassword, newPassword));
      }
      await Promise.all(saveOperations);

      if (hasProfileChanges) {
        updateUser({ full_name: fullName, avatar_url: avatarUrl });
        savedProfileRef.current = { fullName, avatarUrl, bio };
      }
      if (hasAppearanceChanges) {
        setLanguage(draftLanguage);
        if (draftAutoTheme !== autoTheme) setAutoTheme(draftAutoTheme);
        if (!draftAutoTheme && draftTheme !== theme) toggleTheme();
        publishNotificationsEnabled(notificationsEnabled);
        savedAppearanceRef.current = {
          language: draftLanguage,
          theme: draftTheme,
          autoTheme: draftAutoTheme,
          notificationsEnabled,
        };
      }
      if (hasPasswordChanges) {
        setCurrentPassword("");
        setNewPassword("");
        setConfirmPassword("");
      }
      toast({
        title: hasPasswordChanges && !hasProfileChanges && !hasAppearanceChanges
          ? t.toast_password_success
          : t.toast_settings_success,
      });
    } catch {
      toast({
        title: hasPasswordChanges && !hasProfileChanges && !hasAppearanceChanges
          ? t.toast_password_error
          : t.toast_settings_error,
        variant: "destructive",
      });
    } finally {
      setSaving(false);
    }
  };

  const tabs: Array<{ id: SettingsTab; label: string }> = [
    { id: "profile", label: t.tab_profile },
    { id: "account", label: t.tab_account },
    { id: "appearance", label: t.tab_appearance },
    { id: "security", label: t.tab_security },
  ];

  const asideCopy = language === "vi"
    ? {
        eyebrow: "WORKSPACE / PROFILE",
        title: "Một không gian vừa với bạn.",
        description: "Điều chỉnh những chi tiết nhỏ để mỗi lần mở Slidegenius đều có cảm giác quen thuộc.",
        language: "Ngôn ngữ",
        theme: "Giao diện",
        notifications: "Thông báo",
        enabled: "Đang bật",
        disabled: "Đang tắt",
        note: "Thay đổi được lưu theo tài khoản của bạn.",
      }
    : {
        eyebrow: "WORKSPACE / PROFILE",
        title: "A workspace that feels like yours.",
        description: "Tune the small details so every Slidegenius session feels familiar.",
        language: "Language",
        theme: "Theme",
        notifications: "Notifications",
        enabled: "On",
        disabled: "Off",
        note: "Changes are saved to your account.",
      };
  const themeLabel = draftAutoTheme
    ? (language === "vi" ? "Tự động" : "Auto")
    : draftTheme === "dark"
      ? (language === "vi" ? "Tối" : "Dark")
      : (language === "vi" ? "Sáng" : "Light");

  return (
    <section className="workspace-panel settings-panel sgx-settings-panel">
      <div className="sgx-settings-layout">
        <div className="sgx-settings-main">
          <p className="workspace-eyebrow">SETTINGS / PERSONAL</p>
      <h2>{t.settings_title}</h2>
      <p className="guide-lead">{t.settings_subtitle}</p>

      <div className="sgx-settings-summary">
        <div className="sgx-settings-avatar">
          {avatarUrl ? <img src={avatarUrl} alt="" /> : initials}
        </div>
        <div>
          <strong>{userName}</strong>
          <span>{user?.email}</span>
          <small>{language === "vi" ? "Tiếng Việt" : "English"}</small>
        </div>
      </div>

      <nav className="sgx-settings-tabs" aria-label={t.settings_title}>
        {tabs.map((tab) => (
          <button type="button" key={tab.id} className={activeTab === tab.id ? "active" : ""} onClick={() => setActiveTab(tab.id)}>
            {tab.label}
          </button>
        ))}
      </nav>

      {activeTab === "profile" && (
        <div className="sgx-settings-section">
          <div className="sgx-settings-section-heading"><h3>{t.profile_title}</h3><p>{t.profile_subtitle}</p></div>
          {profileLoading ? <div className="sgx-settings-loading">{language === "vi" ? "Đang tải..." : "Loading..."}</div> : <>
            <label className="sgx-settings-field"><span>{t.profile_avatar}</span><div className="sgx-settings-avatar-field"><div className="sgx-settings-avatar small">{avatarUrl ? <img src={avatarUrl} alt="" /> : initials}</div><input value={avatarUrl} onChange={(event) => setAvatarUrl(event.target.value)} placeholder={t.profile_avatar_hint} /></div></label>
            <label className="sgx-settings-field"><span>{t.profile_fullname}</span><input value={fullName} onChange={(event) => setFullName(event.target.value)} placeholder={t.profile_fullname_placeholder} /></label>
            <label className="sgx-settings-field"><span>{t.profile_bio}</span><textarea value={bio} onChange={(event) => setBio(event.target.value)} placeholder={t.profile_bio_placeholder} rows={4} /></label>
          </>}
        </div>
      )}

      {activeTab === "account" && (
        <div className="sgx-settings-section">
          <div className="sgx-settings-section-heading"><h3>{t.account_title}</h3><p>{t.account_subtitle}</p></div>
          <label className="sgx-settings-field"><span>{t.account_username}</span><input value={user?.username ?? ""} readOnly /></label>
          <label className="sgx-settings-field"><span>{t.account_email}</span><input value={user?.email ?? ""} readOnly /></label>
          <p className="sgx-settings-note">{t.account_readonly_hint}</p>
        </div>
      )}

      {activeTab === "appearance" && (
        <div className="sgx-settings-section">
          <div className="sgx-settings-section-heading"><h3>{t.appearance_title}</h3><p>{t.appearance_subtitle}</p></div>
          <div className="sgx-settings-field"><span>{t.appearance_theme}</span><div className="sgx-settings-choice-grid">
            <button type="button" className={!draftAutoTheme && draftTheme === "light" ? "selected" : ""} onClick={() => { setDraftAutoTheme(false); setDraftTheme("light"); }}>{t.appearance_theme_light}</button>
            <button type="button" className={!draftAutoTheme && draftTheme === "dark" ? "selected" : ""} onClick={() => { setDraftAutoTheme(false); setDraftTheme("dark"); }}>{t.appearance_theme_dark}</button>
            <button type="button" className={draftAutoTheme ? "selected" : ""} onClick={() => setDraftAutoTheme(true)}>{t.appearance_auto_theme}</button>
          </div></div>
          <label className="sgx-settings-field"><span>{t.appearance_language}<small>{t.appearance_language_hint}</small></span><select value={draftLanguage} onChange={(event) => setDraftLanguage(event.target.value as "vi" | "en")}><option value="vi">Tiếng Việt</option><option value="en">English</option></select></label>
          <label className="sgx-settings-switch"><span><b>{t.appearance_notifications}</b><small>{t.appearance_notifications_hint}</small></span><input type="checkbox" checked={notificationsEnabled} onChange={(event) => setNotificationsEnabled(event.target.checked)} /><i /></label>
        </div>
      )}

      {activeTab === "security" && (
        <div className="sgx-settings-section">
          <div className="sgx-settings-section-heading"><h3>{t.security_title}</h3><p>{t.security_subtitle}</p></div>
          <label className="sgx-settings-field"><span>{t.security_current_password}</span><div className="sgx-settings-password"><input type={showCurrent ? "text" : "password"} value={currentPassword} onChange={(event) => setCurrentPassword(event.target.value)} /><button type="button" onClick={() => setShowCurrent((value) => !value)}>{showCurrent ? "Hide" : "Show"}</button></div></label>
          <label className="sgx-settings-field"><span>{t.security_new_password}<small>{t.security_hint_length}</small></span><div className="sgx-settings-password"><input type={showNew ? "text" : "password"} value={newPassword} onChange={(event) => setNewPassword(event.target.value)} /><button type="button" onClick={() => setShowNew((value) => !value)}>{showNew ? "Hide" : "Show"}</button></div></label>
          <label className="sgx-settings-field"><span>{t.security_confirm_password}</span><div className="sgx-settings-password"><input type={showConfirm ? "text" : "password"} value={confirmPassword} onChange={(event) => setConfirmPassword(event.target.value)} /><button type="button" onClick={() => setShowConfirm((value) => !value)}>{showConfirm ? "Hide" : "Show"}</button></div></label>
        </div>
      )}

      <div className="sgx-settings-footer">
        <p className={hasUnsavedChanges ? "is-dirty" : ""} aria-live="polite">
          {hasUnsavedChanges && (language === "vi" ? "Có thay đổi chưa lưu" : "Unsaved changes")}
        </p>
        <button
          type="button"
          className={`panel-primary sgx-settings-save ${hasUnsavedChanges ? "has-changes" : ""}`}
          onClick={() => void handleSaveSettings()}
          disabled={saving || !hasUnsavedChanges}
        >
          {saving ? t.profile_saving : t.profile_save} <span>↗</span>
        </button>
      </div>
        </div>

        <aside className="sgx-settings-aside" aria-label={asideCopy.title}>
          <div className="sgx-settings-aside-card">
            <p className="sgx-settings-aside-eyebrow">{asideCopy.eyebrow}</p>
            <div className="sgx-settings-orbit" aria-hidden="true"><span>S</span><i /><i /><i /></div>
            <h3>{asideCopy.title}</h3>
            <p className="sgx-settings-aside-description">{asideCopy.description}</p>
            <div className="sgx-settings-signal-list">
              <div><span>{asideCopy.language}</span><strong>{draftLanguage === "vi" ? "Tiếng Việt" : "English"}</strong></div>
              <div><span>{asideCopy.theme}</span><strong>{themeLabel}</strong></div>
              <div><span>{asideCopy.notifications}</span><strong>{notificationsEnabled ? asideCopy.enabled : asideCopy.disabled}</strong></div>
            </div>
          </div>
          <div className="sgx-settings-aside-note"><span>✦</span><p>{asideCopy.note}</p></div>
        </aside>
      </div>
      <SlidegenConfirmDialog
        open={unsavedDialogOpen}
        onOpenChange={handleUnsavedDialogChange}
        title={unsavedCopy.title}
        description={unsavedCopy.description}
        confirmLabel={unsavedCopy.leave}
        cancelLabel={unsavedCopy.stay}
        onConfirm={leaveWithUnsavedChanges}
      />
    </section>
  );
}
