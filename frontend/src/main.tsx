import { createRoot } from "react-dom/client";
import App from "./App.tsx";
import "./index.css";

const fontStyle = document.createElement("style");
fontStyle.dataset.slidegenFontFaces = "true";
fontStyle.textContent = `
  @font-face { font-family: "Slidegen Dancing"; font-style: normal; font-weight: 500; font-display: swap; src: url("./fonts/dancing-script-500.ttf") format("truetype"); }
  @font-face { font-family: "Slidegen Dancing"; font-style: normal; font-weight: 600; font-display: swap; src: url("./fonts/dancing-script-600.ttf") format("truetype"); }
  @font-face { font-family: "Slidegen Dancing"; font-style: normal; font-weight: 700; font-display: swap; src: url("./fonts/dancing-script-700.ttf") format("truetype"); }
`;
document.head.appendChild(fontStyle);

createRoot(document.getElementById("root")!).render(<App />);
