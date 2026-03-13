// SlideEditor Types

export interface SlideElement {
  id: string;
  type: "text" | "image" | "shape" | "icon" | "video";
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
  strokeStyle?: string; // 'none' | 'solid' | 'dashed' | 'dotted'
  borderRadius?: number;
  shadow?: string;
  clipPath?: string;

  // Typography
  fontSize?: number;
  fontFamily?: string;
  fontWeight?: string; // '100'-'900' or 'bold' | 'normal'
  fontStyle?: string; // 'italic' | 'normal'
  textDecoration?: string; // 'underline' | 'none'
  textAlign?: "left" | "center" | "right" | "justify";
  lineHeight?: string;
  letterSpacing?: string;
  color?: string;

  // Filter effects
  blur?: number;
  brightness?: number;
  saturation?: number;

  // Padding
  paddingTop?: number;
  paddingRight?: number;
  paddingBottom?: number;
  paddingLeft?: number;
}

export interface Slide {
  id: string;
  elements: SlideElement[];
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
