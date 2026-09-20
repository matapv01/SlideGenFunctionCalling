import "./slidegen-logo.css";

interface SlidegenLogoProps {
  className?: string;
}

export default function SlidegenLogo({ className = "" }: SlidegenLogoProps) {
  return (
    <span className={`slidegen-logo ${className}`.trim()}>
      <span className="slidegen-logo-wordmark">
        <span className="slidegen-logo-initial">S</span>
        <span className="slidegen-logo-rest">lide</span>
        <b>Gen</b>
      </span>
    </span>
  );
}
