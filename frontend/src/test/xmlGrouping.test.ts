import { describe, expect, it } from "vitest";
import type { XmlSlideElement } from "@/lib/xmlSlide";
import {
  XML_GROUP_ATTR,
  cloneXmlElements,
  getXmlSelection,
  groupXmlElements,
  moveXmlSelectionLayer,
  ungroupXmlElements,
} from "@/lib/xmlGrouping";

const element = (id: string, x: string): XmlSlideElement => ({
  id,
  tag: "shape",
  attrs: { x, y: "10", width: "100", height: "80" },
  text: "",
  children: [],
});

describe("XML editor grouping", () => {
  it("selects grouped elements together and supports additive selection", () => {
    const grouped = groupXmlElements([element("a", "10"), element("b", "130"), element("c", "250")], ["a", "b"], "g1");
    expect(getXmlSelection(grouped, [], "b")).toEqual(["b", "a"]);
    expect(getXmlSelection(grouped, ["c"], "a", true)).toEqual(["a", "c", "b"]);
    expect(getXmlSelection(grouped, ["c", "a"], "c", false)).toEqual(["c", "a"]);
  });

  it("groups and ungroups without changing geometry", () => {
    const source = [element("a", "10"), element("b", "130")];
    const grouped = groupXmlElements(source, ["a", "b"], "g1");
    expect(grouped.every(item => item.attrs[XML_GROUP_ATTR] === "g1")).toBe(true);
    const ungrouped = ungroupXmlElements(grouped, ["a", "b"]);
    expect(ungrouped.every(item => item.attrs[XML_GROUP_ATTR] === undefined)).toBe(true);
    expect(ungrouped.map(item => item.attrs.x)).toEqual(["10", "130"]);
  });

  it("duplicates grouped elements with a fresh group and offset", () => {
    const grouped = groupXmlElements([element("a", "10"), element("b", "130")], ["a", "b"], "g1");
    const clones = cloneXmlElements(grouped);
    expect(clones.map(item => item.attrs.x)).toEqual(["34", "154"]);
    expect(clones[0].attrs[XML_GROUP_ATTR]).toBe(clones[1].attrs[XML_GROUP_ATTR]);
    expect(clones[0].attrs[XML_GROUP_ATTR]).not.toBe("g1");
  });

  it("moves the selected block through layer order", () => {
    const source = [element("a", "0"), element("b", "0"), element("c", "0")];
    expect(moveXmlSelectionLayer(source, ["a", "b"], "up").map(item => item.id)).toEqual(["c", "a", "b"]);
    expect(moveXmlSelectionLayer(source, ["b", "c"], "down").map(item => item.id)).toEqual(["b", "c", "a"]);
  });
});
