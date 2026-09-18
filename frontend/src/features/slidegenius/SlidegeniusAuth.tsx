import { FormEvent, useEffect, useState } from "react";
import { Link, Navigate, useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "@/contexts/AuthContext";
import { useLanguage } from "@/contexts/LanguageContext";
import { useToast } from "@/hooks/use-toast";
import { api } from "@/lib/api";
import "./slidegenius.css";

type AuthMode = "signin" | "signup";

const copy = {
  en: {
    signin: { eyebrow: "WELCOME BACK", title: "Continue the work worth sharing.", description: "Sign in to pick up your ideas right where you left them.", primary: "Sign in", switchText: "New to Slidegen?", switchAction: "Create an account" },
    signup: { eyebrow: "START CREATING", title: "Make room for better ideas.", description: "Create your Slidegen account and turn rough thoughts into work people remember.", primary: "Create account", switchText: "Already have an account?", switchAction: "Sign in" },
    name: "Full name", email: "Work email", password: "Password", namePlaceholder: "Your name", emailPlaceholder: "you@company.com", passwordPlaceholder: "At least 6 characters", terms: "I agree to the Terms and Privacy Policy.", forgot: "Forgot password?", or: "or continue with", google: "Continue with Google", required: "Please complete the required fields.", invalid: "Please enter a valid name, email and password.", language: "Switch language", back: "Back to home", signInError: "Unable to sign in. Please check your details.", signUpError: "Unable to create your account. Please try again.",
  },
  vi: {
    signin: { eyebrow: "CHÀO MỪNG TRỞ LẠI", title: "Tiếp tục công việc đáng chia sẻ.", description: "Đăng nhập để tiếp tục ý tưởng đang còn dang dở.", primary: "Đăng nhập", switchText: "Mới dùng Slidegen?", switchAction: "Tạo tài khoản" },
    signup: { eyebrow: "BẮT ĐẦU SÁNG TẠO", title: "Dành chỗ cho những ý tưởng tốt hơn.", description: "Tạo tài khoản Slidegen và biến suy nghĩ thô thành sản phẩm đáng nhớ.", primary: "Tạo tài khoản", switchText: "Đã có tài khoản?", switchAction: "Đăng nhập" },
    name: "Họ và tên", email: "Email công việc", password: "Mật khẩu", namePlaceholder: "Tên của bạn", emailPlaceholder: "ban@congty.com", passwordPlaceholder: "Tối thiểu 6 ký tự", terms: "Tôi đồng ý với Điều khoản và Chính sách bảo mật.", forgot: "Quên mật khẩu?", or: "hoặc tiếp tục với", google: "Tiếp tục với Google", required: "Vui lòng điền đủ các trường bắt buộc.", invalid: "Vui lòng nhập đúng họ tên, email và mật khẩu.", language: "Đổi ngôn ngữ", back: "Về trang chủ", signInError: "Không thể đăng nhập. Hãy kiểm tra lại thông tin.", signUpError: "Không thể tạo tài khoản. Vui lòng thử lại.",
  },
} as const;

export default function SlidegeniusAuth({ mode }: { mode: AuthMode }) {
  const navigate = useNavigate();
  const location = useLocation();
  const { login, loginWithAccessToken, register, isAuthenticated, isLoading } = useAuth();
  const { language, setLanguage } = useLanguage();
  const { toast } = useToast();
  const t = copy[language];
  const content = t[mode];
  const isSignup = mode === "signup";
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [remember, setRemember] = useState(false);
  const [terms, setTerms] = useState(false);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [googleLoading, setGoogleLoading] = useState(false);
  const from = (location.state as { from?: { pathname?: string } } | null)?.from?.pathname || "/home";

  useEffect(() => {
    const params = new URLSearchParams(window.location.hash.replace(/^#/, ""));
    const googleToken = params.get("google_token");
    const googleError = params.get("google_error");
    if (!googleToken && !googleError) return;
    window.history.replaceState({}, document.title, `${window.location.pathname}${window.location.search}`);

    if (googleError) {
      const message = googleError === "not_configured"
        ? (language === "vi" ? "Đăng nhập Google chưa được cấu hình trên máy chủ." : "Google sign-in is not configured on the server.")
        : (language === "vi" ? "Đăng nhập Google chưa được hoàn tất." : "Google sign-in was not completed.");
      setError(message);
      return;
    }
    if (!googleToken) return;

    setGoogleLoading(true);
    void loginWithAccessToken(googleToken).then(() => {
      toast({ title: language === "en" ? "Signed in with Google" : "Đăng nhập Google thành công" });
      navigate(from, { replace: true });
    }).catch(() => {
      setError(language === "vi" ? "Không thể đăng nhập bằng Google." : "Unable to sign in with Google.");
    }).finally(() => setGoogleLoading(false));
  }, [from, language, loginWithAccessToken, navigate, toast]);

  if (!isLoading && isAuthenticated) return <Navigate to="/home" replace />;

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (loading) return;
    if ((isSignup && fullName.trim().length < 3) || !email.trim() || password.length < 6 || (isSignup && !terms)) {
      setError(t.invalid);
      return;
    }
    setError("");
    setLoading(true);
    try {
      if (isSignup) {
        await register(fullName.trim(), email.trim(), password);
        toast({ title: language === "en" ? "Account created" : "Tạo tài khoản thành công" });
        navigate("/home", { replace: true });
      } else {
        await login(email.trim(), password, remember);
        toast({ title: language === "en" ? "Signed in" : "Đăng nhập thành công" });
        navigate(from, { replace: true });
      }
    } catch {
      setError(isSignup ? t.signUpError : t.signInError);
      toast({ title: isSignup ? t.signUpError : t.signInError, variant: "destructive" });
    } finally {
      setLoading(false);
    }
  };

  const handleGoogleLogin = () => {
    if (loading || googleLoading) return;
    setError("");
    setGoogleLoading(true);
    window.location.assign(api.googleLoginUrl());
  };

  return (
    <main className="sg-auth auth-page">
      <div className="auth-atmosphere" aria-hidden="true"><span /><span /><span /></div>
      <header className="auth-header"><Link className="brand" to="/" aria-label="Slidegen home"><span className="brand-word"><span>slide</span><b>gen</b></span></Link><div className="auth-header-actions"><button className="auth-language" type="button" onClick={() => setLanguage(language === "en" ? "vi" : "en")} aria-label={t.language}>{language === "en" ? "VI" : "EN"} <span>↗</span></button><Link to="/">{t.back}</Link></div></header>
      <section className={`auth-shell ${isSignup ? "auth-shell-signup" : "auth-shell-signin"}`} aria-labelledby="auth-title">
        <div className="auth-intro"><p className="auth-eyebrow">{content.eyebrow}</p><h1 id="auth-title">{content.title}</h1><p className="auth-description">{content.description}</p><div className="auth-note"><span className="auth-note-line" /><span>{isSignup ? "01 / CREATIVE WORKSPACE" : "02 / YOUR WORKSPACE"}</span></div></div>
        <div className="auth-card"><div className="auth-card-heading"><span>{isSignup ? "CREATE ACCOUNT" : "SIGN IN"}</span><span>SLIDEGEN / {isSignup ? "01" : "02"}</span></div><form onSubmit={handleSubmit}>{isSignup && <label>{t.name}<input name="name" type="text" placeholder={t.namePlaceholder} value={fullName} onChange={(event) => setFullName(event.target.value)} required /></label>}<label>{t.email}<input name="email" type="email" placeholder={t.emailPlaceholder} value={email} onChange={(event) => setEmail(event.target.value)} required /></label><label>{t.password}<input name="password" type="password" placeholder={t.passwordPlaceholder} minLength={6} value={password} onChange={(event) => setPassword(event.target.value)} required /></label>{!isSignup && <><a className="auth-forgot" href="#forgot">{t.forgot}</a><label className="auth-check"><input type="checkbox" checked={remember} onChange={(event) => setRemember(event.target.checked)} /><span>Remember me</span></label></>}{isSignup && <label className="auth-check"><input type="checkbox" checked={terms} onChange={(event) => setTerms(event.target.checked)} required /><span>{t.terms}</span></label>}{error && <p className="auth-error" role="alert">{error || t.required}</p>}<button className="auth-submit" type="submit" disabled={loading || googleLoading}>{loading ? "..." : content.primary}<span>↗</span></button></form><div className="auth-divider"><span>{t.or}</span></div><button className="auth-social" type="button" onClick={handleGoogleLogin} disabled={loading || googleLoading}><span className="google-mark">G</span>{googleLoading ? "..." : t.google}</button><p className="auth-switch">{content.switchText} <Link to={isSignup ? "/login" : "/register"}>{content.switchAction} <span>↗</span></Link></p></div>
      </section>
      <footer className="auth-footer"><span>© 2026 Slidegen</span><span>Ideas into slides.</span></footer>
    </main>
  );
}
