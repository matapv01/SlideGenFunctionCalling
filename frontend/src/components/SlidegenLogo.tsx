import { publicAssetUrl } from "@/lib/publicAssetUrl";
import "./slidegen-logo.css";

interface SlidegenLogoProps {
  className?: string;
}

export default function SlidegenLogo({ className = "" }: SlidegenLogoProps) {
  return (
    <span className={`slidegen-logo ${className}`.trim()}>
      <img className="slidegen-logo-image" src={publicAssetUrl("slidegen-logo.png")} alt="SlideGen" />
      <img className="slidegen-logo-mark-image" src={publicAssetUrl("slidegen-logo-mark.png")} alt="" aria-hidden="true" />
    </span>
  );
}
