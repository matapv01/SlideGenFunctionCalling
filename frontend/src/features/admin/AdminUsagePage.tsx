import { useCallback, useEffect, useMemo, useState } from "react";
import { useLanguage } from "@/contexts/LanguageContext";
import { api, type AdminPlanLimit, type AdminUsageConfigResponse } from "@/lib/api";
import SlidegeniusWorkspaceShell from "@/features/slidegenius/SlidegeniusWorkspaceShell";
import SlidegenConfirmDialog from "@/components/SlidegenConfirmDialog";
import AdminUsersPanel from "./AdminUsersPanel";
import "./admin-usage.css";

type WeightGroup = "model_weights" | "effort_weights";
type PlanDraft = Record<string, {
  chat_credits: string;
  docx_upload: string;
  max_docx_slides: string;
  max_docx_file_mb: string;
  max_docx_total_mb: string;
}>;
type AdminSection = "usage" | "users";

const copy = {
  en: {
    eyebrow: "ADMIN / USAGE CONTROL",
    title: "Usage control",
    subtitle: "Tune weighted chat credits and reset the active five-hour window for every account.",
    models: "Model cost",
    modelsSub: "Relative cost of one chat turn by model.",
    efforts: "Effort cost",
    effortsSub: "Higher effort consumes more weighted credits.",
    plans: "Plan limits",
    plansSub: "The current limits used by the subscription service.",
    window: "Usage window",
    hours: "hours",
    weight: "Usage percentage",
    multiplier: "Effective multiplier",
    save: "Save changes",
    saving: "Saving...",
    saved: "Usage policy saved.",
    reset: "Reset all users",
    resetting: "Resetting...",
    resetConfirm: "Reset usage for every user? This clears the current five-hour chat and DOCX counters.",
    resetDone: "Usage reset for all users.",
    loadError: "Unable to load admin usage configuration.",
    saveError: "Unable to save usage configuration.",
    resetError: "Unable to reset usage.",
    percentageHint: "Allowed range: 10%–500%.",
    limitHint: "Use -1 for unlimited counts. DOCX limits are MB per file and per conversation; the file limit cannot exceed the conversation limit.",
    plan: "Plan",
    chat: "Chat credits / 5h",
    docx: "DOCX / 5h",
    docxFile: "DOCX max / file (MB)",
    docxTotal: "DOCX max / conversation (MB)",
    slides: "Max slides",
    unlimited: "Unlimited",
    messages: "Weighted credits are charged at send time using model × effort.",
    usageTab: "Usage policy",
    usersTab: "User management",
  },
  vi: {
    eyebrow: "ADMIN / KIỂM SOÁT USAGE",
    title: "Kiểm soát usage",
    subtitle: "Điều chỉnh credit chat theo trọng số và reset cửa sổ 5 giờ cho toàn bộ tài khoản.",
    models: "Chi phí model",
    modelsSub: "Chi phí tương đối của một lượt chat theo model.",
    efforts: "Chi phí effort",
    effortsSub: "Effort cao sẽ tiêu tốn nhiều weighted credit hơn.",
    plans: "Giới hạn plan",
    plansSub: "Các giới hạn hiện được subscription service sử dụng.",
    window: "Cửa sổ usage",
    hours: "giờ",
    weight: "Phần trăm usage",
    multiplier: "Hệ số thực tế",
    save: "Lưu thay đổi",
    saving: "Đang lưu...",
    saved: "Đã lưu chính sách usage.",
    reset: "Reset toàn bộ user",
    resetting: "Đang reset...",
    resetConfirm: "Reset usage cho toàn bộ user? Thao tác này xóa bộ đếm chat và DOCX trong cửa sổ 5 giờ hiện tại.",
    resetDone: "Đã reset usage cho toàn bộ user.",
    loadError: "Không thể tải cấu hình usage admin.",
    saveError: "Không thể lưu cấu hình usage.",
    resetError: "Không thể reset usage.",
    percentageHint: "Khoảng cho phép: 10%–500%.",
    limitHint: "Dùng -1 cho số lượng không giới hạn. Giới hạn DOCX tính theo MB/file và MB/cuộc trò chuyện; giới hạn file không được lớn hơn giới hạn cuộc trò chuyện.",
    plan: "Plan",
    chat: "Chat credit / 5 giờ",
    docx: "DOCX / 5 giờ",
    docxFile: "DOCX tối đa / file (MB)",
    docxTotal: "DOCX tối đa / cuộc trò chuyện (MB)",
    slides: "Số slide tối đa",
    unlimited: "Không giới hạn",
    messages: "Credit được tính lúc gửi theo công thức model × effort.",
    usageTab: "Chính sách usage",
    usersTab: "Quản lý user",
  },
} as const;

