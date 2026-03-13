import { useEffect, useState, useRef } from "react";
import { AppLayout } from "@/components/AppLayout";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { cn } from "@/lib/utils";

const sections = [
  { id: "overview", title: "System Overview", content: "SlideGen is an AI-powered slide generation platform. Upload documents, describe ideas, or import existing projects — and let AI transform your content into beautiful presentations.\n\nThe platform supports multiple workflow modes, real-time streaming generation, a full WYSIWYG slide editor, and presentation mode." },
  { id: "workflows", title: "Workflow Modes", content: "**Auto with Heading**: Automatically detects headings in your document and uses them as slide breaks. Best for well-structured documents.\n\n**Auto without Heading**: AI analyzes your content and determines the optimal slide structure. Great for unstructured text.\n\n**Manual Structure**: Review and edit the document structure before generation. Full control over what goes on each slide." },
  { id: "structure", title: "Structure Editor", content: "The Structure Editor lets you organize content before slide generation:\n\n• Apply hierarchy levels (L0-L6)\n• Set block type: Title or Content\n• Drag and reorder text blocks\n• Add intro and transition slides\n• Find and replace text in-place\n• Use zoom controls for easier editing\n• Preview your structure in real time\n• Approve when ready to generate\n\nValidation before Approve:\n• Empty block detection\n• Missing level-1 title detection\n• Invalid level jump detection (example: L1 -> L4)\n• Error blocks are highlighted so you can fix quickly" },
  { id: "manual-tips", title: "Manual Editor Quick Start", content: "Recommended workflow:\n\n1. Upload DOCX and open Structure Editor\n2. Assign level and type to key blocks first\n3. Use Find (Ctrl+F) to locate section names quickly\n4. Reorder blocks with drag handle\n5. Review slide previews\n6. Fix validation errors if any\n7. Approve and continue to design\n\nSaving and safety:\n• Auto-save runs in the background\n• Status chip shows Saved, Saving..., or Unsaved changes\n• Browser warns you before closing tab with unsaved changes" },
  { id: "editor", title: "Slide Editor", content: "The WYSIWYG Slide Editor provides full visual control:\n\n• Drag, resize, and rotate elements on the canvas\n• Add text, images, shapes, icons, and connectors\n• Grid snapping and alignment guides\n• Zoom and pan controls\n• Properties panel for precise positioning\n• Slides panel for managing slide order" },
  { id: "shortcuts", title: "Keyboard Shortcuts", content: "Structure Editor shortcuts:\n\nGlobal:\n• Ctrl+F - Open Find\n• Ctrl+H - Open Find and Replace\n• Ctrl+S - Save now\n• Ctrl+Enter - Open Approve dialog\n• Escape - Close Find panel\n\nInside editor:\n• Ctrl+Z - Undo\n• Ctrl+Y - Redo\n• Ctrl+B - Bold\n• Ctrl+I - Italic\n• Ctrl+U - Underline\n• Tab - Increase selected block level\n• Shift+Tab - Decrease selected block level\n• Alt+0..6 - Set level quickly\n• Alt+T - Set type Title\n• Alt+C - Set type Content\n\nSlide editor shortcuts:\n• Ctrl+Z - Undo\n• Ctrl+Y - Redo\n• Delete - Remove selected element\n\nPresentation shortcuts:\n• Right arrow or Space - Next slide\n• Left arrow - Previous slide\n• Escape - Exit presentation\n• Click left side - Previous\n• Click right side - Next" },
  { id: "troubleshooting", title: "Troubleshooting", content: "Common issues and quick fixes:\n\n1) Cannot approve structure\n• Cause: Validation errors exist\n• Fix: Check highlighted red blocks and fix in this order:\n  - Remove empty block content\n  - Add missing title for level-1 slide\n  - Fix level jump (for example L1 -> L2 -> L3, avoid L1 -> L4)\n\n2) Unsaved changes warning appears when leaving\n• Cause: Recent edits are not saved yet\n• Fix: Press Ctrl+S and wait until status shows Saved\n\n3) Find shows 0 results\n• Cause: Wrong keyword or case sensitivity enabled\n• Fix: Disable Aa mode or try shorter keyword\n\n4) Tab does not change level\n• Cause: Focus is outside the structure editor\n• Fix: Click inside editor block, then press Tab or Shift+Tab\n\n5) Text formatting shortcut not working\n• Cause: Cursor is not inside editable block\n• Fix: Place cursor in content area, then use Ctrl+B/Ctrl+I/Ctrl+U\n\n6) Drag and drop feels hard on long documents\n• Fix: Use Find first (Ctrl+F), then drag by handle to target area\n\nSupport checklist before reporting:\n• Session ID exists in URL\n• Status is Saved\n• Validation panel has no errors\n• Browser tab is not blocked by extension scripts" },
  { id: "faq", title: "FAQ", content: "**Q: What file formats are supported?**\nA: DOCX for document upload, ZIP for project import. Export to PDF and ZIP.\n\n**Q: Can I edit slides after generation?**\nA: Yes! The WYSIWYG editor gives you full control over every element.\n\n**Q: Is my data saved automatically?**\nA: Yes, the editor auto-saves your changes every few seconds.\n\n**Q: How does the AI generation work?**\nA: We use advanced AI models to analyze your content, structure it into slides, and generate professional designs." },
];

const Guide = () => {
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
          <h3 className="mb-3 text-sm font-semibold text-muted-foreground">Contents</h3>
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
