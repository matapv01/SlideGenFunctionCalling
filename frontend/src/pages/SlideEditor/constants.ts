import { 
  Type, Square, Circle, Triangle, 
  Image as ImageIcon, Video, FileText, Sigma 
} from "lucide-react";
import type { ElementCategory, Template } from "./types";

// --- Canvas Dimensions ---
export const CANVAS_WIDTH = 1920;
export const CANVAS_HEIGHT = 1080;

// --- Templates ---
export const TEMPLATES: Template[] = [
  { id: "title", name: "Title Slide", layout: "title" },
  { id: "content", name: "Title & Content", layout: "content" },
  { id: "two-col", name: "Two Columns", layout: "two-col" },
  { id: "blank", name: "Blank", layout: "blank" },
];

// --- Element Categories ---
export const ELEMENTS_CATEGORIES: ElementCategory[] = [
  {
    name: "Basic Shapes",
    items: [
      { id: "rect", icon: Square, label: "Rectangle", type: "shape", subType: "rectangle" },
      { id: "circle", icon: Circle, label: "Circle", type: "shape", subType: "circle" },
      { id: "triangle", icon: Triangle, label: "Triangle", type: "shape", subType: "triangle" },
    ]
  },
  {
    name: "Media",
    items: [
      { id: "image", icon: ImageIcon, label: "Image", type: "image", subType: "" },
      { id: "video", icon: Video, label: "Video", type: "video", subType: "" },
    ]
  },
  {
    name: "Text",
    items: [
      { id: "heading", icon: Type, label: "Heading", type: "text", subType: "heading" },
      { id: "paragraph", icon: Type, label: "Paragraph", type: "text", subType: "paragraph" },
    ]
  },
  {
    name: "Equations",
    items: [
      { id: "math", icon: Sigma, label: "Equation", type: "math", subType: "equation" },
    ]
  }
];
