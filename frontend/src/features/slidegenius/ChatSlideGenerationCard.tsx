import type { ChatSlideStreamSlide } from "./ChatSlideStreamPanel";

interface ChatSlideGenerationCardProps {
  phase: "running" | "completed" | "error";
  slides: ChatSlideStreamSlide[];
  totalSlides: number | null;
  targetSlideCount: number | null;
  progress: number;
  projectId: number | null;
  projectName: string;
  error: string;
  title: string;
  generatingLabel: string;
  completedLabel: string;
  openStreamLabel: string;
  openProjectLabel: string;
  slideLabel: string;
  onOpenStream: () => void;
  onOpenProject: (projectId: number) => void;
}

export function ChatSlideGenerationCard({
  phase,
  slides,
  totalSlides,
  targetSlideCount,
  progress,
  projectId,
  projectName,
  error,
  title,
  generatingLabel,
  completedLabel,
  openStreamLabel,
  openProjectLabel,
  slideLabel,
  onOpenStream,
  onOpenProject,
}: ChatSlideGenerationCardProps) {
  const isRunning = phase === "running";
  const isError = phase === "error";
  const expectedSlides = totalSlides || targetSlideCount;
  const progressLabel = expectedSlides
    ? `${slides.length}/${expectedSlides} ${slideLabel.toLowerCase()}`
    : `${Math.round(progress)}%`;

  return (
    <article className={`chat-slide-generation-card ${phase}`} role="status" aria-live="polite">
      <span className={`chat-slide-generation-card-icon ${isError ? "error" : ""}`} aria-hidden="true">
        {isRunning ? <span className="chat-slide-generation-card-spinner" /> : isError ? "!" : "✓"}
      </span>
      <div className="chat-slide-generation-card-copy">
        <span className="chat-slide-generation-card-eyebrow">SLIDE DECK</span>
        <strong>{projectName || title}</strong>
        <small>{isError ? error : isRunning ? `${generatingLabel} · ${progressLabel}` : `${completedLabel} · ${progressLabel}`}</small>
      </div>
      {isRunning && <div className="chat-slide-generation-card-progress" aria-hidden="true"><span style={{ width: `${Math.min(100, Math.max(0, progress))}%` }} /></div>}
      <button className="chat-slide-generation-card-action" type="button" onClick={onOpenStream}>{openStreamLabel} ↗</button>
      {!isRunning && projectId !== null && (
        <button className="chat-slide-generation-card-project" type="button" onClick={() => onOpenProject(projectId)}>{openProjectLabel} ↗</button>
      )}
    </article>
  );
}
