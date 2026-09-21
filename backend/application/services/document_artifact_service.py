"""Build canonical Markdown and ordered asset metadata for documents."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from backend.domain.entities.document_artifact import (
    DocumentArtifact,
    DocumentBlock,
)


class DocumentArtifactService:
    """Keep source assets and rendered Markdown in one deterministic step."""

    def build(
        self,
        *,
        title: str,
        markdown: str,
        structure: list[dict[str, Any]],
        assets: list[dict[str, Any]] | None = None,
        markdown_root: str | Path | None = None,
        source_type: str = "unknown",
        metadata: dict[str, Any] | None = None,
    ) -> DocumentArtifact:
        normalized_assets = self._normalize_assets(
            assets or [], markdown_root=markdown_root
        )
        rendered_markdown = self._insert_asset_links(markdown, normalized_assets)
        blocks = self._blocks_from_markdown(rendered_markdown, normalized_assets)
        return DocumentArtifact(
            title=" ".join(str(title or "Document").split()) or "Document",
            plain_text=str(markdown or "").strip(),
            markdown=rendered_markdown,
            structure=structure if isinstance(structure, list) else [],
            blocks=blocks,
            assets=normalized_assets,
            source_type=source_type,
            metadata=dict(metadata or {}),
        )

    @staticmethod
    def _normalize_assets(
        assets: list[dict[str, Any]],
        *,
        markdown_root: str | Path | None,
    ) -> list[dict[str, Any]]:
        root = Path(markdown_root).resolve() if markdown_root else None
        normalized: list[dict[str, Any]] = []
        for item in assets:
            if not isinstance(item, dict):
                continue
            source = str(item.get("source_path") or "").strip()
            if not source:
                continue
            asset = dict(item)
            relative = str(asset.get("relative_path") or "").strip()
            if not relative and root is not None:
                try:
                    relative = Path(source).resolve().relative_to(root).as_posix()
                except ValueError:
                    relative = Path(source).name
            asset["relative_path"] = relative or Path(source).name
            asset["markdown_path"] = f"./{asset['relative_path'].lstrip('./')}"
            asset["alt_text"] = (
                str(
                    asset.get("alt_text")
                    or asset.get("filename")
                    or "Embedded document image"
                ).strip()
               [:500]
            )
            normalized.append(asset)
        return sorted(
            normalized,
            key=lambda item: (
                int(item.get("block_index", item.get("paragraph_index", 0)) or 0),
                int(item.get("ordinal", 0) or 0),
            ),
        )

    @classmethod
    def _insert_asset_links(
        cls,
        markdown: str,
        assets: list[dict[str, Any]],
    ) -> str:
        lines = str(markdown or "").strip().splitlines()
        if not assets:
            return "\n".join(lines).strip()

        insertions: dict[int, list[str]] = {}
        used_targets: dict[str, int] = {}
        for asset in assets:
            if not asset.get("markdown_path"):
                continue
            anchor = " ".join(str(asset.get("anchor_text") or "").split())
            section = " ".join(str(asset.get("section_title") or "").split())
            target = cls._find_target_line(lines, anchor, section, used_targets)
            used_targets[anchor or f"section:{section}"] = target
            rendered = (
                f"![{asset['alt_text']}]({asset['markdown_path']})"
            )
            insertions.setdefault(target, []).append(rendered)

        output: list[str] = []
        for index, line in enumerate(lines):
            output.append(line)
            for image_link in insertions.get(index, []):
                output.extend(("", image_link, ""))
        for image_link in insertions.get(len(lines), []):
            output.extend(("", image_link, ""))
        return "\n".join(output).strip()

    @staticmethod
    def _find_target_line(
        lines: list[str],
        anchor: str,
        section: str,
        used_targets: dict[str, int],
    ) -> int:
        key = anchor or f"section:{section}"
        if key in used_targets:
            return used_targets[key]
        if anchor:
            for index, line in enumerate(lines):
                if anchor.casefold() in line.casefold():
                    return index
        if section:
            for index, line in enumerate(lines):
                clean = re.sub(r"^#+\s*", "", line).strip()
                if section.casefold() == clean.casefold():
                    return index
        return len(lines)

    @staticmethod
    def _blocks_from_markdown(
        markdown: str,
        assets: list[dict[str, Any]],
    ) -> list[DocumentBlock]:
        assets_by_path = {
            str(asset.get("markdown_path")): asset
            for asset in assets
        }
        blocks: list[DocumentBlock] = []
        for index, line in enumerate(str(markdown or "").splitlines()):
            stripped = line.strip()
            if not stripped:
                continue
            image_match = re.match(r"!\[[^]]*\]\(([^)]+)\)", stripped)
            if image_match and image_match.group(1) in assets_by_path:
                asset = assets_by_path[image_match.group(1)]
                blocks.append(
                    DocumentBlock(
                        kind="image",
                        index=index,
                        asset_id=str(asset.get("image_id") or "") or None,
                        metadata=dict(asset),
                    )
                )
            elif stripped.startswith("#"):
                blocks.append(
                    DocumentBlock(
                        kind="heading",
                        index=index,
                        text=re.sub(r"^#+\s*", "", stripped),
                    )
                )
            else:
                blocks.append(DocumentBlock(kind="paragraph", index=index, text=stripped))
        return blocks


document_artifact_service = DocumentArtifactService()
