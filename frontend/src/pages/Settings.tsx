import { useState, useEffect } from "react";
import {
  User,
  Mail,
  Lock,
  Eye,
  EyeOff,
  Globe,
  Bell,
  Sun,
  Moon,
  Save,
  ShieldCheck,
  Palette,
  UserCircle,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Switch } from "@/components/ui/switch";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Separator } from "@/components/ui/separator";
import { useToast } from "@/hooks/use-toast";
import { useAuth } from "@/contexts/AuthContext";
import { useTheme } from "@/contexts/ThemeContext";
import { useLanguage } from "@/contexts/LanguageContext";
import { api } from "@/lib/api";
import { AppLayout } from "@/components/AppLayout";

const Settings = () => {
  const { user } = useAuth();
  const { theme, toggleTheme } = useTheme();
  const { language, setLanguage, t } = useLanguage();
  const { toast } = useToast();

  // Profile state
  const [fullName, setFullName] = useState("");
  const [avatarUrl, setAvatarUrl] = useState("");
  const [bio, setBio] = useState("");
  const [profileLoading, setProfileLoading] = useState(false);
  const [profileInitLoading, setProfileInitLoading] = useState(true);

  // Settings state
  const [notificationsEnabled, setNotificationsEnabled] = useState(true);
  const [settingsLoading, setSettingsLoading] = useState(false);

  // Password state
  const [currentPassword, setCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [showCurrent, setShowCurrent] = useState(false);
  const [showNew, setShowNew] = useState(false);
  const [showConfirm, setShowConfirm] = useState(false);
  const [passwordLoading, setPasswordLoading] = useState(false);

  useEffect(() => {
    const loadData = async () => {
      try {
        const [profile, settings] = await Promise.all([
          api.getProfile(),
          api.getSettings(),
        ]);
        setFullName(profile.full_name ?? "");
        setAvatarUrl(profile.avatar_url ?? "");
        setBio(profile.bio ?? "");
        setNotificationsEnabled(settings.notifications_enabled ?? true);
      } catch {
        // Use defaults if API fails
      } finally {
        setProfileInitLoading(false);
      }
    };
    loadData();
  }, []);

  const handleSaveProfile = async () => {
    setProfileLoading(true);
    try {
      await api.updateProfile({ full_name: fullName, avatar_url: avatarUrl, bio });
      toast({ title: t.toast_profile_success });
    } catch (err: any) {
      toast({ title: t.toast_profile_error, description: err.message, variant: "destructive" });
    } finally {
      setProfileLoading(false);
    }
  };

  const handleSaveSettings = async () => {
    setSettingsLoading(true);
    try {
      await api.updateSettings({ language, notifications_enabled: notificationsEnabled, theme });
      toast({ title: t.toast_settings_success });
    } catch (err: any) {
      toast({ title: t.toast_settings_error, description: err.message, variant: "destructive" });
    } finally {
      setSettingsLoading(false);
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
    setPasswordLoading(true);
    try {
      await api.changePassword(currentPassword, newPassword);
      toast({ title: t.toast_password_success });
      setCurrentPassword("");
      setNewPassword("");
      setConfirmPassword("");
    } catch (err: any) {
      toast({ title: t.toast_password_error, description: err.message, variant: "destructive" });
    } finally {
      setPasswordLoading(false);
    }
  };

  const initials = user?.username?.slice(0, 2).toUpperCase() ?? "U";

  return (
    <AppLayout>
      <div className="max-w-4xl mx-auto px-4 py-8">
        {/* Page title */}
        <div className="mb-6">
          <h1 className="text-2xl font-semibold">{t.settings_title}</h1>
          <p className="text-sm text-muted-foreground mt-1">{t.settings_subtitle}</p>
        </div>
        {/* User summary card */}
        <Card className="mb-6">
          <CardContent className="flex items-center gap-4 pt-5 pb-5">
            <Avatar className="h-16 w-16 ring-2 ring-primary/20">
              <AvatarImage src={avatarUrl || undefined} />
              <AvatarFallback className="gradient-primary text-primary-foreground text-lg font-bold">
                {initials}
              </AvatarFallback>
            </Avatar>
            <div>
              <p className="font-semibold text-base">{fullName || user?.username}</p>
              <p className="text-sm text-muted-foreground">{user?.email}</p>
              <div className="flex items-center gap-1 mt-1">
                <Globe className="h-3 w-3 text-muted-foreground" />
                <span className="text-xs text-muted-foreground">
                  {language === "vi" ? "Tiếng Việt" : "English"}
                </span>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Tabs */}
        <Tabs defaultValue="profile">
          <TabsList className="mb-6 grid w-full grid-cols-4">
            <TabsTrigger value="profile" className="gap-1.5">
              <UserCircle className="h-4 w-4" />
              <span className="hidden sm:inline">{t.tab_profile}</span>
            </TabsTrigger>
            <TabsTrigger value="account" className="gap-1.5">
              <User className="h-4 w-4" />
              <span className="hidden sm:inline">{t.tab_account}</span>
            </TabsTrigger>
            <TabsTrigger value="appearance" className="gap-1.5">
              <Palette className="h-4 w-4" />
              <span className="hidden sm:inline">{t.tab_appearance}</span>
            </TabsTrigger>
            <TabsTrigger value="security" className="gap-1.5">
              <ShieldCheck className="h-4 w-4" />
              <span className="hidden sm:inline">{t.tab_security}</span>
            </TabsTrigger>
          </TabsList>

          {/* Profile Tab */}
          <TabsContent value="profile">
            <Card>
              <CardHeader>
                <CardTitle>{t.profile_title}</CardTitle>
                <CardDescription>{t.profile_subtitle}</CardDescription>
              </CardHeader>
              <CardContent className="space-y-5">
                {profileInitLoading ? (
                  <div className="flex justify-center py-8">
                    <div className="h-6 w-6 animate-spin rounded-full border-4 border-primary border-t-transparent" />
                  </div>
                ) : (
                  <>
                    <div className="space-y-2">
                      <Label htmlFor="avatar">{t.profile_avatar}</Label>
                      <div className="flex items-center gap-3">
                        <Avatar className="h-10 w-10 shrink-0">
                          <AvatarImage src={avatarUrl || undefined} />
                          <AvatarFallback className="gradient-primary text-primary-foreground text-sm font-bold">
                            {initials}
                          </AvatarFallback>
                        </Avatar>
                        <Input
                          id="avatar"
                          placeholder={t.profile_avatar_hint}
                          value={avatarUrl}
                          onChange={(e) => setAvatarUrl(e.target.value)}
                        />
                      </div>
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="fullname">{t.profile_fullname}</Label>
                      <div className="relative">
                        <User className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                        <Input
                          id="fullname"
                          className="pl-9"
                          placeholder={t.profile_fullname_placeholder}
                          value={fullName}
                          onChange={(e) => setFullName(e.target.value)}
                        />
                      </div>
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="bio">{t.profile_bio}</Label>
                      <Textarea
                        id="bio"
                        placeholder={t.profile_bio_placeholder}
                        value={bio}
                        onChange={(e) => setBio(e.target.value)}
                        rows={3}
                        className="resize-none"
                      />
                    </div>

                    <Button
                      className="w-full gradient-primary text-primary-foreground"
                      onClick={handleSaveProfile}
                      disabled={profileLoading}
                    >
                      <Save className="h-4 w-4 mr-2" />
                      {profileLoading ? t.profile_saving : t.profile_save}
                    </Button>
                  </>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          {/* Account Tab */}
          <TabsContent value="account">
            <Card>
              <CardHeader>
                <CardTitle>{t.account_title}</CardTitle>
                <CardDescription>{t.account_subtitle}</CardDescription>
              </CardHeader>
              <CardContent className="space-y-5">
                <div className="space-y-2">
                  <Label htmlFor="username">{t.account_username}</Label>
                  <div className="relative">
                    <User className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                    <Input
                      id="username"
                      className="pl-9 bg-muted cursor-not-allowed"
                      value={user?.username ?? ""}
                      readOnly
                    />
                  </div>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="email">{t.account_email}</Label>
                  <div className="relative">
                    <Mail className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                    <Input
                      id="email"
                      className="pl-9 bg-muted cursor-not-allowed"
                      value={user?.email ?? ""}
                      readOnly
                    />
                  </div>
                </div>

                <div className="flex items-center gap-2 rounded-lg border border-dashed p-3 text-sm text-muted-foreground">
                  <ShieldCheck className="h-4 w-4 shrink-0" />
                  {t.account_readonly_hint}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Appearance Tab */}
          <TabsContent value="appearance">
            <Card>
              <CardHeader>
                <CardTitle>{t.appearance_title}</CardTitle>
                <CardDescription>{t.appearance_subtitle}</CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                {/* Theme */}
                <div className="space-y-3">
                  <Label>{t.appearance_theme}</Label>
                  <div className="grid grid-cols-2 gap-3">
                    <button
                      onClick={() => theme === "dark" && toggleTheme()}
                      className={`flex items-center justify-center gap-2 rounded-lg border p-4 text-sm font-medium transition-all ${
                        theme === "light"
                          ? "border-primary bg-primary/10 text-primary"
                          : "border-border hover:border-border/80 hover:bg-muted"
                      }`}
                    >
                      <Sun className="h-4 w-4" />
                      {t.appearance_theme_light}
                    </button>
                    <button
                      onClick={() => theme === "light" && toggleTheme()}
                      className={`flex items-center justify-center gap-2 rounded-lg border p-4 text-sm font-medium transition-all ${
                        theme === "dark"
                          ? "border-primary bg-primary/10 text-primary"
                          : "border-border hover:border-border/80 hover:bg-muted"
                      }`}
                    >
                      <Moon className="h-4 w-4" />
                      {t.appearance_theme_dark}
                    </button>
                  </div>
                </div>

                <Separator />

                {/* Language */}
                <div className="space-y-3">
                  <div>
                    <Label>{t.appearance_language}</Label>
                    <p className="text-xs text-muted-foreground mt-0.5">{t.appearance_language_hint}</p>
                  </div>
                  <div className="grid grid-cols-2 gap-3">
                    <button
                      onClick={() => setLanguage("vi")}
                      className={`flex items-center justify-center gap-2 rounded-lg border p-4 text-sm font-medium transition-all ${
                        language === "vi"
                          ? "border-primary bg-primary/10 text-primary"
                          : "border-border hover:border-border/80 hover:bg-muted"
                      }`}
                    >
                      <span className="text-base">🇻🇳</span>
                      Tiếng Việt
                    </button>
                    <button
                      onClick={() => setLanguage("en")}
                      className={`flex items-center justify-center gap-2 rounded-lg border p-4 text-sm font-medium transition-all ${
                        language === "en"
                          ? "border-primary bg-primary/10 text-primary"
                          : "border-border hover:border-border/80 hover:bg-muted"
                      }`}
                    >
                      <span className="text-base">🇺🇸</span>
                      English
                    </button>
                  </div>
                </div>

                <Separator />

                {/* Notifications */}
                <div className="flex items-center justify-between">
                  <div className="space-y-0.5">
                    <div className="flex items-center gap-2">
                      <Bell className="h-4 w-4 text-muted-foreground" />
                      <Label className="text-sm font-medium cursor-pointer">{t.appearance_notifications}</Label>
                    </div>
                    <p className="text-xs text-muted-foreground pl-6">{t.appearance_notifications_hint}</p>
                  </div>
                  <Switch
                    checked={notificationsEnabled}
                    onCheckedChange={setNotificationsEnabled}
                  />
                </div>

                <Button
                  className="w-full gradient-primary text-primary-foreground"
                  onClick={handleSaveSettings}
                  disabled={settingsLoading}
                >
                  <Save className="h-4 w-4 mr-2" />
                  {settingsLoading ? t.appearance_saving : t.appearance_save}
                </Button>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Security Tab */}
          <TabsContent value="security">
            <Card>
              <CardHeader>
                <CardTitle>{t.security_title}</CardTitle>
                <CardDescription>{t.security_subtitle}</CardDescription>
              </CardHeader>
              <CardContent className="space-y-5">
                <div className="space-y-2">
                  <Label htmlFor="current-password">{t.security_current_password}</Label>
                  <div className="relative">
                    <Lock className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                    <Input
                      id="current-password"
                      type={showCurrent ? "text" : "password"}
                      className="pl-9 pr-9"
                      value={currentPassword}
                      onChange={(e) => setCurrentPassword(e.target.value)}
                    />
                    <button
                      type="button"
                      className="absolute right-3 top-3 text-muted-foreground hover:text-foreground"
                      onClick={() => setShowCurrent(!showCurrent)}
                    >
                      {showCurrent ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                    </button>
                  </div>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="new-password">{t.security_new_password}</Label>
                  <div className="relative">
                    <Lock className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                    <Input
                      id="new-password"
                      type={showNew ? "text" : "password"}
                      className="pl-9 pr-9"
                      value={newPassword}
                      onChange={(e) => setNewPassword(e.target.value)}
                    />
                    <button
                      type="button"
                      className="absolute right-3 top-3 text-muted-foreground hover:text-foreground"
                      onClick={() => setShowNew(!showNew)}
                    >
                      {showNew ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                    </button>
                  </div>
                  {newPassword.length > 0 && newPassword.length < 6 && (
                    <p className="text-xs text-destructive">{t.security_hint_length}</p>
                  )}
                </div>

                <div className="space-y-2">
                  <Label htmlFor="confirm-password">{t.security_confirm_password}</Label>
                  <div className="relative">
                    <Lock className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                    <Input
                      id="confirm-password"
                      type={showConfirm ? "text" : "password"}
                      className="pl-9 pr-9"
                      value={confirmPassword}
                      onChange={(e) => setConfirmPassword(e.target.value)}
                    />
                    <button
                      type="button"
                      className="absolute right-3 top-3 text-muted-foreground hover:text-foreground"
                      onClick={() => setShowConfirm(!showConfirm)}
                    >
                      {showConfirm ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                    </button>
                  </div>
                  {confirmPassword.length > 0 && confirmPassword !== newPassword && (
                    <p className="text-xs text-destructive">{t.security_hint_match}</p>
                  )}
                </div>

                <Button
                  className="w-full gradient-primary text-primary-foreground"
                  onClick={handleChangePassword}
                  disabled={passwordLoading || !currentPassword || !newPassword || !confirmPassword}
                >
                  <ShieldCheck className="h-4 w-4 mr-2" />
                  {passwordLoading ? t.security_changing : t.security_change}
                </Button>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </AppLayout>
  );
};

export default Settings;
