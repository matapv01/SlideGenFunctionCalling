// SlideEditor Types

export interface SlideElement {
  id: string;
  type: "text" | "image" | "shape" | "icon" | "video" | "math" | "connector";
  subType?: string;
  content?: string;
  src?: string;
  x: number;
  y: number;
  width: number;
  height: number;
  rotation: number;
  zIndex: number;
  opacity: number;
  
  // Appearance
  fillColor?: string;
  strokeColor?: string;
  strokeWidth?: number;
  borderRadius?: number;
  shadow?: string;
  clipPath?: string;

  // Typography
  fontSize?: number;
  fontFamily?: string;
  fontWeight?: string; // 'bold' | 'normal'
  fontStyle?: string; // 'italic' | 'normal'
  textDecoration?: string; // 'underline' | 'none'
  textAlign?: "left" | "center" | "right";
  lineHeight?: string;
  letterSpacing?: string;
  color?: string;
}

export interface Slide {
  id: string;
  elements: SlideElement[];  // Interactive elements on top
  htmlBackground?: string;   // Raw HTML from backend - rendered as read-only background
  backgroundColor?: string;
  backgroundImage?: string;
  notes?: string;
  defs?: string;
}

export interface DragItem {
  type: string;
  subType?: string;
  content?: string; // Default content or SRC
}

export interface ElementCategory {
  name: string;
  items: {
    id: string;
    icon: React.ComponentType<{ className?: string }>;
    label: string;
    type: string;
    subType: string;
  }[];
}

export interface Template {
  id: string;
  name: string;
  layout: string;
}
