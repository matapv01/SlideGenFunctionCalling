import { Globe, Check } from "lucide-react";
import { useLanguage } from "@/contexts/LanguageContext";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Button } from "@/components/ui/button";

export const LanguageToggle = () => {
  const { language, setLanguage } = useLanguage();

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="ghost" size="icon" className="rounded-full">
          <Globe className="h-4 w-4" />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end">
        <DropdownMenuItem onClick={() => setLanguage("en")} className="gap-2">
          <Check className={`h-4 w-4 ${language === "en" ? "opacity-100" : "opacity-0"}`} />
          English
        </DropdownMenuItem>
        <DropdownMenuItem onClick={() => setLanguage("vi")} className="gap-2">
          <Check className={`h-4 w-4 ${language === "vi" ? "opacity-100" : "opacity-0"}`} />
          Tiếng Việt
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
};