function displayName(id: string) {
  if (id.startsWith("genius-")) return id.replace("genius-", "Genius ");
  return id.charAt(0).toUpperCase() + id.slice(1);
}

function formatMultiplier(value: number) {
  return `×${value.toFixed(2).replace(/0+$/, "").replace(/\.$/, "")}`;
}

function toDraft(config: AdminUsageConfigResponse | null, group: WeightGroup): Record<string, string> {
  return Object.fromEntries((config?.[group] ?? []).map((item) => [item.id, String(item.percentage)]));
}

function toPlanDraft(config: AdminUsageConfigResponse | null): PlanDraft {
  return Object.fromEntries(
    Object.entries(config?.plan_limits ?? {}).map(([tier, limits]) => [tier, {
      chat_credits: String(limits.chat_credits),
      docx_upload: String(limits.docx_upload),
      max_docx_slides: String(limits.max_docx_slides),
      max_docx_file_mb: String(limits.max_docx_file_mb),
      max_docx_total_mb: String(limits.max_docx_total_mb),
    }]),
  );
}

function AdminSectionTabs({ activeSection, onChange, usageLabel, usersLabel }: {
  activeSection: AdminSection;
  onChange: (section: AdminSection) => void;
  usageLabel: string;
  usersLabel: string;
}) {
  return (
    <div className="admin-section-tabs" role="tablist" aria-label="Admin sections">
      <button type="button" className={activeSection === "usage" ? "active" : ""} onClick={() => onChange("usage")} role="tab" aria-selected={activeSection === "usage"}>
        {usageLabel}
      </button>
      <button type="button" className={activeSection === "users" ? "active" : ""} onClick={() => onChange("users")} role="tab" aria-selected={activeSection === "users"}>
        {usersLabel}
      </button>
    </div>
  );
}

