import React, { useRef, useEffect } from 'react';
import 'mathlive';
import { useEditorStore } from '../store/useEditorStore';
import type { SlideElement } from '../types';

declare global {
  namespace JSX {
    interface IntrinsicElements {
      'math-field': React.DetailedHTMLProps<React.HTMLAttributes<HTMLElement> & {
         onInput?: (e: Event) => void;
      }, HTMLElement>;
    }
  }
}

interface MathLiveElementProps {
  element: SlideElement;
}

export const MathLiveElement = ({ element }: MathLiveElementProps) => {
  const mfRef = useRef<HTMLElement>(null);
  const { updateElement, currentSlideId } = useEditorStore();

  useEffect(() => {
    const mf = mfRef.current as any;
    if (mf && element.content !== mf.value) {
      mf.value = element.content || '';
    }
  }, [element.content]);

  useEffect(() => {
    const mf = mfRef.current as any;
    if (!mf) return;

    const handleInput = (e: Event) => {
      const newValue = (e.target as any).value;
      if (currentSlideId) {
        updateElement(currentSlideId, element.id, { content: newValue });
      }
    };

    mf.addEventListener('input', handleInput);
    return () => mf.removeEventListener('input', handleInput);
  }, [currentSlideId, element.id, updateElement]);

  return (
      <math-field
        ref={mfRef}
        style={{
          width: '100%',
          height: '100%',
          fontSize: 'inherit',
          color: 'inherit',
          backgroundColor: 'transparent',
          border: 'none',
          outline: 'none',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          pointerEvents: 'auto', // Ensure it receives pointer events
        }}
        onFocus={(e) => {
            e.stopPropagation(); // Stop propagation to not immediately deselect
        }}
        onClick={(e) => {
             e.stopPropagation(); // Avoid triggering deselect on the canvas
             (mfRef.current as any)?.focus();
        }}
      >
        {element.content}
      </math-field>
  );
};
