import type { XmlSlideElement } from "./xmlSlide";

export const XML_GROUP_ATTR = "editor_group";

const makeGroupId = () => `xml-group-${Date.now()}-${Math.random().toString(36).slice(2, 7)}`;
const makeElementId = (index: number) => `xml-element-${Date.now()}-${index}-${Math.random().toString(36).slice(2, 7)}`;

export const getXmlSelection = (
  elements: XmlSlideElement[],
  currentIds: string[],
  targetId: string | null,
  additive = false,
) => {
  if (!targetId) return [];
  const target = elements.find(element => element.id === targetId);
  if (!target) return [];

  const groupId = target.attrs[XML_GROUP_ATTR];
  const candidates = groupId
    ? elements.filter(element => element.attrs[XML_GROUP_ATTR] === groupId).map(element => element.id)
    : [targetId];

  if (!additive) {
    if (currentIds.length > 1 && currentIds.includes(targetId)) {
      return [targetId, ...currentIds.filter(id => id !== targetId)];
    }
    return [targetId, ...candidates.filter(id => id !== targetId)];
  }

  const current = new Set(currentIds);
  const allSelected = candidates.every(id => current.has(id));
  candidates.forEach(id => allSelected ? current.delete(id) : current.add(id));
  if (current.size === 0) return [];
  if (!allSelected && current.has(targetId)) {
    return [targetId, ...Array.from(current).filter(id => id !== targetId)];
  }
  return Array.from(current);
};

export const groupXmlElements = (
  elements: XmlSlideElement[],
  selectedIds: string[],
  groupId = makeGroupId(),
) => {
  if (selectedIds.length < 2) return elements;
  const selected = new Set(selectedIds);
  return elements.map(element => selected.has(element.id)
    ? { ...element, attrs: { ...element.attrs, [XML_GROUP_ATTR]: groupId } }
    : element);
};

export const ungroupXmlElements = (elements: XmlSlideElement[], selectedIds: string[]) => {
  const selected = new Set(selectedIds);
  const groupIds = new Set(
    elements
      .filter(element => selected.has(element.id))
      .map(element => element.attrs[XML_GROUP_ATTR])
      .filter(Boolean),
  );
  if (groupIds.size === 0) return elements;

  return elements.map(element => {
    if (!groupIds.has(element.attrs[XML_GROUP_ATTR])) return element;
    const attrs = { ...element.attrs };
    delete attrs[XML_GROUP_ATTR];
    return { ...element, attrs };
  });
};

const offsetPoints = (points: string, offset: number) => points.replace(
  /(-?\d+(?:\.\d+)?)\s*,\s*(-?\d+(?:\.\d+)?)/g,
  (_, x, y) => `${Number(x) + offset},${Number(y) + offset}`,
);

const offsetElement = (element: XmlSlideElement, offset: number) => {
  const attrs = { ...element.attrs };
  ["x", "y", "x1", "y1", "x2", "y2"].forEach(name => {
    if (attrs[name] === undefined) return;
    const value = Number(attrs[name]);
    if (Number.isFinite(value)) attrs[name] = String(value + offset);
  });
  if (attrs.points) attrs.points = offsetPoints(attrs.points, offset);
  return attrs;
};

export const cloneXmlElements = (elements: XmlSlideElement[], offset = 24) => {
  const groupIds = new Map<string, string>();
  return elements.map((source, index) => {
    const clone = JSON.parse(JSON.stringify(source)) as XmlSlideElement;
    clone.id = makeElementId(index);
    clone.attrs = offsetElement(clone, offset);
    const sourceGroupId = source.attrs[XML_GROUP_ATTR];
    if (sourceGroupId) {
      if (!groupIds.has(sourceGroupId)) groupIds.set(sourceGroupId, makeGroupId());
      clone.attrs[XML_GROUP_ATTR] = groupIds.get(sourceGroupId)!;
    }
    return clone;
  });
};

export const moveXmlSelectionLayer = (
  elements: XmlSlideElement[],
  selectedIds: string[],
  direction: "up" | "down",
) => {
  const next = [...elements];
  const selected = new Set(selectedIds);
  if (direction === "up") {
    for (let index = next.length - 2; index >= 0; index -= 1) {
      if (selected.has(next[index].id) && !selected.has(next[index + 1].id)) {
        [next[index], next[index + 1]] = [next[index + 1], next[index]];
      }
    }
  } else {
    for (let index = 1; index < next.length; index += 1) {
      if (selected.has(next[index].id) && !selected.has(next[index - 1].id)) {
        [next[index], next[index - 1]] = [next[index - 1], next[index]];
      }
    }
  }
  return next;
};
