bl_info = {
    "name": "Frame Hierarchy",
    "author": "ChatGPT, deepseek, duhazzz",
    "version": (1, 8),
    "blender": (2, 93, 0),
    "location": "Node Editor > Sidebar > Frame Hierarchy",
    "description": "Displays frame hierarchy with popup and focus functionality",
    "category": "Node",
}

import bpy
from bpy.types import Panel, Operator, Menu
from bpy.props import StringProperty, BoolProperty


class NODE_OT_toggle_frame_collapse(Operator):
    bl_idname = "node.toggle_frame_collapse"
    bl_label = "Toggle Frame Collapse"
    bl_options = {'INTERNAL'}

    frame_name: StringProperty()
    use_focus: BoolProperty(default=False)

    def execute(self, context):
        # Toggle collapsed state
        if not self.use_focus:
            if not hasattr(context.scene, "collapsed_frames"):
                context.scene.collapsed_frames = {}
            current_state = context.scene.collapsed_frames.get(self.frame_name, True)
            context.scene.collapsed_frames[self.frame_name] = not current_state

        # Focus on frame node if requested
        if self.use_focus:
            space = context.space_data
            if hasattr(space, "edit_tree") and space.edit_tree:
                tree = space.edit_tree
                frame = tree.nodes.get(self.frame_name)
                if frame and frame.type == 'FRAME':
                    # Deselect all, select this frame
                    for node in tree.nodes:
                        node.select = False
                    frame.select = True
                    tree.nodes.active = frame

                    # Focus view on selected node
                    bpy.ops.node.view_selected()

        return {'FINISHED'}

    def invoke(self, context, event):
        self.use_focus = event.ctrl
        return self.execute(context)


class NODE_OT_show_frame_hierarchy_popup(Operator):
    bl_idname = "node.show_frame_hierarchy_popup"
    bl_label = "Frame Hierarchy"  # This will be the popup title
    bl_description = "Show frame hierarchy in popup window"

    def execute(self, context):
        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_popup(self, width=300)

    def draw(self, context):
        layout = self.layout
        space = context.space_data

        # Add title label (matches the panel header)
        layout.label(text="Frame Hierarchy", icon='FILE_VOLUME')

        if not hasattr(space, "edit_tree") or space.edit_tree is None:
            layout.label(text="No active node tree")
            return

        tree = space.edit_tree
        frames = [node for node in tree.nodes if node.type == 'FRAME']

        if not hasattr(context.scene, "collapsed_frames"):
            context.scene.collapsed_frames = {}

        root_frames = [f for f in frames if f.parent is None or f.parent.type != 'FRAME']

        def draw_frame(frame, level=0):
            display_name = frame.label if frame.label else frame.name
            frame_id = frame.name

            is_collapsed = context.scene.collapsed_frames.get(frame_id, True)
            children = [f for f in frames if f.parent == frame]
            has_children = bool(children)

            row = layout.row(align=True)
            row.alignment = 'LEFT'

            # Indentation
            for _ in range(level):
                row.label(text="", icon='BLANK1')

            icon = 'TRIA_RIGHT' if is_collapsed and has_children else 'TRIA_DOWN' if has_children else 'DOT'

            op_icon = row.operator(
                "node.toggle_frame_collapse",
                text="",
                icon=icon,
                emboss=True
            )
            op_icon.frame_name = frame_id

            op_label = row.operator(
                "node.toggle_frame_collapse",
                text=display_name,
                icon='NONE',
                emboss=True
            )
            op_label.frame_name = frame_id

            if has_children and not is_collapsed:
                for child in children:
                    draw_frame(child, level + 1)

        # Add scrollable region
        scroll = layout.box()
        col = scroll.column()
        
        for frame in root_frames:
            draw_frame(frame)


class NODE_PT_frame_hierarchy(Panel):
    bl_label = "Frame Hierarchy"
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_category = "Frame Hierarchy"

    def draw(self, context):
        layout = self.layout
        space = context.space_data

        # Add button to open popup
        row = layout.row()
        row.operator("node.show_frame_hierarchy_popup", 
                    text="Open Hierarchy Popup",
                    icon='WINDOW')

        if not hasattr(space, "edit_tree") or space.edit_tree is None:
            layout.label(text="No active node tree")
            return

        tree = space.edit_tree
        frames = [node for node in tree.nodes if node.type == 'FRAME']

        if not hasattr(context.scene, "collapsed_frames"):
            context.scene.collapsed_frames = {}

        root_frames = [f for f in frames if f.parent is None or f.parent.type != 'FRAME']

        def draw_frame(frame, level=0):
            display_name = frame.label if frame.label else frame.name
            frame_id = frame.name

            is_collapsed = context.scene.collapsed_frames.get(frame_id, True)
            children = [f for f in frames if f.parent == frame]
            has_children = bool(children)

            row = layout.row(align=True)
            row.alignment = 'LEFT'

            # Indentation
            for _ in range(level):
                row.label(text="", icon='BLANK1')

            icon = 'TRIA_RIGHT' if is_collapsed and has_children else 'TRIA_DOWN' if has_children else 'DOT'

            op_icon = row.operator(
                "node.toggle_frame_collapse",
                text="",
                icon=icon,
                emboss=True
            )
            op_icon.frame_name = frame_id

            op_label = row.operator(
                "node.toggle_frame_collapse",
                text=display_name,
                icon='NONE',
                emboss=True
            )
            op_label.frame_name = frame_id

            if has_children and not is_collapsed:
                for child in children:
                    draw_frame(child, level + 1)

        for frame in root_frames:
            draw_frame(frame)


def register():
    bpy.utils.register_class(NODE_OT_toggle_frame_collapse)
    bpy.utils.register_class(NODE_OT_show_frame_hierarchy_popup)
    bpy.utils.register_class(NODE_PT_frame_hierarchy)
    bpy.types.Scene.collapsed_frames = {}


def unregister():
    bpy.utils.unregister_class(NODE_PT_frame_hierarchy)
    bpy.utils.unregister_class(NODE_OT_show_frame_hierarchy_popup)
    bpy.utils.unregister_class(NODE_OT_toggle_frame_collapse)
    del bpy.types.Scene.collapsed_frames


if __name__ == "__main__":
    register()