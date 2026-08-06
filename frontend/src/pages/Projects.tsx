import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { Search, FolderOpen, Edit, FileText, Trash2, Eye, MoreVertical, Grid3X3, List, CheckSquare, Square } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter, DialogDescription } from "@/components/ui/dialog";
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from "@/components/ui/dropdown-menu";
import { Checkbox } from "@/components/ui/checkbox";
import { useToast } from "@/hooks/use-toast";
import { api } from "@/lib/api";
import { resolveSlideBackground } from "@/lib/slideBackground";
import { AppLayout } from "@/components/AppLayout";
import { ProjectSlidePreview } from "@/components/ProjectSlidePreview";
import { useLanguage } from "@/contexts/LanguageContext";

const Projects = () => {
  const navigate = useNavigate();
  const { toast } = useToast();
  const { t } = useLanguage();
  const [projects, setProjects] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [viewMode, setViewMode] = useState<"grid" | "list">(() => {
    const saved = localStorage.getItem("projectsViewMode");
    return (saved === "list" || saved === "grid") ? saved : "grid";
  });
  const [deleteId, setDeleteId] = useState<string | null>(null);
  const [renameId, setRenameId] = useState<string | null>(null);
  const [renameName, setRenameName] = useState("");
  const [firstSlides, setFirstSlides] = useState<Record<string, string>>({});
  const [firstSlideBackgrounds, setFirstSlideBackgrounds] = useState<Record<string, string>>({});
  const [firstSlideBackgroundImages, setFirstSlideBackgroundImages] = useState<Record<string, string>>({});
  const [slideCounts, setSlideCounts] = useState<Record<string, number>>({});
  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set());
  const [selectMode, setSelectMode] = useState(false);
  const [bulkDeleteOpen, setBulkDeleteOpen] = useState(false);

  useEffect(() => {
    loadProjects();
  }, []);

  const loadProjects = async () => {
    try {
      const res = await api.getProjects();
      // Map backend fields to frontend expected fields
      const mappedProjects = res.projects.map((p: any) => ({
        ...p,
        name: p.title,
        slideCount: p.slide_count,
        updatedAt: p.updated_at,
      }));
      setProjects(mappedProjects);
      setLoading(false);
      
      // Load slide previews in batches (optimized)
      const loadSlidesInBatches = async () => {
        const BATCH_SIZE = 3; // Small batch to avoid GPU overload
        const BATCH_DELAY = 100; // 100ms delay between batches
        
        for (let i = 0; i < mappedProjects.length; i += BATCH_SIZE) {
          const batch = mappedProjects.slice(i, i + BATCH_SIZE);
          
          const results = await Promise.allSettled(
            batch.map(async (project: any) => {
              try {
                const slidesRes = await api.getSlides(project.id, 1); // Only fetch first slide
                const count = slidesRes.total || slidesRes.slides?.length || 0;
                
                if (slidesRes.slides && slidesRes.slides.length > 0) {
                  const slide = slidesRes.slides[0];
                  const rawContent = slide.xmlContent || slide.xml_content || slide.html_content || slide.html || slide.content || '';
                  const { backgroundColor, backgroundImage } = resolveSlideBackground(slide.design_settings, rawContent);
                  
                  return {
                    id: project.id,
                    html: rawContent,
                    bg: backgroundColor,
                    bgImg: backgroundImage,
                    count,
                  };
                }
                return { id: project.id, count };
              } catch {
                return { id: project.id, count: 0 };
              }
            })
          );
          
          // Update state after each batch
          results.forEach((result) => {
            if (result.status === 'fulfilled' && result.value) {
              const data = result.value;
              if (data.html) setFirstSlides(prev => ({ ...prev, [data.id]: data.html }));
              if (data.bg) setFirstSlideBackgrounds(prev => ({ ...prev, [data.id]: data.bg }));
              if (data.bgImg) setFirstSlideBackgroundImages(prev => ({ ...prev, [data.id]: data.bgImg }));
              setSlideCounts(prev => ({ ...prev, [data.id]: data.count }));
            }
          });
          
          // Small delay between batches to avoid UI freeze
          if (i + BATCH_SIZE < mappedProjects.length) {
            await new Promise(resolve => setTimeout(resolve, BATCH_DELAY));
          }
        }
      };
      
      // Load in background
      loadSlidesInBatches();
    } catch (err: any) {
      toast({ title: t.projects_toast_load_fail, variant: "destructive" });
      setLoading(false);
    }
  };

  const handleDelete = async () => {
    if (!deleteId) return;
    try {
      await api.deleteProject(deleteId);
      setProjects((p) => p.filter((x) => x.id !== deleteId));
      toast({ title: t.projects_toast_deleted });
    } catch (err: any) {
      toast({ title: t.projects_toast_delete_fail, variant: "destructive" });
    }
    setDeleteId(null);
  };

  const handleRename = async () => {
    if (!renameId || !renameName.trim()) return;
    try {
      await api.renameProject(renameId, renameName);
      setProjects((p) => p.map((x) => (x.id === renameId ? { ...x, name: renameName, title: renameName } : x)));
      toast({ title: t.projects_toast_renamed });
    } catch (err: any) {
      toast({ title: t.projects_toast_rename_fail, variant: "destructive" });
    }
    setRenameId(null);
  };

  const toggleSelect = (id: string) => {
    setSelectedIds((prev) => {
      const next = new Set(prev);
      if (next.has(id)) {
        next.delete(id);
      } else {
        next.add(id);
      }
      return next;
    });
  };

  const selectAll = () => {
    if (selectedIds.size === filtered.length) {
      setSelectedIds(new Set());
    } else {
      setSelectedIds(new Set(filtered.map((p) => p.id)));
    }
  };

  const handleBulkDelete = async () => {
    try {
      await Promise.all(Array.from(selectedIds).map((id) => api.deleteProject(id)));
      setProjects((p) => p.filter((x) => !selectedIds.has(x.id)));
      toast({ title: `${selectedIds.size} ${t.projects_toast_deleted}` });
      setSelectedIds(new Set());
      setSelectMode(false);
    } catch (err: any) {
      toast({ title: t.projects_toast_delete_fail, variant: "destructive" });
    }
    setBulkDeleteOpen(false);
  };

  const exitSelectMode = () => {
    setSelectMode(false);
    setSelectedIds(new Set());
  };

  const filtered = projects.filter((p) =>
    p.name?.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <AppLayout>
      <div className="p-4 lg:p-6">
        <div className="mb-6 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div className="flex items-center gap-3">
            <h1 className="text-2xl font-bold">{t.projects_title}</h1>
            {selectMode && (
              <span className="text-sm text-muted-foreground">
                {selectedIds.size} {t.projects_select_mode}
              </span>
            )}
          </div>
          <div className="flex items-center gap-2">
            {selectMode ? (
              <>
                <Button variant="outline" size="sm" onClick={selectAll}>
                  {selectedIds.size === filtered.length ? (
                    <><Square className="mr-1 h-4 w-4" /> {t.projects_deselect_all}</>
                  ) : (
                    <><CheckSquare className="mr-1 h-4 w-4" /> {t.projects_select_all}</>
                  )}
                </Button>
                <Button
                  variant="destructive"
                  size="sm"
                  disabled={selectedIds.size === 0}
                  onClick={() => setBulkDeleteOpen(true)}
                >
                  <Trash2 className="mr-1 h-4 w-4" /> {t.projects_delete} ({selectedIds.size})
                </Button>
                <Button variant="ghost" size="sm" onClick={exitSelectMode}>
                  {t.projects_cancel}
                </Button>
              </>
            ) : (
              <>
                <div className="relative flex-1 sm:w-64">
                  <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                  <Input placeholder={t.projects_search} className="pl-9" value={search} onChange={(e) => setSearch(e.target.value)} />
                </div>
                <Button variant="outline" size="icon" onClick={() => setSelectMode(true)} title={t.projects_select_mode}>
                  <CheckSquare className="h-4 w-4" />
                </Button>
                <Button variant="outline" size="icon" onClick={() => {
                  const newMode = viewMode === "grid" ? "list" : "grid";
                  setViewMode(newMode);
                  localStorage.setItem("projectsViewMode", newMode);
                }}>
                  {viewMode === "grid" ? <List className="h-4 w-4" /> : <Grid3X3 className="h-4 w-4" />}
                </Button>
              </>
            )}
          </div>
        </div>

        {loading ? (
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {[1, 2, 3].map((i) => (
              <Card key={i} className="animate-pulse">
                <CardContent className="h-40" />
              </Card>
            ))}
          </div>
        ) : filtered.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-20 text-center">
            <FolderOpen className="mb-4 h-12 w-12 text-muted-foreground" />
            <p className="text-lg font-medium">{t.projects_no_found}</p>
            <p className="text-sm text-muted-foreground">{t.projects_no_found_hint}</p>
            <Button className="mt-4" onClick={() => navigate("/")}>{t.projects_go_home}</Button>
          </div>
        ) : viewMode === "grid" ? (
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {filtered.map((project) => (
              <Card
                key={project.id}
                className={`glass cursor-pointer relative ${selectedIds.has(project.id) ? "ring-2 ring-primary" : ""}`}
                style={{ willChange: 'auto' }}
                onClick={() => selectMode ? toggleSelect(project.id) : navigate(`/view/${project.id}`)}
              >
                {selectMode && (
                  <div className="absolute top-2 left-2 z-10" onClick={(e) => e.stopPropagation()}>
                    <Checkbox
                      checked={selectedIds.has(project.id)}
                      onCheckedChange={() => toggleSelect(project.id)}
                      className="h-5 w-5 bg-background"
                    />
                  </div>
                )}
                <CardHeader className="flex flex-row items-start justify-between">
                  <div className={selectMode ? "ml-6" : ""}>
                    <CardTitle className="text-base">{project.name}</CardTitle>
                    <p className="mt-1 text-xs text-muted-foreground">
                      {slideCounts[project.id] ?? project.slideCount ?? 0} {t.projects_slides} • {project.updatedAt ? new Date(new Date(project.updatedAt).getTime() + 7 * 60 * 60 * 1000).toLocaleString('vi-VN', { day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit', second: '2-digit' }) : ""}
                    </p>
                  </div>
                  {!selectMode && (
                    <div className="flex items-center gap-1">
                      <Button variant="ghost" size="sm" onClick={(e) => { e.stopPropagation(); navigate(`/editor?project=${project.id}`); }}>
                        <Edit className="mr-1 h-3 w-3" /> {t.projects_edit}
                      </Button>
                      <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                          <Button variant="ghost" size="icon" className="h-8 w-8" onClick={(e) => e.stopPropagation()}>
                            <MoreVertical className="h-4 w-4" />
                          </Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent align="end">
                          <DropdownMenuItem onClick={(e) => { e.stopPropagation(); setRenameId(project.id); setRenameName(project.name); }}>
                            <Edit className="mr-2 h-4 w-4" /> {t.projects_rename}
                          </DropdownMenuItem>
                          <DropdownMenuItem onClick={(e) => { e.stopPropagation(); navigate(`/view/${project.id}`); }}>
                            <Eye className="mr-2 h-4 w-4" /> {t.projects_view}
                          </DropdownMenuItem>
                          <DropdownMenuItem className="text-destructive" onClick={(e) => { e.stopPropagation(); setDeleteId(project.id); }}>
                            <Trash2 className="mr-2 h-4 w-4" /> {t.projects_delete}
                          </DropdownMenuItem>
                        </DropdownMenuContent>
                      </DropdownMenu>
                    </div>
                  )}
                </CardHeader>
                <CardContent>
                  <div className="aspect-video overflow-hidden rounded-lg bg-muted/50 relative">
                    {firstSlides[project.id] ? (
                      <ProjectSlidePreview
                        slideId={`project-thumb-${project.id}`}
                        content={firstSlides[project.id]}
                        backgroundColor={firstSlideBackgrounds[project.id]}
                        backgroundImage={firstSlideBackgroundImages[project.id]}
                        className="absolute inset-0"
                      />
                    ) : (
                      <div className="flex h-full items-center justify-center">
                        <FolderOpen className="h-10 w-10 text-muted-foreground/40 animate-pulse" />
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        ) : (
          <div className="space-y-2">
            {filtered.map((project) => (
              <Card
                key={project.id}
                className={`glass cursor-pointer ${selectedIds.has(project.id) ? "ring-2 ring-primary" : ""}`}
                onClick={() => selectMode ? toggleSelect(project.id) : navigate(`/view/${project.id}`)}
              >
                <CardContent className="flex items-center justify-between p-4">
                  <div className="flex items-center gap-3">
                    {selectMode && (
                      <div onClick={(e) => e.stopPropagation()}>
                        <Checkbox
                          checked={selectedIds.has(project.id)}
                          onCheckedChange={() => toggleSelect(project.id)}
                          className="h-5 w-5"
                        />
                      </div>
                    )}
                    <div>
                      <p className="font-medium">{project.name}</p>
                      <p className="text-xs text-muted-foreground">
                        {slideCounts[project.id] ?? project.slideCount ?? 0} {t.projects_slides} • {project.updatedAt ? new Date(new Date(project.updatedAt).getTime() + 7 * 60 * 60 * 1000).toLocaleString('vi-VN', { day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit', second: '2-digit' }) : ""}
                      </p>
                    </div>
                  </div>
                  {!selectMode && (
                    <div className="flex items-center gap-1">
                      <Button variant="ghost" size="sm" onClick={(e) => { e.stopPropagation(); navigate(`/view/${project.id}`); }}>
                        <Eye className="mr-1 h-3 w-3" /> {t.projects_view}
                      </Button>
                      <Button variant="ghost" size="sm" onClick={(e) => { e.stopPropagation(); navigate(`/editor?project=${project.id}`); }}>
                        <Edit className="mr-1 h-3 w-3" /> {t.projects_edit}
                      </Button>
                      <Button variant="ghost" size="sm" onClick={(e) => { e.stopPropagation(); setRenameId(project.id); setRenameName(project.name); }}>
                        <FileText className="mr-1 h-3 w-3" /> {t.projects_rename}
                      </Button>
                      <Button variant="ghost" size="sm" className="text-destructive" onClick={(e) => { e.stopPropagation(); setDeleteId(project.id); }}>
                        <Trash2 className="mr-1 h-3 w-3" /> {t.projects_delete}
                      </Button>
                    </div>
                  )}
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>

      {/* Delete dialog */}
      <Dialog open={!!deleteId} onOpenChange={() => setDeleteId(null)}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>{t.projects_delete_title}</DialogTitle>
            <DialogDescription>{t.projects_delete_desc}</DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button variant="outline" onClick={() => setDeleteId(null)}>{t.projects_cancel}</Button>
            <Button variant="destructive" onClick={handleDelete}>{t.projects_delete}</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Rename dialog */}
      <Dialog open={!!renameId} onOpenChange={() => setRenameId(null)}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>{t.projects_rename_title}</DialogTitle>
            <DialogDescription>{t.projects_rename_desc}</DialogDescription>
          </DialogHeader>
          <Input value={renameName} onChange={(e) => setRenameName(e.target.value)} placeholder={t.projects_name_placeholder} />
          <DialogFooter>
            <Button variant="outline" onClick={() => setRenameId(null)}>{t.projects_cancel}</Button>
            <Button onClick={handleRename}>{t.projects_save}</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Bulk delete dialog */}
      <Dialog open={bulkDeleteOpen} onOpenChange={() => setBulkDeleteOpen(false)}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>{t.projects_delete_title} ({selectedIds.size})</DialogTitle>
            <DialogDescription>
              {t.projects_delete_desc}
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button variant="outline" onClick={() => setBulkDeleteOpen(false)}>{t.projects_cancel}</Button>
            <Button variant="destructive" onClick={handleBulkDelete}>{t.projects_delete_all}</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </AppLayout>
  );
};

export default Projects;
