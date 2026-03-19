import { 
  Type, Square, Circle, Triangle, Star, Minus, Diamond, Sigma,
  Image as ImageIcon, Video,
  Heading1, Heading2, AlignLeft, Tag,
} from "lucide-react";
import type { ElementCategory, Template } from "./types";

// --- Canvas Dimensions ---
export const CANVAS_WIDTH = 1920;
export const CANVAS_HEIGHT = 1080;

// --- Templates ---
export const TEMPLATES: Template[] = [
  { id: "blank",    name: "Blank",           layout: "blank" },
  { id: "title",    name: "Title Slide",     layout: "title" },
  { id: "content",  name: "Title & Content", layout: "content" },
  { id: "two-col",  name: "Two Columns",     layout: "two-col" },
  { id: "img-left", name: "Image + Text",    layout: "image-left" },
  { id: "bullets",  name: "Title & Bullets", layout: "bullets" },
];

// --- Element Categories ---
export const ELEMENTS_CATEGORIES: ElementCategory[] = [
  {
    name: "Text",
    items: [
      { id: "heading",    icon: Heading1,  label: "Title",    type: "text", subType: "heading" },
      { id: "subheading", icon: Heading2,  label: "Subtitle", type: "text", subType: "subheading" },
      { id: "paragraph",  icon: AlignLeft, label: "Body",     type: "text", subType: "paragraph" },
      { id: "label",      icon: Tag,       label: "Label",    type: "text", subType: "label" },
    ]
  },
  {
    name: "Shapes",
    items: [
      { id: "rect",     icon: Square,   label: "Rectangle", type: "shape", subType: "rectangle" },
      { id: "circle",   icon: Circle,   label: "Circle",    type: "shape", subType: "circle" },
      { id: "triangle", icon: Triangle, label: "Triangle",  type: "shape", subType: "triangle" },
      { id: "star",     icon: Star,     label: "Star",      type: "shape", subType: "star" },
      { id: "diamond",  icon: Diamond,  label: "Diamond",   type: "shape", subType: "diamond" },
      { id: "line",     icon: Minus,    label: "Line",      type: "shape", subType: "line" },
      { id: "equation", icon: Sigma,    label: "Equation",  type: "equation", subType: "equation" },
    ]
  },
  {
    name: "Media",
    items: [
      { id: "image", icon: ImageIcon, label: "Image", type: "image", subType: "" },
      { id: "video", icon: Video,     label: "Video", type: "video", subType: "" },
    ]
  },
];
