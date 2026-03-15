import { useState } from "react";
import { Link, useNavigate, useLocation, Navigate } from "react-router-dom";
import { Mail, Lock, Eye, EyeOff, ArrowLeft } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Checkbox } from "@/components/ui/checkbox";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { useToast } from "@/hooks/use-toast";
import { useAuth } from "@/contexts/AuthContext";
import { ThemeToggle } from "@/components/ThemeToggle";
import { LanguageToggle } from "@/components/LanguageToggle";
import { useLanguage } from "@/contexts/LanguageContext";

const Login = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { login, isAuthenticated, isLoading } = useAuth();
  const { toast } = useToast();
  const { t } = useLanguage();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [remember, setRemember] = useState(false);
  const [loading, setLoading] = useState(false);

  const from = (location.state as any)?.from?.pathname || "/slidegen";

  // Redirect nếu đã authenticated (xử lý race condition sau login)
  if (!isLoading && isAuthenticated) {
    return <Navigate to={from} replace />;
  }

  const performLogin = async () => {
    if (loading) return;
    setLoading(true);
    try {
      await login(email, password, remember);
      toast({ title: t.login_toast_success });
      navigate(from, { replace: true });
    } catch (err: any) {
      toast({ title: t.login_toast_error, variant: "destructive" });
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    performLogin();
  };

  return (
    <div className="flex min-h-screen items-center justify-center px-4">
      <div className="absolute inset-0 gradient-primary opacity-5" />
      <div className="absolute top-4 left-4">
        <Button variant="ghost" size="icon" onClick={() => navigate("/")}>
          <ArrowLeft className="h-5 w-5" />
        </Button>
      </div>
      <div className="absolute top-4 right-4 flex items-center gap-2">
        <LanguageToggle />
        <ThemeToggle />
      </div>
      <Card className="w-full max-w-md glass animate-scale-in">
        <CardHeader className="text-center">
          <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-xl gradient-primary">
            <span className="text-lg font-bold text-primary-foreground">S</span>
          </div>
          <CardTitle className="text-2xl">{t.login_title}</CardTitle>
          <CardDescription>{t.login_subtitle}</CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="email">{t.login_email}</Label>
              <div className="relative">
                <Mail className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                <Input id="email" type="email" placeholder={t.login_placeholder_email} className="pl-9" value={email} onChange={(e) => setEmail(e.target.value)} required />
              </div>
            </div>
            <div className="space-y-2">
              <Label htmlFor="password">{t.login_password}</Label>
              <div className="relative">
                <Lock className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                <Input id="password" type={showPassword ? "text" : "password"} placeholder={t.login_placeholder_password} className="pl-9 pr-9" value={password} onChange={(e) => setPassword(e.target.value)} onKeyDown={(e) => e.key === "Enter" && performLogin()} required />
                <button type="button" className="absolute right-3 top-3 text-muted-foreground hover:text-foreground" onClick={() => setShowPassword(!showPassword)}>
                  {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                </button>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <Checkbox id="remember" checked={remember} onCheckedChange={(c) => setRemember(c === true)} />
              <Label htmlFor="remember" className="text-sm">{t.login_remember}</Label>
            </div>
            <Button type="submit" className="w-full gradient-primary text-primary-foreground" disabled={loading}>
              {loading ? t.login_signing_in : t.login_sign_in}
            </Button>
          </form>
          <p className="mt-4 text-center text-sm text-muted-foreground">
            {t.login_no_account} <Link to="/register" className="text-primary hover:underline">{t.login_register}</Link>
          </p>
        </CardContent>
      </Card>
    </div>
  );
};

export default Login;
