import { describe, expect, it, vi } from "vitest";
import { ElementAPIMixin } from "@/lib/mixins/ElementAPIMixin.js";
import { SelectionMixin } from "@/lib/mixins/SelectionMixin.js";

const makeElement = (id: string, left: number) => {
  const element = document.createElement("div");
  element.id = id;
  element.className = "element";
  element.dataset.selectable = "true";
  element.style.cssText = `position:absolute;left:${left}px;top:20px;width:100px;height:80px;z-index:1;`;
  return element;
};

const createLogic = () => {
  const root = document.createElement("div");
  const canvas = document.createElement("div");
  root.appendChild(canvas);

  const first = makeElement("first", 10);
  const second = makeElement("second", 140);
  canvas.append(first, second);

  const logic = Object.assign({
    root,
    canvas,
    selectedElements: [first, second],
    selectedElementId: first.id,
    isEditingText: false,
    isDragging: false,
    isResizing: false,
    onElementSelect: vi.fn(),
    saveHistory: vi.fn(),
  }, SelectionMixin, ElementAPIMixin);

  return { logic, canvas, first, second };
};

describe("slide element grouping", () => {
  it("groups a multi-selection and selects the whole group on click", () => {
    const { logic, first, second } = createLogic();

    expect(logic.groupSelectedElements()).toBe(true);
    expect(first.dataset.editorGroup).toBeTruthy();
    expect(second.dataset.editorGroup).toBe(first.dataset.editorGroup);

    logic.selectedElements = [];
    logic.selectElement(second);
    expect(logic.getSelectionInfo()).toMatchObject({ count: 2, isGroup: true });
  });

  it("ungroups without changing element positions", () => {
    const { logic, first, second } = createLogic();
    const firstLeft = first.style.left;
    const secondLeft = second.style.left;

    logic.groupSelectedElements();
    expect(logic.ungroupSelectedElements()).toBe(true);

    expect(first.dataset.editorGroup).toBeUndefined();
    expect(second.dataset.editorGroup).toBeUndefined();
    expect(first.style.left).toBe(firstLeft);
    expect(second.style.left).toBe(secondLeft);
  });

  it("duplicates and deletes a group as one operation", () => {
    const { logic, canvas } = createLogic();
    logic.groupSelectedElements();

    const duplicatedIds = logic.duplicateElement();
    expect(duplicatedIds).toHaveLength(2);
    const duplicated = duplicatedIds.map(id => canvas.querySelector<HTMLElement>(`#${id}`));
    expect(duplicated.every(Boolean)).toBe(true);
    expect(duplicated[0]?.dataset.editorGroup).toBe(duplicated[1]?.dataset.editorGroup);

    const deletedIds = logic.deleteElement(duplicatedIds[0]);
    expect(deletedIds).toHaveLength(2);
    expect(canvas.children).toHaveLength(2);
  });
});
