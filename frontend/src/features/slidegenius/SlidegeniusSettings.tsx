import { useEffect, useMemo, useState } from "react";
import { useAuth } from "@/contexts/AuthContext";
import { useLanguage } from "@/contexts/LanguageContext";
import { useTheme } from "@/contexts/ThemeContext";
import { api } from "@/lib/api";
import { useToast } from "@/hooks/use-toast";
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
  const [profileSaving, setProfileSaving] = useState(false);
  const [draftLanguage, setDraftLanguage] = useState(language);
  const [draftTheme, setDraftTheme] = useState<ThemeChoice>(theme);
  const [draftAutoTheme, setDraftAutoTheme] = useState(autoTheme);
  const [notificationsEnabled, setNotificationsEnabled] = useState(true);
  const [settingsSaving, setSettingsSaving] = useState(false);
  const [currentPassword, setCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [showCurrent, setShowCurrent] = useState(false);
  const [showNew, setShowNew] = useState(false);
  const [showConfirm, setShowConfirm] = useState(false);
  const [passwordSaving, setPasswordSaving] = useState(false);

  const userName = fullName || user?.full_name || user?.username || user?.email || "Slidegen user";
  const initials = useMemo(() => userName.slice(0, 2).toUpperCase(), [userName]);
  const hasAppearanceChanges = draftLanguage !== language || draftTheme !== theme || draftAutoTheme !== autoTheme;

  useEffect(() => {
    let active = true;
    Promise.all([api.getProfile(), api.getSettings()]).then(([profile, settings]) => {
      if (!active) return;
      setFullName(profile.full_name ?? "");
      setAvatarUrl(profile.avatar_url ?? "");
      setBio(profile.bio ?? "");
      if (settings?.language === "en" || settings?.language === "vi") setDraftLanguage(settings.language);
      if (settings?.theme === "light" || settings?.theme === "dark") setDraftTheme(settings.theme);
      if (settings?.theme === "system") setDraftAutoTheme(true);
      if (typeof settings?.notifications_enabled === "boolean") setNotificationsEnabled(settings.notifications_enabled);
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

  const handleSaveProfile = async () => {
    setProfileSaving(true);
    try {
      await api.updateProfile({ full_name: fullName, avatar_url: avatarUrl, bio });
      updateUser({ full_name: fullName, avatar_url: avatarUrl });
      toast({ title: t.toast_profile_success });
    } catch {
      toast({ title: t.toast_profile_error, variant: "destructive" });
    } finally {
      setProfileSaving(false);
    }
  };

  const handleSaveAppearance = async () => {
    setSettingsSaving(true);
    try {
      await api.updateSettings({
        language: draftLanguage,
        theme: draftAutoTheme ? "system" : draftTheme,
        notifications_enabled: notificationsEnabled,
      });
      setLanguage(draftLanguage);
      if (draftAutoTheme !== autoTheme) setAutoTheme(draftAutoTheme);
      if (!draftAutoTheme && draftTheme !== theme) toggleTheme();
      toast({ title: t.toast_settings_success });
    } catch {
      toast({ title: t.toast_settings_error, variant: "destructive" });
    } finally {
      setSettingsSaving(false);
    }
  };

  const handleChangePassword = async () => {
    if (newPassword.length < 6) {
      toast({ title: t.toast_password_short, variant: "destructive" });
      return;
    }
    if (newPassword !== confirmPassword) {
      toast({ title: t.toast_password_mismatch, variant: "destructive" });
      return;
    }
    setPasswordSaving(true);
    try {
      await api.changePassword(currentPassword, newPassword);
      setCurrentPassword("");
      setNewPassword("");
      setConfirmPassword("");
      toast({ title: t.toast_password_success });
    } catch {
      toast({ title: t.toast_password_error, variant: "destructive" });
    } finally {
      setPasswordSaving(false);
    }
  };

  const tabs: Array<{ id: SettingsTab; label: string }> = [
    { id: "profile", label: t.tab_profile },
    { id: "account", label: t.tab_account },
    { id: "appearance", label: t.tab_appearance },
    { id: "security", label: t.tab_security },
  ];

  return (
    <section className="workspace-panel settings-panel sgx-settings-panel">
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
            <button type="button" className="panel-primary sgx-settings-save" onClick={handleSaveProfile} disabled={profileSaving}>{profileSaving ? t.profile_saving : t.profile_save} <span>↗</span></button>
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
          <button type="button" className={`panel-primary sgx-settings-save ${hasAppearanceChanges ? "has-changes" : ""}`} onClick={handleSaveAppearance} disabled={settingsSaving}>{settingsSaving ? t.appearance_saving : t.appearance_save} <span>↗</span></button>
        </div>
      )}

      {activeTab === "security" && (
        <div className="sgx-settings-section">
          <div className="sgx-settings-section-heading"><h3>{t.security_title}</h3><p>{t.security_subtitle}</p></div>
          <label className="sgx-settings-field"><span>{t.security_current_password}</span><div className="sgx-settings-password"><input type={showCurrent ? "text" : "password"} value={currentPassword} onChange={(event) => setCurrentPassword(event.target.value)} /><button type="button" onClick={() => setShowCurrent((value) => !value)}>{showCurrent ? "Hide" : "Show"}</button></div></label>
          <label className="sgx-settings-field"><span>{t.security_new_password}<small>{t.security_hint_length}</small></span><div className="sgx-settings-password"><input type={showNew ? "text" : "password"} value={newPassword} onChange={(event) => setNewPassword(event.target.value)} /><button type="button" onClick={() => setShowNew((value) => !value)}>{showNew ? "Hide" : "Show"}</button></div></label>
          <label className="sgx-settings-field"><span>{t.security_confirm_password}</span><div className="sgx-settings-password"><input type={showConfirm ? "text" : "password"} value={confirmPassword} onChange={(event) => setConfirmPassword(event.target.value)} /><button type="button" onClick={() => setShowConfirm((value) => !value)}>{showConfirm ? "Hide" : "Show"}</button></div></label>
          <button type="button" className="panel-primary sgx-settings-save" onClick={handleChangePassword} disabled={passwordSaving || !currentPassword || !newPassword || !confirmPassword}>{passwordSaving ? t.security_changing : t.security_change} <span>↗</span></button>
        </div>
      )}
    </section>
  );
}