export default function AdminUsagePage() {
  const { language } = useLanguage();
  const t = copy[language];
  const [config, setConfig] = useState<AdminUsageConfigResponse | null>(null);
  const [modelDraft, setModelDraft] = useState<Record<string, string>>({});
  const [effortDraft, setEffortDraft] = useState<Record<string, string>>({});
  const [planDraft, setPlanDraft] = useState<PlanDraft>({});
  const [activeSection, setActiveSection] = useState<AdminSection>("usage");
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [resetting, setResetting] = useState(false);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [resetDialogOpen, setResetDialogOpen] = useState(false);

  const loadConfig = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const next = await api.getAdminUsageConfig();
      setConfig(next);
      setModelDraft(toDraft(next, "model_weights"));
      setEffortDraft(toDraft(next, "effort_weights"));
      setPlanDraft(toPlanDraft(next));
    } catch (loadError) {
      setError(loadError instanceof Error ? loadError.message : t.loadError);
    } finally {
      setLoading(false);
    }
  }, [t.loadError]);

  useEffect(() => {
    void loadConfig();
  }, [loadConfig]);

  const planRows = useMemo(() => Object.entries(config?.plan_limits ?? {}), [config]);

  const handleSave = async () => {
    const modelPercentages = Object.fromEntries(
      Object.entries(modelDraft).map(([id, value]) => [id, Number(value)]),
    );
    const effortPercentages = Object.fromEntries(
      Object.entries(effortDraft).map(([id, value]) => [id, Number(value)]),
    );
    const planLimits = Object.fromEntries(
      Object.entries(planDraft).map(([tier, values]) => [tier, {
        chat_credits: Number(values.chat_credits),
        docx_upload: Number(values.docx_upload),
        max_docx_slides: Number(values.max_docx_slides),
        max_docx_file_mb: Number(values.max_docx_file_mb),
        max_docx_total_mb: Number(values.max_docx_total_mb),
      } satisfies AdminPlanLimit]),
    );
    const allValues = [...Object.values(modelPercentages), ...Object.values(effortPercentages)];
    if (allValues.some((value) => !Number.isFinite(value) || value < 10 || value > 500)) {
      setError(t.percentageHint);
      setMessage("");
      return;
    }
    const invalidPlanLimit = Object.values(planLimits).some((limits) => (
      !Number.isFinite(limits.chat_credits)
      || (limits.chat_credits < 0 && limits.chat_credits !== -1)
      || !Number.isInteger(limits.docx_upload)
      || limits.docx_upload < -1
      || !Number.isInteger(limits.max_docx_slides)
      || limits.max_docx_slides < -1
      || !Number.isInteger(limits.max_docx_file_mb)
      || !Number.isInteger(limits.max_docx_total_mb)
      || limits.max_docx_file_mb < 1
      || limits.max_docx_total_mb < 1
      || limits.max_docx_file_mb > limits.max_docx_total_mb
    ));
    if (invalidPlanLimit) {
      setError(t.limitHint);
      setMessage("");
      return;
    }

    setSaving(true);
    setError("");
    setMessage("");
    try {
      const next = await api.updateAdminUsageConfig({
        model_percentages: modelPercentages,
        effort_percentages: effortPercentages,
        plan_limits: planLimits,
      });
      setConfig(next);
      setModelDraft(toDraft(next, "model_weights"));
      setEffortDraft(toDraft(next, "effort_weights"));
      setPlanDraft(toPlanDraft(next));
      setMessage(t.saved);
    } catch (saveError) {
      setError(saveError instanceof Error ? saveError.message : t.saveError);
    } finally {
      setSaving(false);
    }
  };

  const handleReset = () => {
    if (resetting) return;
    setResetDialogOpen(true);
  };

  const confirmReset = async () => {
    setResetDialogOpen(false);
    setResetting(true);
    setError("");
    setMessage("");
    try {
      await api.resetAllUsage();
      setMessage(t.resetDone);
    } catch (resetError) {
      setError(resetError instanceof Error ? resetError.message : t.resetError);
    } finally {
      setResetting(false);
    }
  };

  const renderWeights = (group: WeightGroup, draft: Record<string, string>, setDraft: (value: Record<string, string>) => void) => (
    <div className="admin-usage-weight-list">
      {(config?.[group] ?? []).map((item) => (
        <label className="admin-usage-weight-row" key={item.id}>
          <span>
            <strong>{displayName(item.id)}</strong>
            <small>{t.multiplier} {formatMultiplier(item.multiplier)}</small>
          </span>
          <span className="admin-usage-input-wrap">
            <input
              type="number"
              min="10"
              max="500"
              step="1"
              value={draft[item.id] ?? ""}
              onChange={(event) => setDraft({ ...draft, [item.id]: event.target.value })}
              aria-label={`${displayName(item.id)} ${t.weight}`}
            />
            <i>%</i>
          </span>
        </label>
      ))}
    </div>
  );

  if (activeSection === "users") {
    return (
      <SlidegeniusWorkspaceShell activeTab="admin">
        <section className="workspace-panel admin-usage-panel">
          <AdminSectionTabs activeSection={activeSection} onChange={setActiveSection} usageLabel={t.usageTab} usersLabel={t.usersTab} />
          <AdminUsersPanel />
        </section>
      </SlidegeniusWorkspaceShell>
    );
  }

  return (
    <SlidegeniusWorkspaceShell activeTab="admin">
      <section className="workspace-panel admin-usage-panel">
        <AdminSectionTabs activeSection={activeSection} onChange={setActiveSection} usageLabel={t.usageTab} usersLabel={t.usersTab} />
        <div className="admin-usage-header">
          <div>
            <p className="workspace-eyebrow">{t.eyebrow}</p>
            <h2>{t.title}</h2>
            <p className="guide-lead">{t.subtitle}</p>
          </div>
          <div className="admin-usage-actions">
            <span className="admin-usage-window">{t.window}: <strong>{config?.usage_window_hours ?? "—"} {t.hours}</strong></span>
            <button type="button" className="admin-usage-reset" onClick={handleReset} disabled={loading || resetting}>
              {resetting ? t.resetting : t.reset}
            </button>
          </div>
        </div>

        {loading ? <div className="admin-usage-state">Loading...</div> : (
          <>
            <div className="admin-usage-grid">
              <article className="admin-usage-card">
                <div className="admin-usage-card-heading"><div><h3>{t.models}</h3><p>{t.modelsSub}</p></div><span>MODEL</span></div>
                {renderWeights("model_weights", modelDraft, setModelDraft)}
              </article>
              <article className="admin-usage-card">
                <div className="admin-usage-card-heading"><div><h3>{t.efforts}</h3><p>{t.effortsSub}</p></div><span>EFFORT</span></div>
                {renderWeights("effort_weights", effortDraft, setEffortDraft)}
              </article>
            </div>

            <article className="admin-usage-card admin-usage-plan-card">
              <div className="admin-usage-card-heading"><div><h3>{t.plans}</h3><p>{t.plansSub}</p></div><span>PLANS</span></div>
              <div className="admin-usage-table-wrap">
                <table className="admin-usage-table">
                  <thead><tr><th>{t.plan}</th><th>{t.chat}</th><th>{t.docx}</th><th>{t.docxFile}</th><th>{t.docxTotal}</th><th>{t.slides}</th></tr></thead>
                  <tbody>{planRows.map(([name]) => {
                    const draft = planDraft[name] ?? { chat_credits: "", docx_upload: "", max_docx_slides: "", max_docx_file_mb: "", max_docx_total_mb: "" };
                    const update = (field: keyof PlanDraft[string], value: string) => {
                      setPlanDraft((current) => ({
                        ...current,
                        [name]: { ...draft, ...current[name], [field]: value },
                      }));
                    };
                    return (
                      <tr key={name}>
                        <th>{displayName(name)}</th>
                        <td><input className="admin-usage-plan-input" type="number" min="-1" step="0.1" value={draft.chat_credits} onChange={(event) => update("chat_credits", event.target.value)} aria-label={`${displayName(name)} ${t.chat}`} /></td>
                        <td><input className="admin-usage-plan-input" type="number" min="-1" step="1" value={draft.docx_upload} onChange={(event) => update("docx_upload", event.target.value)} aria-label={`${displayName(name)} ${t.docx}`} /></td>
                        <td><input className="admin-usage-plan-input" type="number" min="1" step="1" value={draft.max_docx_file_mb} onChange={(event) => update("max_docx_file_mb", event.target.value)} aria-label={`${displayName(name)} ${t.docxFile}`} /></td>
                        <td><input className="admin-usage-plan-input" type="number" min="1" step="1" value={draft.max_docx_total_mb} onChange={(event) => update("max_docx_total_mb", event.target.value)} aria-label={`${displayName(name)} ${t.docxTotal}`} /></td>
                        <td><input className="admin-usage-plan-input" type="number" min="-1" step="1" value={draft.max_docx_slides} onChange={(event) => update("max_docx_slides", event.target.value)} aria-label={`${displayName(name)} ${t.slides}`} /></td>
                      </tr>
                    );
                  })}</tbody>
                </table>
              </div>
            </article>

            <div className="admin-usage-footer">
              <p>{t.messages} <span>{t.percentageHint}</span><span>{t.limitHint}</span></p>
              <button type="button" className="panel-primary" onClick={handleSave} disabled={saving}>{saving ? t.saving : t.save}<span>↗</span></button>
            </div>
          </>
        )}

        {message && <p className="admin-usage-message">{message}</p>}
        {error && <p className="admin-usage-error">{error}</p>}
        <SlidegenConfirmDialog
          open={resetDialogOpen}
          onOpenChange={setResetDialogOpen}
          title={language === "vi" ? "Reset usage toàn bộ user?" : "Reset usage for every user?"}
          description={t.resetConfirm}
          confirmLabel={t.reset}
          cancelLabel={language === "vi" ? "Hủy" : "Cancel"}
          onConfirm={() => void confirmReset()}
          destructive
          busy={resetting}
        />
      </section>
    </SlidegeniusWorkspaceShell>
  );
}
