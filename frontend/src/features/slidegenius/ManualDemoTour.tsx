import { useEffect, useState } from "react";
import { createPortal } from "react-dom";
import { useAuth } from "@/contexts/AuthContext";
import { useLanguage } from "@/contexts/LanguageContext";
import "./workspace-tour.css";

type ManualTourStep = {
  target: string;
  title: string;
  description: string;
};

const TOUR_VERSION = 2;

const copy = {
  vi: {
    eyebrow: "THỬ MANUAL",
    progress: "Bước",
    close: "Đóng hướng dẫn",
    back: "Quay lại",
    next: "Tiếp theo",
    finish: "Hoàn tất hướng dẫn",
    skip: "Bỏ qua",
    saveError: "Không thể lưu lựa chọn lúc này. Vui lòng thử lại.",
    exampleHeading: "Tiêu đề slide",
    exampleBody: "Nội dung chính của slide",
    exampleBullet: "Ý quan trọng",
    exampleHint: "# = slide mới · - = gạch đầu dòng",
    steps: [
      { target: "manual-editor", title: "Xem cách nhập mẫu", description: "Mẫu đang được nhập từng dòng ngay trong ô Markdown. Hãy để ý: # tạo slide mới, dòng thường là nội dung và - tạo gạch đầu dòng." },
      { target: "manual-preview", title: "Xem slide thay đổi ngay", description: "Khung Preview bên phải cập nhật theo nội dung bạn nhập. Dùng - ở đầu dòng để tạo gạch đầu dòng trong slide." },
      { target: "manual-approve", title: "Duyệt cấu trúc để tạo slide", description: "Khi dùng Manual thật, tải DOCX từ màn hình trước, chỉnh nội dung ở đây rồi bấm Approve & Continue để bắt đầu thiết kế." },
    ],
  },
  en: {
    eyebrow: "TRY MANUAL",
    progress: "Step",
    close: "Close tour",
    back: "Back",
    next: "Next",
    finish: "Finish tour",
    skip: "Skip",
    saveError: "We couldn't save your choice. Please try again.",
    exampleHeading: "Slide title",
    exampleBody: "Main slide content",
    exampleBullet: "Important point",
    exampleHint: "# = new slide · - = bullet point",
    steps: [
      { target: "manual-editor", title: "Watch the sample being written", description: "The sample is typed line by line into the Markdown editor. Notice: # creates a new slide, a normal line is content, and - creates a bullet point." },
      { target: "manual-preview", title: "Preview the slide instantly", description: "The Preview panel updates as you type. Start a line with - to create a bullet point in the slide." },
      { target: "manual-approve", title: "Approve the structure", description: "In a real Manual workflow, upload a DOCX on the previous screen, edit it here, then click Approve & Continue to start designing." },
    ],
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

export default function ManualDemoTour() {
  const { user, completeWorkspaceTour } = useAuth();
  const { language } = useLanguage();
  const text = copy[language];
  const [stepIndex, setStepIndex] = useState(0);
  const [position, setPosition] = useState<Position | null>(null);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const currentStep: ManualTourStep = text.steps[stepIndex];
  const isOpen = user?.workspace_tour_version === 0;

  useEffect(() => {
    if (!isOpen) return;

    const measure = () => {
      const target = document.querySelector<HTMLElement>(`[data-tour="${currentStep.target}"]`);
      if (!target) return;

      const rect = target.getBoundingClientRect();
      const cardWidth = Math.min(360, window.innerWidth - 32);
      const cardHeight = stepIndex === 0 ? 340 : 250;
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
      const selected = candidates.find(({ top, left }) => (
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

  const isLastStep = stepIndex === text.steps.length - 1;

  return createPortal(
    <div className={`workspace-tour workspace-tour-manual-demo ${stepIndex === 0 ? "is-manual-typing" : ""}`} role="dialog" aria-modal="true" aria-labelledby="manual-tour-title">
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
        <p className="workspace-tour-progress">{text.progress} {stepIndex + 1} / {text.steps.length}</p>
        <h2 id="manual-tour-title">{currentStep.title}</h2>
        <p className="workspace-tour-description">{currentStep.description}</p>
        {stepIndex === 0 && (
          <div className="workspace-tour-manual-preview" aria-label={text.exampleHint}>
            <code><span className="workspace-tour-mark">#</span> {text.exampleHeading}</code>
            <code>{text.exampleBody}</code>
            <code><span className="workspace-tour-mark">-</span> {text.exampleBullet}</code>
            <small>{text.exampleHint}</small>
          </div>
        )}
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
