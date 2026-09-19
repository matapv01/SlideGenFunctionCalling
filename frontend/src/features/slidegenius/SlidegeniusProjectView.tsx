import { useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { api } from "@/lib/api";
import { resolveSlideBackground } from "@/lib/slideBackground";
import { ProjectSlidePreview } from "@/components/ProjectSlidePreview";
import SlidegenLogo from "@/components/SlidegenLogo";
import { useLanguage } from "@/contexts/LanguageContext";
import SlidegenConfirmDialog from "@/components/SlidegenConfirmDialog";
import "./slidegenius-project-view.css";
import { truncateProjectName } from "./projectName";

interface PreviewSlide {
  id: string | number;
  title?: string;
  html_content?: string;
  content?: string;
  html?: string;
  design_settings?: unknown;
  backgroundColor?: string;
  backgroundImage?: string;
}

const copy = {
  en: {
    back: "Back to projects", project: "PROJECT", slides: "slides", open: "Open slide", close: "Close preview",
    previous: "Previous slide", next: "Next slide", edit: "Open editor", deleteProject: "Delete project", deleteProjectTitle: "Delete this project?", deleteProjectConfirm: "All slides will be permanently removed, while the generation record remains in chat.", deleteProjectFailed: "Unable to delete this project.", cancel: "Cancel", empty: "This project has no slides yet.", error: "Unable to load this project.", retry: "Try again", loading: "Loading project...", draft: "Draft",
  },
  vi: {
    back: "Về danh sách dự án", project: "DỰ ÁN", slides: "trang", open: "Mở slide", close: "Đóng xem trước",
    previous: "Slide trước", next: "Slide tiếp", edit: "Mở trình chỉnh sửa", deleteProject: "Xóa project", deleteProjectTitle: "Xóa project này?", deleteProjectConfirm: "Toàn bộ slide sẽ bị xóa vĩnh viễn, còn lịch sử tạo vẫn được giữ trong chatbot.", deleteProjectFailed: "Không thể xóa project.", cancel: "Hủy", empty: "Dự án này chưa có slide.", error: "Không thể tải dự án.", retry: "Thử lại", loading: "Đang tải dự án...", draft: "Bản nháp",
  },
} as const;

function slideContent(slide: PreviewSlide) {
  return slide.html_content || slide.html || slide.content || "";
}

export default function SlidegeniusProjectView() {
  const { projectId } = useParams();
  const navigate = useNavigate();
  const { language } = useLanguage();
  const t = copy[language];
  const [projectName, setProjectName] = useState("");
  const [projectStatus, setProjectStatus] = useState("");
  const [slides, setSlides] = useState<PreviewSlide[]>([]);
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState(false);
  const [activeSlide, setActiveSlide] = useState<number | null>(null);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [deleting, setDeleting] = useState(false);
  const [deleteError, setDeleteError] = useState("");

  const loadProject = async () => {
    if (!projectId) {
      setLoadError(true);
      setLoading(false);
      return;
    }
    setLoading(true);
    setLoadError(false);
    try {
      const [project, response] = await Promise.all([api.getProject(projectId), api.getSlides(projectId)]);
      setProjectName(project.title || project.name || "Untitled project");
      setProjectStatus(project.status || "draft");
      setSlides(response.slides.map((slide: PreviewSlide) => {
        const content = slideContent(slide);
        const { backgroundColor, backgroundImage } = resolveSlideBackground(slide.design_settings, content);
        return { ...slide, backgroundColor, backgroundImage };
      }));
    } catch {
      setLoadError(true);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    void loadProject();
  }, [projectId]);

  const confirmDeleteProject = async () => {
    if (!projectId || deleting) return;
    setDeleting(true);
    setDeleteError("");
    try {
      await api.deleteProject(projectId);
      navigate("/projects", { replace: true });
    } catch (error) {
      setDeleteError(error instanceof Error ? error.message : t.deleteProjectFailed);
      setDeleteDialogOpen(false);
    } finally {
      setDeleting(false);
    }
  };

  useEffect(() => {
    if (activeSlide === null) return;
    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape") setActiveSlide(null);
      if (event.key === "ArrowLeft") setActiveSlide((index) => Math.max(0, (index ?? 0) - 1));
      if (event.key === "ArrowRight" || event.key === " ") {
        event.preventDefault();
        setActiveSlide((index) => Math.min(slides.length - 1, (index ?? 0) + 1));
      }
    };
    const previousOverflow = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    window.addEventListener("keydown", handleKeyDown);
    return () => {
      document.body.style.overflow = previousOverflow;
      window.removeEventListener("keydown", handleKeyDown);
    };
  }, [activeSlide, slides.length]);

  return (
    <main className="sgv-page">
      <header className="sgv-header">
        <Link className="sgv-brand" to="/home" aria-label="Slidegen home"><SlidegenLogo /></Link>
        <div className="sgv-header-actions"><span>{projectStatus ? projectStatus.toUpperCase() : t.draft}</span><button type="button" onClick={() => navigate("/projects")}>← {t.back}</button></div>
      </header>

      <section className="sgv-shell">
        <div className="sgv-heading"><div><p>{t.project} / {String(projectId || "").padStart(2, "0")}</p><h1 title={projectName}>{projectName ? truncateProjectName(projectName) : t.loading}</h1><span>{slides.length} {t.slides}</span></div><div className="sgv-heading-actions"><span className="sgv-status">{projectStatus || t.draft}</span><div className="sgv-heading-button-row">{projectId && <button className="sgv-delete-button" type="button" onClick={() => { setDeleteError(""); setDeleteDialogOpen(true); }}>{t.deleteProject}</button>}{projectId && <Link className="sgv-edit-button" to={`/editor?project=${encodeURIComponent(projectId)}`}>{t.edit} ↗</Link>}</div></div></div>
        {deleteError && <p className="sgv-delete-error" role="alert">{deleteError}</p>}

        {loading ? <div className="sgv-state">{t.loading}</div> : loadError ? <div className="sgv-state"><p>{t.error}</p><button type="button" onClick={() => void loadProject()}>{t.retry}</button></div> : slides.length === 0 ? <div className="sgv-state"><p>{t.empty}</p></div> : <div className="sgv-grid">{slides.map((slide, index) => <article className="sgv-card" key={slide.id || index} onClick={() => setActiveSlide(index)} tabIndex={0} onKeyDown={(event) => { if (event.key === "Enter" || event.key === " ") { event.preventDefault(); setActiveSlide(index); } }}><div className="sgv-card-preview">{slideContent(slide) ? <ProjectSlidePreview slideId={`project-${projectId}-slide-${slide.id || index}`} content={slideContent(slide)} backgroundColor={slide.backgroundColor} backgroundImage={slide.backgroundImage} className="absolute inset-0" /> : <span>{t.empty}</span>}</div><div className="sgv-card-meta"><span>0{index + 1}</span><strong>{slide.title || `${t.open} ${index + 1}`}</strong><button type="button" onClick={(event) => { event.stopPropagation(); setActiveSlide(index); }}>{t.open} ↗</button></div></article>)}</div>}
      </section>

      {activeSlide !== null && slides[activeSlide] && <div className="sgv-viewer" role="dialog" aria-modal="true" aria-label={t.open}>
        <div className="sgv-viewer-top"><span>{String(activeSlide + 1).padStart(2, "0")} / {String(slides.length).padStart(2, "0")}</span><button type="button" onClick={() => setActiveSlide(null)} aria-label={t.close}>×</button></div>
        <div className="sgv-viewer-canvas">{slideContent(slides[activeSlide]) ? <ProjectSlidePreview slideId={`project-viewer-${projectId}-${slides[activeSlide].id || activeSlide}`} content={slideContent(slides[activeSlide])} backgroundColor={slides[activeSlide].backgroundColor} backgroundImage={slides[activeSlide].backgroundImage} className="absolute inset-0" /> : <span>{t.empty}</span>}</div>
        <button className="sgv-viewer-arrow left" type="button" onClick={() => setActiveSlide((index) => Math.max(0, (index ?? 0) - 1))} disabled={activeSlide === 0} aria-label={t.previous}>←</button>
        <button className="sgv-viewer-arrow right" type="button" onClick={() => setActiveSlide((index) => Math.min(slides.length - 1, (index ?? 0) + 1))} disabled={activeSlide === slides.length - 1} aria-label={t.next}>→</button>
        <div className="sgv-viewer-bottom"><span title={projectName}>{truncateProjectName(projectName)}</span><small>← → · Space · Esc</small></div>
      </div>}

      <SlidegenConfirmDialog
        open={deleteDialogOpen}
        onOpenChange={setDeleteDialogOpen}
        title={t.deleteProjectTitle}
        description={`${t.deleteProjectConfirm} ${projectName ? `(${truncateProjectName(projectName)})` : ""}`}
        confirmLabel={t.deleteProject}
        cancelLabel={t.cancel}
        onConfirm={() => void confirmDeleteProject()}
        destructive
        busy={deleting}
      />
    </main>
  );
}
