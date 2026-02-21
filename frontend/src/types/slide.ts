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
  borderRadius?: number;
  shadow?: string;
  clipPath?: string;

  // Typography
  fontSize?: number;
  fontFamily?: string;
  fontWeight?: string;
  fontStyle?: string;
  textDecoration?: string;
  textAlign?: "left" | "center" | "right";
  lineHeight?: string;
  letterSpacing?: string;
  color?: string;
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
  content?: string;
}