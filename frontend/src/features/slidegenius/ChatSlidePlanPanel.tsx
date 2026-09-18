interface ChatSlidePlanAnswer {
  question: string;
  answer: string;
}

interface ChatSlidePlanPanelProps {
  originalPrompt: string;
  brief: string;
  answers: ChatSlidePlanAnswer[];
  targetSlideCount: number | null;
  maxSlideCount: number;
  model: string;
  effort: string;
  document: string | null;
  title: string;
  closeLabel: string;
  requestLabel: string;
  briefLabel: string;
  answersLabel: string;
  sourceLabel: string;
  settingsLabel: string;
  noAnswersLabel: string;
  noBriefLabel: string;
  slideCountLabel: string;
  slideLimitLabel: string;
  slideCountNotSet: string;
  slideCountUnlimited: string;
  modelLabel: string;
  effortLabel: string;
  onClose: () => void;
}

export function ChatSlidePlanPanel({
  originalPrompt,
  brief,
  answers,
  targetSlideCount,
  maxSlideCount,
  model,
  effort,
  document,
  title,
  closeLabel,
  requestLabel,
  briefLabel,
  answersLabel,
  sourceLabel,
  settingsLabel,
  noAnswersLabel,
  noBriefLabel,
  slideCountLabel,
  slideLimitLabel,
  slideCountNotSet,
  slideCountUnlimited,
  modelLabel,
  effortLabel,
  onClose,
}: ChatSlidePlanPanelProps) {
  return (
    <aside className="chat-slide-stream-panel chat-slide-plan-panel" aria-live="polite">
      <div className="chat-slide-stream-header">
        <div>
          <p className="chat-slide-stream-eyebrow">SLIDE PLAN</p>
          <h3>{title}</h3>
        </div>
        <button type="button" aria-label={closeLabel} title={closeLabel} onClick={onClose}>×</button>
      </div>

      <div className="chat-slide-plan-body">
        <section className="chat-slide-plan-section">
          <p className="chat-slide-plan-label">{requestLabel}</p>
          <p className="chat-slide-plan-copy">{originalPrompt || noBriefLabel}</p>
        </section>

        <section className="chat-slide-plan-section chat-slide-plan-count">
          <p className="chat-slide-plan-label">{slideCountLabel}</p>
          <div className="chat-slide-plan-count-grid">
            <strong>{targetSlideCount ?? slideCountNotSet}</strong>
            <span>{slideLimitLabel}: {maxSlideCount === -1 ? slideCountUnlimited : maxSlideCount}</span>
          </div>
        </section>

        <section className="chat-slide-plan-section">
          <p className="chat-slide-plan-label">{briefLabel}</p>
          <p className="chat-slide-plan-copy">{brief || noBriefLabel}</p>
        </section>

        <section className="chat-slide-plan-section">
          <p className="chat-slide-plan-label">{answersLabel}</p>
          {answers.length ? (
            <div className="chat-slide-plan-answers">
              {answers.map((item, index) => (
                <div className="chat-slide-plan-answer" key={`${item.question}-${index}`}>
                  {item.question && <span>{item.question}</span>}
                  <strong>{item.answer || "—"}</strong>
                </div>
              ))}
            </div>
          ) : <p className="chat-slide-plan-copy muted">{noAnswersLabel}</p>}
        </section>

        {document && (
          <section className="chat-slide-plan-section">
            <p className="chat-slide-plan-label">{sourceLabel}</p>
            <p className="chat-slide-plan-copy chat-slide-plan-document">{document}</p>
          </section>
        )}

        <section className="chat-slide-plan-section chat-slide-plan-settings">
          <p className="chat-slide-plan-label">{settingsLabel}</p>
          <div className="chat-slide-plan-setting-grid">
            <span><small>{modelLabel}</small><strong>{model}</strong></span>
            <span><small>{effortLabel}</small><strong>{effort}</strong></span>
          </div>
        </section>
      </div>
    </aside>
  );
}
