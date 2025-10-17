from __future__ import annotations

from base import BaseModel
from base import BaseService

from graph.shared.agent import SlidegenState
from graph.shared.settings import OrganizeChunkSettings

class OrganizeChunkService(BaseService):
    
    organize_chunk_settings: OrganizeChunkSettings
    
    def process(self, inputs: SlidegenState) -> dict:
        
        renumbered_structure = self._add_numbering_recursively(inputs.get('document_structure', []))
        
        final_slides_content, final_slides_positions, final_slides_context_maps = [], [], []

        final_slides_content, final_slides_positions, final_slides_context_maps = self._traverse_dfs(
            nodes=renumbered_structure,
            final_slides_content=final_slides_content,
            final_slides_positions=final_slides_positions,
            final_slides_context_maps=final_slides_context_maps,
            renumbered_structure=renumbered_structure
        )
        
        def _get_version_key(pos_str):
            try: 
                return tuple(map(int, pos_str.split('.')))
            except ValueError: 
                return

        combined = list(zip(final_slides_content, final_slides_positions, final_slides_context_maps))
        def sort_key(slide_data):
            return _get_version_key(slide_data[1][0]) if slide_data[1] else ()

        sorted_combined = sorted(combined, key=sort_key)
        
        if sorted_combined:
            sorted_chunks, sorted_positions, sorted_maps = zip(*sorted_combined)
        else:
            sorted_chunks, sorted_positions, sorted_maps = [], [], []
            
        return {
            'document_outline': renumbered_structure,
            'slide_chunks': list(sorted_chunks),
            'slide_positions': list(sorted_positions),
            'slide_context_maps': list(sorted_maps),
        }
        
            
    def _traverse_dfs(self, nodes, final_slides_content, final_slides_positions, final_slides_context_maps, renumbered_structure):
        for node in nodes:
            if node.get("content"):
                pos = [node.get('index', '')]
                final_slides_content.append(self._render_slide_content("", [node]))
                final_slides_positions.append(pos)
                final_slides_context_maps.append(self._create_context_map(renumbered_structure, pos))
            leaves = [child for child in node.get("children", []) if not child.get("children")]
            if leaves:
                
                self._create_slides_from_leaves(
                    parent=node, 
                    leaves=leaves, 
                    final_slides_content=final_slides_content, 
                    final_slides_positions=final_slides_positions, 
                    final_slides_context_maps=final_slides_context_maps, 
                    renumbered_structure=renumbered_structure
                )
                
            sub_trees = [child for child in node.get("children", []) if child.get("children")]
            if sub_trees:
                
                self._traverse_dfs(
                    sub_trees, 
                    final_slides_content, 
                    final_slides_positions, 
                    final_slides_context_maps, 
                    renumbered_structure
                )
                
        return final_slides_content, final_slides_positions, final_slides_context_maps

    def _create_slides_from_leaves(self, parent, leaves, final_slides_content, final_slides_positions, final_slides_context_maps, renumbered_structure):
        
        if not leaves: 
            return
        buffer = []
        header = parent.get('numbered_title', '')
        for item in leaves:
            tentative_buffer = buffer + [item]
            if len(self._render_slide_content(header, tentative_buffer)) > self.organize_chunk_settings.THRESHOLD_CHAR_LIMIT and buffer:
                content = self._render_slide_content(header, buffer)
                pos = [i.get('index', '') for i in buffer]
                final_slides_content.append(content)
                final_slides_positions.append(pos)
                final_slides_context_maps.append(self._create_context_map(renumbered_structure, pos))
                buffer = [item]
            else:
                buffer.append(item)
        if buffer:
            content = self._render_slide_content(header, buffer)
            pos = [i.get('index', '') for i in buffer]
            final_slides_content.append(content)
            final_slides_positions.append(pos)
            final_slides_context_maps.append(self._create_context_map(renumbered_structure, pos))
            
    def _render_slide_content(self, group_header, items):
        parts = [group_header] if group_header else []
        if len(items) > 1:
            for item in items:
                parts.append(f"\n\t- {item.get('title', '')}")
                if item.get('content'):
                    indented = "\n\t  ".join(item['content'].splitlines())
                    parts.append(f"\t  {indented}")
        else:
            item = items[0]
            parts.append(f"\n{item.get('numbered_title', item.get('title', ''))}")
            if item.get('content'): 
                parts.append(f"{item['content']}")
        return "\n".join(parts)
    
    def _add_numbering_recursively(self, nodes, counters=None, parent_level=0):
        counters = [0] * 6 if counters is None else counters
        for node in nodes:
            counters[parent_level] += 1
            for i in range(parent_level + 1, len(counters)): 
                counters[i] = 0
                
            index = ".".join(map(str, counters[:parent_level + 1]))
            node['index'] = index
            node['numbered_title'] = f"{index}. {node['title']}"
            node['level'] = parent_level + 1
            if node.get('children'):
                self._add_numbering_recursively(nodes=node['children'], counters=list(counters), parent_level=parent_level+1)
                
        return nodes
    
    
    def _create_context_map(self, outline_nodes, active_indices):
        map_lines = []
        map_lines = self._generate(map_lines=map_lines, nodes=outline_nodes, active_indices=active_indices, indent=0)
        return "\n".join(map_lines)
    
    def _generate(self, map_lines, nodes, active_indices, indent):
        for node in nodes:
            marker = " <--- YOU ARE HERE" if node.get("index") in active_indices else ""
            map_lines.append(f'{"  " * indent}{node.get("index", "")}. {node.get("title", "")}{marker}')
            if node.get("children"): 
                self._generate(map_lines=map_lines, nodes=node["children"], active_indices=active_indices, indent=indent+1)
                
        return map_lines
