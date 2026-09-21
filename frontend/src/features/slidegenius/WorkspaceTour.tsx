import { useEffect, useMemo, useState } from "react";
import { createPortal } from "react-dom";
import { useNavigate } from "react-router-dom";
import { useAuth } from "@/contexts/AuthContext";
import { useLanguage } from "@/contexts/LanguageContext";
import "./workspace-tour.css";

type TourStep = {
  target: string;
  title: string;
  description: string;
};

const TOUR_VERSION = 2;

const copy = {
  vi: {
    eyebrow: "BẮT ĐẦU VỚI SLIDEGEN",
    title: "Làm quen với workspace",
    toolUpload: "Tải file",
    toolSearch: "Search trên web",
    manualExampleHeading: "# Tiêu đề slide",
    manualExampleBody: "Nội dung chính của slide",
    manualExampleBullet: "- Gạch đầu dòng",
    manualHint: "# tạo slide mới · - tạo bullet",
    steps: [
      { target: "workspace-nav", title: "Thanh điều hướng workspace", description: "Chuyển nhanh giữa Slidegenius, Projects, Manual và Guide từ thanh bên này." },
      { target: "chat-history", title: "Lịch sử hội thoại", description: "Các cuộc trò chuyện được lưu lại để bạn có thể mở tiếp bất cứ lúc nào." },
      { target: "chat-composer", title: "Tạo slide bằng một câu lệnh", description: "Nhập ý tưởng, brief hoặc gắn file rồi gửi cho Slidegenius." },
      { target: "composer-tools", title: "Mở thêm công cụ bằng dấu +", description: "Bấm dấu + để tải file hoặc bật Search khi cần tìm thông tin trên web." },
      { target: "composer-model", title: "Chọn model và mức effort", description: "Genius 3 Medium là lựa chọn cân bằng. Bạn có thể đổi model hoặc mức effort khi cần." },
      { target: "manual-nav", title: "Tự dựng slide bằng Manual", description: "Trong Manual, dùng Markdown để chia cấu trúc: mỗi dòng bắt đầu bằng # tạo một slide mới, nội dung bên dưới là phần thân và - tạo gạch đầu dòng." },
      { target: "projects-nav", title: "Quản lý project", description: "Bài trình bày đã tạo sẽ nằm trong Project Manager để xem, đổi tên và chỉnh sửa." },
    ],
    skip: "Bỏ qua",
    back: "Quay lại",
    next: "Tiếp theo",
    manualDemo: "Mở Manual mẫu",
    finish: "Bắt đầu tạo slide",
    progress: "Bước",
    close: "Đóng hướng dẫn",
    saveError: "Không thể lưu lựa chọn lúc này. Vui lòng thử lại.",
  },
  en: {
    eyebrow: "GET STARTED WITH SLIDEGEN",
    title: "A quick tour of your workspace",
    toolUpload: "Upload file",
    toolSearch: "Search the web",
    manualExampleHeading: "# Slide title",
    manualExampleBody: "Main slide content",
    manualExampleBullet: "- Bullet point",
    manualHint: "# creates a new slide · - creates a bullet",
    steps: [
      { target: "workspace-nav", title: "Workspace navigation", description: "Move between Slidegenius, Projects, Manual and Guide from this sidebar." },
      { target: "chat-history", title: "Conversation history", description: "Your conversations are saved here so you can pick up where you left off." },
      { target: "chat-composer", title: "Create slides with a prompt", description: "Enter an idea, brief or attach a file, then send it to Slidegenius." },
      { target: "composer-tools", title: "Open tools with the + button", description: "Select the + button to upload a file or turn on Search when you need web information." },
      { target: "composer-model", title: "Choose model and effort", description: "Genius 3 Medium is a balanced default. Change the model or effort whenever you need." },
      { target: "manual-nav", title: "Build slides manually", description: "In Manual, use Markdown to define the structure: each line starting with # creates a new slide, the following lines become content, and - creates a bullet." },
      { target: "projects-nav", title: "Manage your projects", description: "Generated presentations appear in Project Manager, where you can review and edit them." },
    ],
    skip: "Skip tour",
    back: "Back",
    next: "Next",
    manualDemo: "Open Manual demo",
    finish: "Start creating",
    progress: "Step",
    close: "Close tour",
    saveError: "We couldn't save your choice. Please try again.",
  },
} as const;

