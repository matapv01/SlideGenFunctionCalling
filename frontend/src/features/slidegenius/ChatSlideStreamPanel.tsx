import { ProjectSlidePreview } from "@/components/ProjectSlidePreview";

export interface ChatSlideStreamSlide {
  index: number;
  title: string;
  content: string;
}

export interface ChatSlideStreamStatus {
  stage: string;
  title: string;
  description: string;
  message: string;
}

interface ChatSlideStreamPanelProps {
  className?: string;
  status: ChatSlideStreamStatus;
  progress: number;
  slides: ChatSlideStreamSlide[];
  totalSlides: number | null;
  completed: boolean;
  projectId: number | null;
  error: string;
  closeLabel: string;
  openProjectLabel: string;
  slideLabel: string;
  completedLabel: string;
  waitingLabel: string;
  onClose: () => void;
  onOpenProject: (projectId: number) => void;
}

export function ChatSlideStreamPanel({
  className,
  status,
  progress,
  slides,
  totalSlides,
  completed,
  projectId,
  error,
  closeLabel,
  openProjectLabel,
  slideLabel,
  completedLabel,
  waitingLabel,
  onClose,
  onOpenProject,
}: ChatSlideStreamPanelProps) {
  const safeProgress = Math.min(100, Math.max(0, Number.isFinite(progress) ? progress : 0));

  return (
    <aside className={`chat-slide-stream-panel${className ? ` ${className}` : ""}`} aria-live="polite">
      <div className="chat-slide-stream-header">
        <div>
          <p className="chat-slide-stream-eyebrow">SLIDE STREAM</p>
          <h3>{status.title}</h3>
        </div>
        <button type="button" aria-label={closeLabel} title={closeLabel} onClick={onClose}>×</button>
      </div>

      <div className="chat-slide-stream-progress-copy">
        <span>{status.message || status.description} · {slides.length}{totalSlides ? `/${totalSlides}` : ""} {slideLabel.toLowerCase()}</span>
        <strong>{Math.round(safeProgress)}%</strong>
      </div>
      <div className="chat-slide-stream-progress" aria-label={`${Math.round(safeProgress)}%`}>
        <span style={{ width: `${safeProgress}%` }} />
      </div>
      <p className="chat-slide-stream-description">{error || status.description}</p>

      <div className="chat-slide-stream-list">
        {slides.length === 0 ? (
          <div className="chat-slide-stream-empty">
            <span className="chat-slide-stream-empty-mark" aria-hidden="true">✦</span>
            <p>{waitingLabel}</p>
          </div>
        ) : slides.map((slide) => (
          <article className="chat-slide-stream-card" key={slide.index}>
            <div className="chat-slide-stream-preview">
              {slide.content ? (
                <ProjectSlidePreview
                  slideId={`chat-stream-slide-${slide.index}`}
                  content={slide.content}
                  className="chat-slide-stream-preview-canvas"
                />
              ) : (
                <span>{slide.title}</span>
              )}
            </div>
            <div className="chat-slide-stream-card-meta">
              <span>{String(slide.index + 1).padStart(2, "0")} / {slideLabel}</span>
              <strong>{slide.title || `${slideLabel} ${slide.index + 1}`}</strong>
            </div>
          </article>
        ))}
      </div>

      {completed && (
        <div className="chat-slide-stream-complete">
          <span>{completedLabel}</span>
          {projectId !== null && (
            <button type="button" onClick={() => onOpenProject(projectId)}>{openProjectLabel} ↗</button>
          )}
        </div>
      )}
    </aside>
  );
}
