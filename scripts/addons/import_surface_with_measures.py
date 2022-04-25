import bpy
import typing

from bpy.props import (
    StringProperty,
    CollectionProperty,
)
from bpy_extras.io_utils import (
    ImportHelper,
)
from bpy.types import (
    Operator,
    OperatorFileListElement,
)

bl_info = {
    "name": "Import Surface and Measures",
    "author": "Patrick Scheibe",
    "version": (0, 0, 1),
    "blender": (3, 1, 2),
    "location": "File > Import-Export",
    "description": "Import asc surface and measure files",
    "category": "Import-Export",
}


class ImportBrain(Operator, ImportHelper):
    """Loads a surface together with measurements on each vertex"""
    bl_idname = "import_surface_and_measures.asc"
    bl_label = "Import Surface and Measures"
    filename_ext = ".asc"

    filter_glob: StringProperty(
        default="*.asc",
        options={'HIDDEN'},
    )
    files: CollectionProperty(
        name="File Path",
        type=OperatorFileListElement,
    )
    directory: StringProperty(
        subtype='DIR_PATH',
    )

    def execute(self, context) -> typing.Union[typing.Set[str], typing.Set[int]]:
        import os

        paths = [os.path.join(self.directory, name.name) for name in self.files]
        scene = context.scene

        if len(paths) != 2:
            return {"CANCELLED"}

        pts_file = [s for s in paths if s.endswith("surf.asc")]
        assert len(pts_file) == 1
        pts_file = pts_file[0]

        tri_file = [s for s in paths if s.endswith("tri.asc")]
        assert len(tri_file) == 1
        tri_file = tri_file[0]

        pts, measurements = read_vertices_and_measurements(pts_file)
        tris = read_triangle_indices(tri_file)

        create_and_link_mesh("brain", tris, pts, measurements)

        return {'FINISHED'}


def menu_import(self, context):
    self.layout.operator(ImportBrain.bl_idname, text="Surface and Measures (.asc)")


def read_vertices_and_measurements(file: str) -> tuple:
    """
    Reads in a file where each line consists of id, x, y, z, m1, m2, ... and where the m are
    measurement values that we'd like to attach to vertices in Blender.
    Later, their values can be used for visualizing scientific results.
    """
    pts = []
    meas = []
    with open(file, "r") as f:
        for line in f.readlines():
            parts = line.split()
            id = int(float(parts[0]))
            x = float(parts[1])
            y = float(parts[2])
            z = float(parts[3])
            measures = []
            for i in range(4, len(parts)):
                measures.append(float(parts[i]))
            pts.append((x,y,z))
            meas.append(measures)
    return pts, meas


def read_triangle_indices(file: str) -> typing.List:
    """
    Reads in a file where each line is a triple of indices pointing to the list of vertices
    read in before. The final surface is then created from the returned set of triangles.
    """
    result = []
    with open(file, "r") as f:
        for line in f.readlines():
            parts = line.split()
            poly = []
            for i in range(len(parts)):
                poly.append(int(float(parts[i])) - 1)
            result.append(poly)
    return result


def create_and_link_mesh(name: str, faces: typing.List[tuple], points: typing.List[tuple], measures: typing.List):
    """
    Create a blender mesh and object called name from a list of
    *points* and *faces* and link it in the current scene.
    """
    import bpy

    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(points, [], faces)

    if len(measures) == len(points):
        dim = len(measures[0])
        for i in range(dim):
            measure_name = f"Measure{i+1}"
            # Create custom attribute storing one FLOAT for every POINT (vertex)
            attr = mesh.attributes.new(measure_name, 'FLOAT', 'POINT')
            # Set value at each vertex
            attr.data.foreach_set("value", [m[i] for m in measures])

    mesh.validate(clean_customdata=False, verbose=True)
    mesh.calc_normals()
    mesh.use_auto_smooth = True
    mesh.update()

    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)


def register():
    bpy.utils.register_class(ImportBrain)
    bpy.types.TOPBAR_MT_file_import.append(menu_import)


def unregister():
    bpy.utils.unregister_class(ImportBrain)
    bpy.types.TOPBAR_MT_file_import.remove(menu_import)


if __name__ == "__main__":
    register()
