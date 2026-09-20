import { useEffect, useMemo, useState } from "react";
import { createPortal } from "react-dom";
import { useAuth } from "@/contexts/AuthContext";
import { useLanguage } from "@/contexts/LanguageContext";
import "./workspace-tour.css";

type TourStep = {
  target: string;
  title: string;
  description: string;
};

const TOUR_VERSION = 1;

const copy = {
  vi: {
    eyebrow: "BẮT ĐẦU VỚI SLIDEGEN",
    title: "Làm quen với workspace",
    steps: [
      { target: "workspace-nav", title: "Thanh điều hướng workspace", description: "Chuyển nhanh giữa Slidegenius, Projects, Manual và Guide từ thanh bên này." },
      { target: "chat-history", title: "Lịch sử hội thoại", description: "Các cuộc trò chuyện được lưu lại để bạn có thể mở tiếp bất cứ lúc nào." },
      { target: "chat-composer", title: "Tạo slide bằng một câu lệnh", description: "Nhập ý tưởng, brief hoặc gắn tài liệu DOCX rồi gửi cho Slidegenius." },
      { target: "composer-model", title: "Chọn model và mức effort", description: "Genius 3 Medium là lựa chọn cân bằng. Bạn có thể đổi model hoặc mức effort khi cần." },
      { target: "projects-nav", title: "Quản lý project", description: "Bài trình bày đã tạo sẽ nằm trong Project Manager để xem, đổi tên và chỉnh sửa." },
    ],
    skip: "Bỏ qua",
    back: "Quay lại",
    next: "Tiếp theo",
    finish: "Bắt đầu tạo slide",
    progress: "Bước",
    close: "Đóng hướng dẫn",
    saveError: "Không thể lưu lựa chọn lúc này. Vui lòng thử lại.",
  },
  en: {
    eyebrow: "GET STARTED WITH SLIDEGEN",
    title: "A quick tour of your workspace",
    steps: [
      { target: "workspace-nav", title: "Workspace navigation", description: "Move between Slidegenius, Projects, Manual and Guide from this sidebar." },
      { target: "chat-history", title: "Conversation history", description: "Your conversations are saved here so you can pick up where you left off." },
      { target: "chat-composer", title: "Create slides with a prompt", description: "Enter an idea, brief or attach a DOCX document, then send it to Slidegenius." },
      { target: "composer-model", title: "Choose model and effort", description: "Genius 3 Medium is a balanced default. Change the model or effort whenever you need." },
      { target: "projects-nav", title: "Manage your projects", description: "Generated presentations appear in Project Manager, where you can review and edit them." },
    ],
    skip: "Skip tour",
    back: "Back",
    next: "Next",
    finish: "Start creating",
    progress: "Step",
    close: "Close tour",
    saveError: "We couldn't save your choice. Please try again.",
  },
} as const;

type Placement = "below" | "above" | "center";

type Position = {
  top: number;
  left: number;
  width: number;
  height: number;
  tooltipTop: number;
  tooltipLeft: number;
  placement: Placement;
};

export default function WorkspaceTour() {
  const { user, completeWorkspaceTour } = useAuth();
  const { language } = useLanguage();
  const text = copy[language];
  const steps = useMemo(() => text.steps, [text.steps]);
  const [stepIndex, setStepIndex] = useState(0);
  const [position, setPosition] = useState<Position | null>(null);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");

  const isOpen = user?.workspace_tour_version === 0;
  const currentStep = steps[stepIndex];

  useEffect(() => {
    if (!isOpen) return;

    const measure = () => {
      const target = document.querySelector<HTMLElement>(`[data-tour="${currentStep.target}"]`);
      if (!target) {
        setPosition({
          top: 0,
          left: 0,
          width: 0,
          height: 0,
          tooltipTop: Math.max(24, (window.innerHeight - 300) / 2),
          tooltipLeft: Math.max(16, (window.innerWidth - 360) / 2),
          placement: "center",
        });
        return;
      }

      const rect = target.getBoundingClientRect();
      const cardWidth = Math.min(360, window.innerWidth - 32);
      const cardHeight = 230;
      const gap = 16;
      const below = rect.bottom + gap + cardHeight <= window.innerHeight;
      const placement: Placement = below ? "below" : rect.top - gap - cardHeight >= 16 ? "above" : "center";
      const tooltipTop = placement === "below"
        ? rect.bottom + gap
        : placement === "above"
          ? rect.top - gap - cardHeight
          : Math.max(16, (window.innerHeight - cardHeight) / 2);
      const tooltipLeft = Math.min(
        Math.max(16, rect.left),
        Math.max(16, window.innerWidth - cardWidth - 16),
      );

      setPosition({
        top: Math.max(8, rect.top - 8),
        left: Math.max(8, rect.left - 8),
        width: rect.width + 16,
        height: rect.height + 16,
        tooltipTop,
        tooltipLeft,
        placement,
      });
    };

    const frame = window.requestAnimationFrame(measure);
    window.addEventListener("resize", measure);
    window.addEventListener("scroll", measure, true);
    return () => {
      window.cancelAnimationFrame(frame);
      window.removeEventListener("resize", measure);
      window.removeEventListener("scroll", measure, true);
    };
  }, [currentStep.target, isOpen]);

  useEffect(() => {
    if (!isOpen) return;
    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape") void finishTour();
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  });

  if (!isOpen || !position) return null;

  async function finishTour() {
    if (saving) return;
    setSaving(true);
    setError("");
    try {
      await completeWorkspaceTour(TOUR_VERSION);
    } catch {
      setError(text.saveError);
      setSaving(false);
    }
  }

  const isLastStep = stepIndex === steps.length - 1;

  return createPortal(
    <div className="workspace-tour" role="dialog" aria-modal="true" aria-labelledby="workspace-tour-title">
      <div className="workspace-tour-backdrop" aria-hidden="true" />
      {position.placement !== "center" && (
        <div
          className="workspace-tour-spotlight"
          aria-hidden="true"
          style={{ top: position.top, left: position.left, width: position.width, height: position.height }}
        />
      )}
      <section
        className={`workspace-tour-card is-${position.placement}`}
        style={{ top: position.tooltipTop, left: position.tooltipLeft }}
      >
        <div className="workspace-tour-card-top">
          <span>{text.eyebrow}</span>
          <button type="button" aria-label={text.close} title={text.close} onClick={() => void finishTour()} disabled={saving}>×</button>
        </div>
        <p className="workspace-tour-progress">{text.progress} {stepIndex + 1} / {steps.length}</p>
        <h2 id="workspace-tour-title">{currentStep.title}</h2>
        <p className="workspace-tour-description">{currentStep.description}</p>
        {error && <p className="workspace-tour-error" role="alert">{error}</p>}
        <div className="workspace-tour-actions">
          <button className="workspace-tour-skip" type="button" onClick={() => void finishTour()} disabled={saving}>{text.skip}</button>
          <div className="workspace-tour-navigation">
            {stepIndex > 0 && <button className="workspace-tour-back" type="button" onClick={() => setStepIndex((value) => value - 1)} disabled={saving}>{text.back}</button>}
            <button className="workspace-tour-next" type="button" onClick={() => isLastStep ? void finishTour() : setStepIndex((value) => value + 1)} disabled={saving}>
              {isLastStep ? text.finish : text.next}<span aria-hidden="true">↗</span>
            </button>
          </div>
        </div>
      </section>
    </div>,
    document.body,
  );
}
