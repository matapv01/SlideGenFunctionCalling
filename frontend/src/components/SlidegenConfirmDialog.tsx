import { AlertTriangle, HelpCircle } from "lucide-react";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog";
import { cn } from "@/lib/utils";

interface SlidegenConfirmDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  title: string;
  description: string;
  confirmLabel: string;
  cancelLabel: string;
  onConfirm: () => void;
  destructive?: boolean;
  busy?: boolean;
}

/** A compact confirmation surface shared by the migrated Slidegen workspace. */
export default function SlidegenConfirmDialog({
  open,
  onOpenChange,
  title,
  description,
  confirmLabel,
  cancelLabel,
  onConfirm,
  destructive = false,
  busy = false,
}: SlidegenConfirmDialogProps) {
  return (
    <AlertDialog open={open} onOpenChange={onOpenChange}>
      <AlertDialogContent className="sg-confirm-dialog">
        <AlertDialogHeader className="sg-confirm-dialog-header">
          <span className={cn("sg-confirm-dialog-icon", destructive && "is-destructive")} aria-hidden="true">
            {destructive ? <AlertTriangle /> : <HelpCircle />}
          </span>
          <div>
            <AlertDialogTitle className="sg-confirm-dialog-title">{title}</AlertDialogTitle>
            <AlertDialogDescription className="sg-confirm-dialog-description">
              {description}
            </AlertDialogDescription>
          </div>
        </AlertDialogHeader>
        <AlertDialogFooter className="sg-confirm-dialog-footer">
          <AlertDialogCancel className="sg-confirm-dialog-cancel" disabled={busy}>
            {cancelLabel}
          </AlertDialogCancel>
          <AlertDialogAction
            className={cn("sg-confirm-dialog-confirm", destructive && "is-destructive")}
            onClick={onConfirm}
            disabled={busy}
          >
            {busy ? "…" : confirmLabel}
          </AlertDialogAction>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  );
}
