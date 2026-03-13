import { Button } from "@/components/ui/button";
import { useLanguage } from "@/contexts/LanguageContext";

export const LanguageToggle = () => {
  const { language, setLanguage } = useLanguage();
  
  const toggleLanguage = () => {
    setLanguage(language === "vi" ? "en" : "vi");
  };

  return (
    <Button variant="ghost" size="icon" onClick={toggleLanguage} className="rounded-full font-bold text-sm">
      {language === "vi" ? "E" : "V"}
    </Button>
  );
};
