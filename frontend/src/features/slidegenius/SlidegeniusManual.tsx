import { ChangeEvent, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { FileText, Upload } from "lucide-react";
import { api } from "@/lib/api";
import { useLanguage } from "@/contexts/LanguageContext";
import { useToast } from "@/hooks/use-toast";

export default function SlidegeniusManual() {
  const navigate = useNavigate();
  const { language } = useLanguage();
  const { toast } = useToast();
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [uploading, setUploading] = useState(false);

  const text = language === "vi"
    ? {
        eyebrow: "MANUAL / STRUCTURE",
        title: "Tự xây dựng cấu trúc slide.",
        description: "Tải DOCX lên, chỉnh Markdown và xem preview từng slide trước khi chạy bộ máy thiết kế.",
        note: "Manual là một workflow độc lập. Nó không dùng lịch sử, tài liệu hay trạng thái của chatbot.",
        choose: "Chọn file DOCX",
        uploading: "Đang mở trình biên tập...",
        invalid: "Chỉ hỗ trợ file DOCX.",
        failed: "Không thể mở trình biên tập manual.",
      }
    : {
        eyebrow: "MANUAL / STRUCTURE",
        title: "Build the slide structure yourself.",
        description: "Upload a DOCX, edit its Markdown, and review each slide before running the design engine.",
        note: "Manual is an independent workflow. It does not share chatbot history, documents, or state.",
        choose: "Choose DOCX file",
        uploading: "Opening editor...",
        invalid: "Only DOCX files are supported.",
        failed: "Unable to open the manual editor.",
      };

  const handleSelected = async (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    event.target.value = "";
    if (!file || uploading) return;
    if (!file.name.toLowerCase().endsWith(".docx")) {
      toast({ title: text.invalid, variant: "destructive" });
      return;
    }

    setUploading(true);
    try {
      const result = await api.uploadDocxForManual(file, { outputFormat: "xml" });
      navigate(`/structure?session=${encodeURIComponent(result.session_id)}`);
    } catch (error) {
      toast({
        title: text.failed,
        description: error instanceof Error ? error.message : undefined,
        variant: "destructive",
      });
    } finally {
      setUploading(false);
    }
  };

  return (
    <section className="workspace-panel manual-panel">
      <p className="workspace-eyebrow">{text.eyebrow}</p>
      <h2>{text.title}</h2>
      <p className="guide-lead">{text.description}</p>

      <div className="manual-card">
        <div className="manual-card-icon" aria-hidden="true"><FileText /></div>
        <div>
          <strong>Structure Editor</strong>
          <p>{text.note}</p>
        </div>
        <input
          ref={fileInputRef}
          type="file"
          accept=".docx,application/vnd.openxmlformats-officedocument.wordprocessingml.document"
          hidden
          onChange={(event) => void handleSelected(event)}
        />
        <button className="panel-primary manual-upload-button" type="button" disabled={uploading} onClick={() => fileInputRef.current?.click()}>
          {uploading ? text.uploading : text.choose}
          <Upload aria-hidden="true" />
        </button>
      </div>
    </section>
  );
}
