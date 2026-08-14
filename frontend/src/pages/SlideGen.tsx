import { useState, useRef, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { Upload, Lightbulb, Sparkles, Lock, Crown } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Switch } from "@/components/ui/switch";
import { Label } from "@/components/ui/label";
import { useToast } from "@/hooks/use-toast";
import { api } from "@/lib/api";
import type { OutputFormat } from "@/lib/api";
import { AppLayout } from "@/components/AppLayout";
import { useLanguage } from "@/contexts/LanguageContext";
import { useAuth } from "@/contexts/AuthContext";

const SlideGen = () => {
  const navigate = useNavigate();
  const { toast } = useToast();
  const { t } = useLanguage();
  const { isAuthenticated } = useAuth();

  const workflowModes = [
    { id: "auto_heading", label: t.slidegen_workflow_auto_heading, desc: t.slidegen_workflow_auto_heading_desc },
    { id: "auto_no_heading", label: t.slidegen_workflow_auto_no_heading, desc: t.slidegen_workflow_auto_no_heading_desc },
    { id: "manual", label: t.slidegen_workflow_manual, desc: t.slidegen_workflow_manual_desc },
  ];

  const docxRef = useRef<HTMLInputElement>(null);


  const [workflowMode, setWorkflowMode] = useState("auto_heading");
  const [ideaTitle, setIdeaTitle] = useState("");
  const [ideaDescription, setIdeaDescription] = useState("");
  const [ideaContentLength, setIdeaContentLength] = useState("standard");
  const [outputFormat] = useState<OutputFormat>("xml");
  const [isUploading, setIsUploading] = useState(false);
  const [processing, setProcessing] = useState(false);
  const [subscriptionTier, setSubscriptionTier] = useState<string>("free");

  useEffect(() => {
    if (isAuthenticated) {
      api.getSubscriptionInfo().then((info: any) => {
        setSubscriptionTier(info.tier || "free");
      }).catch(() => {});
    }
  }, [isAuthenticated]);

  const tierOrder: Record<string, number> = { free: 0, plus: 1, ultra: 2 };
  const isLocked = (requiredTier: string) =>
    (tierOrder[subscriptionTier] ?? 0) < (tierOrder[requiredTier] ?? 0);

  const contentLengths = [
    { id: "brief",     label: t.slidegen_length_brief,     slides: "5-8",   requiredTier: "free" },
    { id: "standard",  label: t.slidegen_length_standard,  slides: "8-12",  requiredTier: "free" },
    { id: "detailed",  label: t.slidegen_length_detailed,  slides: "12-18", requiredTier: "plus" },
    { id: "extensive", label: t.slidegen_length_extensive,  slides: "18-25", requiredTier: "ultra" },
  ];

  const handleDocxUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setIsUploading(true);
    try {
      if (workflowMode === "manual") {
        // Manual mode: upload for structure editing
        const res = await api.uploadDocxForManual(file, { outputFormat });
        toast({ title: t.slidegen_toast_success, description: t.slidegen_toast_opening_structure });
        navigate(`/structure?session=${res.session_id}`);
      } else {
        // Auto modes: upload for streaming workflow
        const res = await api.uploadDocxForStream(file, {
          workflow_mode: workflowMode,
          outputFormat,
        });
        toast({ title: t.slidegen_toast_success, description: t.slidegen_toast_starting });
        navigate(`/streaming/docx`, { state: { filename: res.filename } });
      }
    } catch (err: any) {
      const isRateLimit = err.status === 429;
      const rawMsg = (err.message || "").toLowerCase();
      const isAuth = rawMsg.includes('authentication') || rawMsg.includes('unauthorized') || rawMsg.includes('not auth');
      toast({
        title: isRateLimit ? t.error_rate_limit_title : t.error_upload_title,
        description: isRateLimit ? t.error_rate_limit_desc : (isAuth ? t.error_auth_required : undefined),
        variant: "destructive"
      });
    } finally {
      setIsUploading(false);
    }
  };



  const handleCreateFromIdea = async () => {
    if (!ideaTitle.trim()) {
      toast({ title: t.slidegen_toast_no_title, variant: "destructive" });
      return;
    }

    setProcessing(true);
    try {
      // Generate structure first
      const response = await api.generateIdeaStructure({
        title: ideaTitle.trim(),
        prompt: ideaDescription.trim(),
        content_length: ideaContentLength,
        output_format: outputFormat,
      });

      // Convert idea JSON into manual structure session (L0/L1 blocks) and open StructureEditor.
      const manualSession = await api.convertIdeaToManualSession(response.session_id);
      toast({ title: t.slidegen_toast_success, description: t.slidegen_toast_opening_structure });
      navigate(`/structure?session=${manualSession.session_id}`);
    } catch (err: any) {
      const isRateLimit = err.status === 429;
      const rawMsg = (err.message || "").toLowerCase();
      const isAuth = rawMsg.includes('authentication') || rawMsg.includes('unauthorized') || rawMsg.includes('not auth');
      toast({
        title: isRateLimit ? t.error_rate_limit_title : t.error_generate_title,
        description: isRateLimit ? t.error_rate_limit_desc : (isAuth ? t.error_auth_required : undefined),
        variant: "destructive"
      });
    } finally {
      setProcessing(false);
    }
  };

  return (
    <AppLayout>
      <div className="relative overflow-hidden">
        {/* Hero */}
        <section className="relative px-4 py-20 lg:py-32">
          <div className="absolute inset-0 gradient-primary opacity-10" />
          <div className="absolute -top-40 -right-40 h-96 w-96 rounded-full bg-primary/20 blur-3xl animate-float" />
          <div className="absolute -bottom-40 -left-40 h-96 w-96 rounded-full bg-accent/20 blur-3xl animate-float" style={{ animationDelay: "3s" }} />

          <div className="relative mx-auto max-w-4xl text-center">
            <div className="mb-4 inline-flex items-center gap-2 rounded-full border border-border bg-card/50 px-4 py-1.5 text-sm backdrop-blur">
              <Sparkles className="h-4 w-4 text-primary" />
              {t.slidegen_badge}
            </div>
            <h1 className="mb-6 text-4xl font-extrabold tracking-tight sm:text-5xl lg:text-6xl">
              {t.slidegen_h1} <br />
              <span className="gradient-text">{t.slidegen_h1_span}</span>
            </h1>
            <p className="mx-auto mb-10 max-w-2xl text-lg text-muted-foreground">
              {t.slidegen_sub}
            </p>
          </div>
        </section>

        {/* Action cards */}
        <section className="relative mx-auto max-w-6xl px-4 pb-20">
          <div className="grid gap-6 md:grid-cols-2">
            {/* Create from Document (DOCX) */}
            <Card className="group glass transition-all hover:shadow-xl">
              <CardHeader>
                <div className="mb-3 flex h-12 w-12 items-center justify-center rounded-xl gradient-primary">
                  <Upload className="h-6 w-6 text-primary-foreground" />
                </div>
                <CardTitle>{t.slidegen_upload_title}</CardTitle>
                <CardDescription>{t.slidegen_upload_desc}</CardDescription>
              </CardHeader>
              <CardContent className="space-y-5">
                {/* Workflow modes */}
                <div>
                  <Label className="mb-2 block text-sm font-medium">{t.slidegen_workflow}</Label>
                  <div className="grid gap-2 sm:grid-cols-3">
                    {workflowModes.map((mode) => (
                      <button
                        key={mode.id}
                        onClick={() => setWorkflowMode(mode.id)}
                        className={`rounded-lg border p-2.5 text-left transition-all ${
                          workflowMode === mode.id
                            ? "border-primary bg-primary/10 ring-2 ring-primary/20"
                            : "border-border hover:border-primary/50"
                        }`}
                      >
                        <p className="text-sm font-medium">{mode.label}</p>
                        <p className="mt-0.5 text-xs text-muted-foreground">{mode.desc}</p>
                      </button>
                    ))}
                  </div>
                </div>

                {/* Upload button */}
                <input ref={docxRef} type="file" accept=".docx" className="hidden" onChange={handleDocxUpload} />
                <Button className="w-full gradient-primary text-primary-foreground" disabled={isUploading} onClick={() => docxRef.current?.click()}>
                  {isUploading ? t.slidegen_uploading : t.slidegen_choose_file} <Upload className="ml-2 h-4 w-4" />
                </Button>
              </CardContent>
            </Card>

            {/* Create from Idea */}
            <Card className="group glass transition-all hover:shadow-xl">
              <CardHeader>
                <div className="mb-3 flex h-12 w-12 items-center justify-center rounded-xl bg-accent">
                  <Lightbulb className="h-6 w-6 text-accent-foreground" />
                </div>
                <CardTitle>{t.slidegen_idea_title}</CardTitle>
                <CardDescription>{t.slidegen_idea_desc}</CardDescription>
              </CardHeader>
              <CardContent className="space-y-5">
                <Input placeholder={t.slidegen_idea_title_ph} value={ideaTitle} onChange={(e) => setIdeaTitle(e.target.value)} />
                <textarea
                  placeholder={t.slidegen_idea_desc_ph}
                  value={ideaDescription}
                  onChange={(e) => setIdeaDescription(e.target.value)}
                  className="flex min-h-[100px] w-full rounded-md border border-input bg-background px-3 py-2 text-sm placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
                />

                {/* Content Length */}
                <div>
                  <Label className="mb-2 block text-sm font-medium">{t.slidegen_length_label}</Label>
                  <div className="grid grid-cols-4 gap-2">
                    {contentLengths.map((len) => {
                      const locked = isLocked(len.requiredTier);
                      return (
                        <button
                          key={len.id}
                          title={locked ? (len.requiredTier === "ultra" ? t.plan_requires_ultra : t.plan_requires_plus) : undefined}
                          onClick={() => {
                            if (locked) {
                              toast({
                                title: len.requiredTier === "ultra" ? t.plan_requires_ultra : t.plan_requires_plus,
                                description: t.plan_slide_limit_desc,
                                variant: "destructive",
                              });
                              return;
                            }
                            setIdeaContentLength(len.id);
                          }}
                          className={`relative rounded-lg border p-2 text-center transition-all ${
                            locked
                              ? "border-border opacity-50 cursor-not-allowed"
                              : ideaContentLength === len.id
                              ? "border-primary bg-primary/10 ring-2 ring-primary/20"
                              : "border-border hover:border-primary/50"
                          }`}
                        >
                          {locked && (
                            <div className="absolute top-1 right-1">
                              {len.requiredTier === "ultra"
                                ? <Crown className="h-3 w-3 text-yellow-500" />
                                : <Lock className="h-3 w-3 text-muted-foreground" />}
                            </div>
                          )}
                          <p className="text-sm font-medium">{len.label}</p>
                          <p className="text-xs text-muted-foreground">{len.slides} slides</p>
                        </button>
                      );
                    })}
                  </div>
                </div>

                <Button className="w-full gradient-primary text-primary-foreground" onClick={handleCreateFromIdea} disabled={processing}>
                  {processing ? (
                    <>
                      <div className="mr-2 h-4 w-4 animate-spin rounded-full border-2 border-white/30 border-t-white" />
                      Generating...
                    </>
                  ) : (
                    <>
                      {t.slidegen_generate} <Sparkles className="ml-2 h-4 w-4" />
                    </>
                  )}
                </Button>
              </CardContent>
            </Card>
          </div>
        </section>
      </div>
    </AppLayout>
  );
};

export default SlideGen;
