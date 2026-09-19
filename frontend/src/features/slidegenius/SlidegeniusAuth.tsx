import { FormEvent, useEffect, useState } from "react";
import { Link, Navigate, useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "@/contexts/AuthContext";
import { useLanguage } from "@/contexts/LanguageContext";
import { useToast } from "@/hooks/use-toast";
import SlidegenLogo from "@/components/SlidegenLogo";
import { api, type EmailVerificationChallenge } from "@/lib/api";
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
  const { login, loginWithAccessToken, register, verifyEmailCode, resendEmailCode, isAuthenticated, isLoading } = useAuth();
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
  const [verificationChallenge, setVerificationChallenge] = useState<EmailVerificationChallenge | null>(null);
  const [verificationCode, setVerificationCode] = useState("");
  const [verificationLoading, setVerificationLoading] = useState(false);
  const [resendLoading, setResendLoading] = useState(false);
  const from = (location.state as { from?: { pathname?: string } } | null)?.from?.pathname || "/home";

  useEffect(() => {
    const prefilledEmail = new URLSearchParams(location.search).get("email")?.trim();
    if (prefilledEmail) setEmail(prefilledEmail);
  }, [location.search]);

  const verificationText = language === "vi"
    ? {
      eyebrow: "XÁC THỰC EMAIL",
      title: "Xác thực email của bạn.",
      description: "Nhập mã 6 số chúng tôi vừa gửi để hoàn tất đăng ký.",
      code: "Mã xác thực",
      placeholder: "000000",
      verify: "Xác thực và tiếp tục",
      resend: "Gửi lại mã",
      sent: "Mã xác thực đã được gửi.",
      verified: "Xác thực thành công",
      invalid: "Vui lòng nhập mã xác thực 6 số.",
      back: "Dùng email khác",
    }
    : {
      eyebrow: "VERIFY YOUR EMAIL",
      title: "Verify your email.",
      description: "Enter the 6-digit code we sent to finish creating your account.",
      code: "Verification code",
      placeholder: "000000",
      verify: "Verify and continue",
      resend: "Resend code",
      sent: "A verification code was sent.",
      verified: "Email verified",
      invalid: "Enter the 6-digit verification code.",
      back: "Use another email",
    };

  const verificationSpamHint = language === "vi"
    ? "Nếu chưa thấy mã sau vài phút, hãy kiểm tra Spam/Thư rác hoặc Quảng cáo, rồi chọn “Không phải thư rác”."
    : "If the code does not arrive within a few minutes, check Spam or Promotions and mark the email as Not spam.";
  const verificationSpamLabel = language === "vi" ? "Lưu ý" : "Heads up";

  useEffect(() => {
    const params = new URLSearchParams(window.location.hash.replace(/^#/, ""));
    const googleToken = params.get("google_token");
    const googleError = params.get("google_error");
    if (!googleToken && !googleError) return;
    window.history.replaceState({}, document.title, `${window.location.pathname}${window.location.search}`);

    if (googleError) {
      const message = googleError === "not_configured"
        ? (language === "vi" ? "Đăng nhập Google chưa được cấu hình trên máy chủ." : "Google sign-in is not configured on the server.")
        : googleError === "email_not_verified"
          ? (language === "vi" ? "Google chưa xác minh địa chỉ email này." : "Google has not verified this email address.")
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
        const authResult = await register(fullName.trim(), email.trim(), password);
        if ("access_token" in authResult) {
          await loginWithAccessToken(authResult.access_token);
          toast({ title: language === "en" ? "Account created" : "Tạo tài khoản thành công" });
          navigate(from, { replace: true });
          return;
        }
        setVerificationChallenge(authResult);
        setVerificationCode("");
        toast({ title: verificationText.sent });
        return;
      } else {
        const authResult = await login(email.trim(), password, remember);
        if ("access_token" in authResult) {
          await loginWithAccessToken(authResult.access_token);
          toast({ title: language === "en" ? "Signed in" : "Đăng nhập thành công" });
          navigate(from, { replace: true });
          return;
        }
        setVerificationChallenge(authResult);
        setVerificationCode("");
        toast({ title: verificationText.sent });
        return;
      }
    } catch (submitError) {
      const fallback = isSignup ? t.signUpError : t.signInError;
      const reason = submitError instanceof Error && submitError.message.trim()
        ? submitError.message.trim()
        : fallback;
      setError(reason);
      toast({ title: reason, variant: "destructive" });
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

  const handleVerifyCode = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!verificationChallenge || verificationLoading) return;
    if (!/^\d{6}$/.test(verificationCode.trim())) {
      setError(verificationText.invalid);
      return;
    }

    setError("");
    setVerificationLoading(true);
    try {
      await verifyEmailCode(verificationChallenge.challenge_id, verificationCode.trim());
      toast({ title: verificationText.verified });
      navigate(from, { replace: true });
    } catch (verifyError) {
      const reason = verifyError instanceof Error && verifyError.message.trim()
        ? verifyError.message.trim()
        : verificationText.invalid;
      setError(reason);
    } finally {
      setVerificationLoading(false);
    }
  };

  const handleResendCode = async () => {
    if (!verificationChallenge || resendLoading) return;
    setError("");
    setResendLoading(true);
    try {
      const challenge = await resendEmailCode(verificationChallenge.challenge_id);
      setVerificationChallenge(challenge);
      toast({ title: verificationText.sent });
    } catch (resendError) {
      const reason = resendError instanceof Error && resendError.message.trim()
        ? resendError.message.trim()
        : verificationText.invalid;
      setError(reason);
    } finally {
      setResendLoading(false);
    }
  };

  if (verificationChallenge) {
    return (
      <main className="sg-auth auth-page">
        <div className="auth-atmosphere" aria-hidden="true"><span /><span /><span /></div>
        <header className="auth-header"><Link className="brand" to="/" aria-label="Slidegen home"><SlidegenLogo /></Link><div className="auth-header-actions"><button className="auth-language" type="button" onClick={() => setLanguage(language === "en" ? "vi" : "en")} aria-label={t.language}>{language === "en" ? "VI" : "EN"} <span>↗</span></button><Link to="/">{t.back}</Link></div></header>
        <section className="auth-shell auth-shell-signin" aria-labelledby="verification-title">
          <div className="auth-intro"><p className="auth-eyebrow">{verificationText.eyebrow}</p><h1 id="verification-title">{verificationText.title}</h1><p className="auth-description">{verificationText.description}</p><div className="auth-verification-alert" role="note"><span className="auth-verification-alert-icon" aria-hidden="true">!</span><div><strong>{verificationSpamLabel}</strong><p>{verificationSpamHint}</p></div></div><div className="auth-note"><span className="auth-note-line" /><span>{verificationChallenge.email}</span></div></div>
          <div className="auth-card"><div className="auth-card-heading"><span>{verificationText.eyebrow}</span><span>SLIDEGEN / CODE</span></div><form onSubmit={handleVerifyCode}><label>{verificationText.code}<input autoFocus name="verification-code" type="text" inputMode="numeric" autoComplete="one-time-code" pattern="[0-9]{6}" maxLength={6} placeholder={verificationText.placeholder} value={verificationCode} onChange={(event) => setVerificationCode(event.target.value.replace(/\D/g, "").slice(0, 6))} required /></label>{error && <p className="auth-error" role="alert">{error}</p>}<button className="auth-submit" type="submit" disabled={verificationLoading || resendLoading}>{verificationLoading ? "..." : verificationText.verify}<span>↗</span></button></form><div className="auth-code-actions"><button type="button" onClick={() => void handleResendCode()} disabled={resendLoading || verificationLoading}>{resendLoading ? "..." : verificationText.resend}</button><button type="button" onClick={() => { setVerificationChallenge(null); setVerificationCode(""); setError(""); }}>{verificationText.back}</button></div></div>
        </section>
        <footer className="auth-footer"><span>© 2026 Slidegen</span><span>Ideas into slides.</span></footer>
      </main>
    );
  }

  return (
    <main className="sg-auth auth-page">
      <div className="auth-atmosphere" aria-hidden="true"><span /><span /><span /></div>
      <header className="auth-header"><Link className="brand" to="/" aria-label="Slidegen home"><SlidegenLogo /></Link><div className="auth-header-actions"><button className="auth-language" type="button" onClick={() => setLanguage(language === "en" ? "vi" : "en")} aria-label={t.language}>{language === "en" ? "VI" : "EN"} <span>↗</span></button><Link to="/">{t.back}</Link></div></header>
      <section className={`auth-shell ${isSignup ? "auth-shell-signup" : "auth-shell-signin"}`} aria-labelledby="auth-title">
        <div className="auth-intro"><p className="auth-eyebrow">{content.eyebrow}</p><h1 id="auth-title">{content.title}</h1><p className="auth-description">{content.description}</p><div className="auth-note"><span className="auth-note-line" /><span>{isSignup ? "01 / CREATIVE WORKSPACE" : "02 / YOUR WORKSPACE"}</span></div></div>
        <div className="auth-card"><div className="auth-card-heading"><span>{isSignup ? "CREATE ACCOUNT" : "SIGN IN"}</span><span>SLIDEGEN / {isSignup ? "01" : "02"}</span></div><form onSubmit={handleSubmit}>{isSignup && <label>{t.name}<input name="name" type="text" placeholder={t.namePlaceholder} value={fullName} onChange={(event) => setFullName(event.target.value)} required /></label>}<label>{t.email}<input name="email" type="email" placeholder={t.emailPlaceholder} value={email} onChange={(event) => setEmail(event.target.value)} required /></label><label>{t.password}<input name="password" type="password" placeholder={t.passwordPlaceholder} minLength={6} value={password} onChange={(event) => setPassword(event.target.value)} required /></label>{!isSignup && <><a className="auth-forgot" href="#forgot">{t.forgot}</a><label className="auth-check"><input type="checkbox" checked={remember} onChange={(event) => setRemember(event.target.checked)} /><span>Remember me</span></label></>}{isSignup && <label className="auth-check"><input type="checkbox" checked={terms} onChange={(event) => setTerms(event.target.checked)} required /><span>{t.terms}</span></label>}{error && <p className="auth-error" role="alert">{error || t.required}</p>}<button className="auth-submit" type="submit" disabled={loading || googleLoading}>{loading ? "..." : content.primary}<span>↗</span></button></form><div className="auth-divider"><span>{t.or}</span></div><button className="auth-social" type="button" onClick={handleGoogleLogin} disabled={loading || googleLoading}><span className="google-mark">G</span>{googleLoading ? "..." : t.google}</button><p className="auth-switch">{content.switchText} <Link to={isSignup ? "/login" : "/register"}>{content.switchAction} <span>↗</span></Link></p></div>
      </section>
      <footer className="auth-footer"><span>© 2026 Slidegen</span><span>Ideas into slides.</span></footer>
    </main>
  );
}
