import { useState } from "react";
import { Link, Navigate, useNavigate } from "react-router-dom";
import SlidegenLogo from "@/components/SlidegenLogo";
import { useAuth } from "@/contexts/AuthContext";
import { useLanguage } from "@/contexts/LanguageContext";
import { api } from "@/lib/api";
import "./slidegenius.css";
import "./slidegenius-onboarding.css";

const choices = {
  en: {
    step: "GETTING STARTED",
    useTitle: "What will you use SlideGen for?",
    useDescription: "Pick anything that fits. You can always change your mind later.",
    uses: [
      ["work", "Work presentations"],
      ["study", "School & learning"],
      ["pitch", "Pitch decks"],
      ["marketing", "Marketing & campaigns"],
      ["reports", "Reports & research"],
      ["personal", "Personal projects"],
    ],
    roleTitle: "Which best describes you?",
    roleDescription: "This helps us make your workspace feel more useful from day one.",
    roles: [
      ["student", "Student"],
      ["educator", "Educator"],
      ["founder", "Founder"],
      ["professional", "Professional"],
      ["creative", "Creative"],
      ["other", "Something else"],
    ],
    skip: "Skip for now",
    continue: "Continue",
    welcome: "Welcome to SlideGen",
    welcomeDescription: "Your workspace is ready. Start with an idea, a brief, or a document and make it into something worth sharing.",
    enter: "Go to workspace",
    progress: "Step",
    saveError: "We couldn't save your choices. Please try again.",
  },
  vi: {
    step: "BẮT ĐẦU",
    useTitle: "Bạn dùng SlideGen để làm gì?",
    useDescription: "Chọn những mục phù hợp. Bạn có thể bỏ qua bước này.",
    uses: [
      ["work", "Thuyết trình công việc"],
      ["study", "Học tập"],
      ["pitch", "Gọi vốn / giới thiệu ý tưởng"],
      ["marketing", "Marketing & chiến dịch"],
      ["reports", "Báo cáo & nghiên cứu"],
      ["personal", "Dự án cá nhân"],
    ],
    roleTitle: "Bạn đang làm công việc gì?",
    roleDescription: "SlideGen sẽ hiểu hơn cách bạn muốn làm việc.",
    roles: [
      ["student", "Học sinh / sinh viên"],
      ["educator", "Giáo viên"],
      ["founder", "Nhà sáng lập"],
      ["professional", "Nhân viên"],
      ["creative", "Người làm sáng tạo"],
      ["other", "Khác"],
    ],
    skip: "Bỏ qua",
    continue: "Tiếp tục",
    welcome: "Chào mừng đến với SlideGen",
    welcomeDescription: "Không gian làm việc của bạn đã sẵn sàng. Bắt đầu từ một ý tưởng, bản tóm tắt hoặc tài liệu để tạo nên bài trình bày của riêng bạn.",
    enter: "Vào workspace",
    progress: "Bước",
    saveError: "Chưa lưu được lựa chọn của bạn. Vui lòng thử lại.",
  },
} as const;

export default function SlidegeniusOnboarding() {
  const navigate = useNavigate();
  const { user, updateUser } = useAuth();
  const { language, setLanguage } = useLanguage();
  const [step, setStep] = useState(0);
  const [useCases, setUseCases] = useState<string[]>([]);
  const [role, setRole] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);
  const [saveError, setSaveError] = useState("");
  const t = choices[language];

  if (!user || user.onboarding_completed !== false) return <Navigate to="/home" replace />;

  const finish = async () => {
    if (saving) return;
    setSaving(true);
    setSaveError("");
    try {
      await api.completeOnboarding({ use_cases: useCases, role });
      updateUser({ onboarding_completed: true });
      navigate("/home", { replace: true });
    } catch {
      setSaveError(t.saveError);
      setSaving(false);
    }
  };

  const options = step === 0 ? t.uses : t.roles;
  const title = step === 0 ? t.useTitle : t.roleTitle;
  const description = step === 0 ? t.useDescription : t.roleDescription;

  return (
    <main className="sg-auth auth-page onboarding-page">
      <div className="auth-atmosphere" aria-hidden="true"><span /><span /><span /></div>
      <header className="auth-header">
        <Link className="brand" to="/" aria-label="SlideGen home"><SlidegenLogo /></Link>
        <div className="auth-header-actions">
          <button className="auth-language" type="button" onClick={() => setLanguage(language === "en" ? "vi" : "en")} aria-label={language === "vi" ? "Đổi ngôn ngữ" : "Switch language"}>{language === "en" ? "VI" : "EN"} <span>↗</span></button>
        </div>
      </header>
      <section className="onboarding-shell" aria-labelledby="onboarding-title">
        <div className="onboarding-progress" aria-label={`${t.progress} ${Math.min(step + 1, 3)} / 3`}>
          {[0, 1, 2].map((index) => <span key={index} className={index <= step ? "is-active" : ""} />)}
        </div>
        {step < 2 ? (
          <>
            <p className="auth-eyebrow">{t.step} / 0{step + 1}</p>
            <h1 id="onboarding-title">{title}</h1>
            <p className="onboarding-description">{description}</p>
            <div className="onboarding-options" role="group" aria-label={title}>
              {options.map(([value, label]) => {
                const selected = step === 0 ? useCases.includes(value) : role === value;
                return <button className={`onboarding-option${selected ? " is-selected" : ""}`} key={value} type="button" aria-pressed={selected} onClick={() => {
                  if (step === 0) setUseCases((current) => current.includes(value) ? current.filter((item) => item !== value) : [...current, value]);
                  else setRole(value);
                }}><span className="onboarding-option-check" aria-hidden="true">{selected ? "✓" : ""}</span>{label}</button>;
              })}
            </div>
            <div className="onboarding-actions">
              <button className="onboarding-skip" type="button" onClick={() => {
                if (step === 0) setUseCases([]);
                else setRole(null);
                setStep(step + 1);
              }}>{t.skip}</button>
              <button className="onboarding-next" type="button" onClick={() => setStep(step + 1)}>{t.continue}<span aria-hidden="true">↗</span></button>
            </div>
          </>
        ) : (
          <div className="onboarding-welcome">
            <span className="onboarding-spark" aria-hidden="true">✦</span>
            <p className="auth-eyebrow">SLIDEGEN / WELCOME</p>
            <h1 id="onboarding-title">{t.welcome}{user.full_name ? `, ${user.full_name.trim().split(/\s+/).slice(-1)[0]}` : ""}.</h1>
            <p className="onboarding-description">{t.welcomeDescription}</p>
            {saveError && <p className="onboarding-error" role="alert">{saveError}</p>}
            <button className="onboarding-next" type="button" disabled={saving} onClick={() => void finish()}>{saving ? "..." : t.enter}<span aria-hidden="true">↗</span></button>
          </div>
        )}
      </section>
      <footer className="auth-footer"><span>© 2026 SlideGen</span><span>Ideas into slides.</span></footer>
    </main>
  );
}
