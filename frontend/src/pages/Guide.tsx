import { useEffect, useState, useRef } from "react";
import { AppLayout } from "@/components/AppLayout";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { cn } from "@/lib/utils";
import { useLanguage } from "@/contexts/LanguageContext";

const Guide = () => {
  const { t } = useLanguage();

  const sections = [
    { id: "overview", title: t.guide_overview_title, content: t.guide_overview_content },
    { id: "workflows", title: t.guide_workflows_title, content: t.guide_workflows_content },
    { id: "structure", title: t.guide_structure_title, content: t.guide_structure_content },
    { id: "editor", title: t.guide_editor_title, content: t.guide_editor_content },
    { id: "shortcuts", title: t.guide_shortcuts_title, content: t.guide_shortcuts_content },
    { id: "faq", title: t.guide_faq_title, content: t.guide_faq_content },
  ];

  const [activeSection, setActiveSection] = useState("overview");
  const contentRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const container = contentRef.current;
    if (!container) return;

    const observer = new IntersectionObserver(
      (entries) => {
        for (const entry of entries) {
          if (entry.isIntersecting) {
            setActiveSection(entry.target.id);
          }
        }
      },
      { root: container, rootMargin: "-20% 0% -60% 0%" }
    );

    sections.forEach((s) => {
      const el = document.getElementById(s.id);
      if (el) observer.observe(el);
    });

    return () => observer.disconnect();
  }, []);

  const scrollToSection = (id: string) => {
    const el = document.getElementById(id);
    if (el && contentRef.current) {
      el.scrollIntoView({ behavior: "smooth", block: "start" });
    }
  };

  return (
    <AppLayout>
      <div className="flex h-[calc(100vh-4rem)]">
        {/* Sidebar nav - sticky */}
        <nav className="hidden w-48 flex-shrink-0 border-r border-border p-4 lg:block overflow-y-auto">
          <h3 className="mb-3 text-sm font-semibold text-muted-foreground">{t.guide_contents}</h3>
          <div className="space-y-1">
            {sections.map((s) => (
              <button
                key={s.id}
                onClick={() => scrollToSection(s.id)}
                className={cn(
                  "block w-full text-left rounded-md px-3 py-1.5 text-sm transition-colors",
                  activeSection === s.id ? "bg-primary/10 text-primary font-medium" : "text-muted-foreground hover:text-foreground"
                )}
              >
                {s.title}
              </button>
            ))}
          </div>
        </nav>

        {/* Content - scrollable */}
        <div ref={contentRef} className="flex-1 overflow-y-auto px-4 py-8 lg:px-12">
          <h1 className="mb-8 text-3xl font-bold">
            <span className="gradient-text">{t.guide_title}</span>
          </h1>

          <div className="space-y-12">
            {sections.map((section) => (
              <section key={section.id} id={section.id}>
                <Card className="glass">
                  <CardHeader>
                    <CardTitle>{section.title}</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="prose prose-sm dark:prose-invert max-w-none whitespace-pre-line">
                      {section.content}
                    </div>
                  </CardContent>
                </Card>
              </section>
            ))}
          </div>
        </div>
      </div>
    </AppLayout>
  );
};

export default Guide;
