import { useEffect, useState } from "react";
import { AppLayout } from "@/components/AppLayout";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { cn } from "@/lib/utils";

const sections = [
  { id: "overview", title: "System Overview", content: "SlideGen is an AI-powered slide generation platform. Upload documents, describe ideas, or import existing projects — and let AI transform your content into beautiful presentations.\n\nThe platform supports multiple workflow modes, real-time streaming generation, a full WYSIWYG slide editor, and presentation mode." },
  { id: "workflows", title: "Workflow Modes", content: "**Auto with Heading**: Automatically detects headings in your document and uses them as slide breaks. Best for well-structured documents.\n\n**Auto without Heading**: AI analyzes your content and determines the optimal slide structure. Great for unstructured text.\n\n**Manual Structure**: Review and edit the document structure before generation. Full control over what goes on each slide." },
  { id: "structure", title: "Structure Editor", content: "The Structure Editor lets you organize your content before slide generation:\n\n• Apply hierarchy levels (0-7) to control nesting\n• Set content types: Title (blue), Content (green), Bullet (orange)\n• Drag and reorder text blocks\n• Add intro and transition slides\n• Preview your structure in real-time\n• Approve when ready to generate" },
  { id: "editor", title: "Slide Editor", content: "The WYSIWYG Slide Editor provides full visual control:\n\n• Drag, resize, and rotate elements on the canvas\n• Add text, images, shapes, icons, and connectors\n• Grid snapping and alignment guides\n• Zoom and pan controls\n• Properties panel for precise positioning\n• Slides panel for managing slide order" },
  { id: "shortcuts", title: "Keyboard Shortcuts", content: "**Editor:**\n• Ctrl+Z — Undo\n• Ctrl+Y — Redo\n• Delete — Remove selected element\n\n**Presentation:**\n• → / Space — Next slide\n• ← — Previous slide\n• Escape — Exit presentation\n• Click left side — Previous\n• Click right side — Next" },
  { id: "faq", title: "FAQ", content: "**Q: What file formats are supported?**\nA: DOCX for document upload, ZIP for project import. Export to PDF and ZIP.\n\n**Q: Can I edit slides after generation?**\nA: Yes! The WYSIWYG editor gives you full control over every element.\n\n**Q: Is my data saved automatically?**\nA: Yes, the editor auto-saves your changes every few seconds.\n\n**Q: How does the AI generation work?**\nA: We use advanced AI models to analyze your content, structure it into slides, and generate professional designs." },
];

const Guide = () => {
  const [activeSection, setActiveSection] = useState("overview");

  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        for (const entry of entries) {
          if (entry.isIntersecting) {
            setActiveSection(entry.target.id);
          }
        }
      },
      { rootMargin: "-20% 0% -60% 0%" }
    );

    sections.forEach((s) => {
      const el = document.getElementById(s.id);
      if (el) observer.observe(el);
    });

    return () => observer.disconnect();
  }, []);

  return (
    <AppLayout>
      <div className="flex">
        {/* Sidebar nav */}
        <nav className="hidden w-48 flex-shrink-0 border-r border-border p-4 lg:block">
          <h3 className="mb-3 text-sm font-semibold text-muted-foreground">Contents</h3>
          <div className="space-y-1">
            {sections.map((s) => (
              <a
                key={s.id}
                href={`#${s.id}`}
                className={cn(
                  "block rounded-md px-3 py-1.5 text-sm transition-colors",
                  activeSection === s.id ? "bg-primary/10 text-primary font-medium" : "text-muted-foreground hover:text-foreground"
                )}
              >
                {s.title}
              </a>
            ))}
          </div>
        </nav>

        {/* Content */}
        <div className="flex-1 overflow-auto px-4 py-8 lg:px-12">
          <h1 className="mb-8 text-3xl font-bold">
            <span className="gradient-text">SlideGen Guide</span>
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