type Placement = "below" | "above" | "left" | "right" | "center";

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
  const navigate = useNavigate();
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
      // The tools step includes a small upload/search preview, so reserve
      // enough room when deciding whether the card goes above or below.
      const cardHeight = currentStep.target === "composer-tools"
        ? 480
        : currentStep.target === "composer-model"
          ? 380
          : currentStep.target === "manual-nav"
            ? 340
            : 230;
      const gap = 16;
      const minEdge = 16;
      const maxTop = Math.max(minEdge, window.innerHeight - cardHeight - minEdge);
      const maxLeft = Math.max(minEdge, window.innerWidth - cardWidth - minEdge);
      const clampTop = (value: number) => Math.min(Math.max(minEdge, value), maxTop);
      const clampLeft = (value: number) => Math.min(Math.max(minEdge, value), maxLeft);
      const overlapsTarget = (top: number, left: number) => !(
        top + cardHeight <= rect.top - 8
        || top >= rect.bottom + 8
        || left + cardWidth <= rect.left - 8
        || left >= rect.right + 8
      );
      const candidates: Array<{ placement: Exclude<Placement, "center">; top: number; left: number }> = [
        { placement: "below", top: rect.bottom + gap, left: clampLeft(rect.left) },
        { placement: "above", top: rect.top - gap - cardHeight, left: clampLeft(rect.left) },
        { placement: "right", top: clampTop(rect.top + (rect.height - cardHeight) / 2), left: rect.right + gap },
        { placement: "left", top: clampTop(rect.top + (rect.height - cardHeight) / 2), left: rect.left - gap - cardWidth },
      ];
      const sidebarTarget = ["workspace-nav", "chat-history", "manual-nav", "projects-nav"].includes(currentStep.target);
      const orderedCandidates = currentStep.target === "composer-tools"
        ? [candidates[2], candidates[3], candidates[1], candidates[0]]
        : currentStep.target === "composer-model"
          ? [candidates[3], candidates[2], candidates[1], candidates[0]]
          : sidebarTarget
        ? [candidates[2], candidates[0], candidates[1], candidates[3]]
        : candidates;
      const selected = orderedCandidates.find(({ top, left }) => (
        top >= minEdge
        && left >= minEdge
        && top + cardHeight <= window.innerHeight - minEdge
        && left + cardWidth <= window.innerWidth - minEdge
        && !overlapsTarget(top, left)
      ));
      const placement: Placement = selected?.placement || "center";
      const tooltipTop = selected?.top ?? Math.max(minEdge, (window.innerHeight - cardHeight) / 2);
      const tooltipLeft = selected?.left ?? Math.max(minEdge, (window.innerWidth - cardWidth) / 2);

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

  function openManualDemo() {
    navigate("/structure?demo=1");
  }

  const isLastStep = stepIndex === steps.length - 1;
  const isManualStep = currentStep.target === "manual-nav";

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
        {currentStep.target === "composer-tools" && (
          <div className="workspace-tour-tool-preview" aria-label={`${text.toolUpload}, ${text.toolSearch}`}>
            <div><span aria-hidden="true">↑</span>{text.toolUpload}</div>
            <div><span aria-hidden="true">⌕</span>{text.toolSearch}</div>
          </div>
        )}
        {currentStep.target === "manual-nav" && (
          <div className="workspace-tour-manual-preview" aria-label={text.manualHint}>
            <code><span className="workspace-tour-mark">#</span> {text.manualExampleHeading.replace(/^#\s*/, "")}</code>
            <code>{text.manualExampleBody}</code>
            <code><span className="workspace-tour-mark">-</span> {text.manualExampleBullet.replace(/^-\s*/, "")}</code>
            <small>{text.manualHint}</small>
          </div>
        )}
        {error && <p className="workspace-tour-error" role="alert">{error}</p>}
        <div className="workspace-tour-actions">
          <button className="workspace-tour-skip" type="button" onClick={() => void finishTour()} disabled={saving}>{text.skip}</button>
          <div className="workspace-tour-navigation">
            {stepIndex > 0 && <button className="workspace-tour-back" type="button" onClick={() => setStepIndex((value) => value - 1)} disabled={saving}>{text.back}</button>}
            <button className="workspace-tour-next" type="button" onClick={() => isManualStep ? openManualDemo() : isLastStep ? void finishTour() : setStepIndex((value) => value + 1)} disabled={saving}>
              {isManualStep ? text.manualDemo : isLastStep ? text.finish : text.next}<span aria-hidden="true">↗</span>
            </button>
          </div>
        </div>
      </section>
    </div>,
    document.body,
  );
}
