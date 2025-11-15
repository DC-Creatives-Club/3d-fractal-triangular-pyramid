import bpy
import bmesh
import math
from mathutils import Vector, Matrix, Euler

# Parameters
size = 30
nozzle_width = 0.4
scale_factor = 0.5
recursion_depth = 4

def create_tetra(s):
    """Create a tetrahedron mesh with given size"""
    points = [
        Vector([0, 0, 0]),
        Vector([s, 0, 0]),
        Vector([s/2, (math.sqrt(3)/2)*s, 0]),
        Vector([s/2, (math.sqrt(3)/6)*s, math.sqrt(6)/3 * s])
    ]
    
    faces = [
        [0, 1, 2],  # base
        [0, 1, 3],  # side 1
        [1, 2, 3],  # side 2
        [2, 0, 3]   # side 3
    ]
    
    # Create mesh
    mesh = bpy.data.meshes.new("Tetrahedron")
    bm = bmesh.new()
    
    # Add vertices
    verts = [bm.verts.new(p) for p in points]
    
    # Add faces
    for face in faces:
        bm.faces.new([verts[i] for i in face])
    
    bm.to_mesh(mesh)
    bm.free()
    
    return mesh

def get_rotation_matrix_to_align(from_vec, to_vec):
    """Get rotation matrix to align from_vec to to_vec"""
    from_vec = from_vec.normalized()
    to_vec = to_vec.normalized()
    
    # Cross product gives rotation axis
    axis = from_vec.cross(to_vec)
    
    # If vectors are parallel or anti-parallel
    if axis.length < 0.0001:
        if from_vec.dot(to_vec) > 0:
            return Matrix.Identity(4)
        else:
            # 180 degree rotation around any perpendicular axis
            perp = Vector([1, 0, 0]) if abs(from_vec.x) < 0.9 else Vector([0, 1, 0])
            axis = from_vec.cross(perp).normalized()
            return Matrix.Rotation(math.pi, 4, axis)
    
    axis.normalize()
    angle = math.acos(max(-1, min(1, from_vec.dot(to_vec))))
    return Matrix.Rotation(angle, 4, axis)

def fractal_tetra_simple(s, depth, parent_matrix=Matrix.Identity(4), all_meshes=None, skip_base=False):
    """Recursively create fractal tetrahedron"""
    if all_meshes is None:
        all_meshes = []
    
    if s >= nozzle_width and depth > 0:
        print(f"depth: {depth}, size: {s}")
        
        # Create tetrahedron at this level
        mesh = create_tetra(s)
        all_meshes.append((mesh, parent_matrix.copy(), depth))
        
        next_size = s * scale_factor
        
        # Define vertices for this tetrahedron
        v0 = Vector([0, 0, 0])
        v1 = Vector([s, 0, 0])
        v2 = Vector([s/2, (math.sqrt(3)/2)*s, 0])
        v3 = Vector([s/2, (math.sqrt(3)/6)*s, math.sqrt(6)/3 * s])
        
        # Define the 4 faces with their vertices and normals
        faces = [
            ([v0, v1, v2], Vector([0, 0, 1]), "base"),     # base (pointing up/out)
            ([v0, v1, v3], None, "front"),                   # front face
            ([v1, v2, v3], None, "right"),                   # right face
            ([v2, v0, v3], None, "left")                     # left face
        ]
        
        for i, (face_verts, normal, name) in enumerate(faces):
            # Skip base on recursive calls
            if skip_base and i == 0:
                continue
            
            print(f"depth={depth} face={name}")
            
            # Calculate face centroid
            centroid = (face_verts[0] + face_verts[1] + face_verts[2]) / 3
            
            # Calculate face normal if not provided
            if normal is None:
                edge1 = face_verts[1] - face_verts[0]
                edge2 = face_verts[2] - face_verts[0]
                normal = edge1.cross(edge2).normalized()
                # Flip normal to point outward
                normal = -normal
            
            # Create transformation matrix for child tetrahedron
            mat = parent_matrix.copy()
            
            # Move to face centroid
            mat @= Matrix.Translation(centroid)
            
            # Rotate so the base of the new tetrahedron aligns with this face
            # The base of a new tetrahedron points in -Z direction
            base_normal = Vector([0, 0, -1])
            rotation = get_rotation_matrix_to_align(base_normal, normal)
            mat @= rotation
            
            # The new tetrahedron's centroid is at (s/2, sqrt(3)/6*s, 0)
            # We want its base centroid at origin, so offset
            base_centroid = Vector([next_size/2, (math.sqrt(3)/6)*next_size, 0])
            mat @= Matrix.Translation(-base_centroid)
            
            fractal_tetra_simple(next_size, depth - 1, mat, all_meshes, skip_base=True)
    
    return all_meshes

# Clear existing mesh objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Generate fractal
print("Tetrahedral Fractal Parameters:")
print(f"Base Size: {size}")
print(f"Scale Factor: {scale_factor}")
print(f"Recursion Depth: {recursion_depth}")

all_meshes = fractal_tetra_simple(size, recursion_depth, skip_base=True)

# Create objects from meshes with transformations and colors
for i, (mesh, matrix, depth) in enumerate(all_meshes):
    obj = bpy.data.objects.new(f"Tetra_{i}", mesh)
    bpy.context.collection.objects.link(obj)
    
    # Apply transformation matrix
    obj.matrix_world = matrix
    
    # Add color based on depth
    mat = bpy.data.materials.new(name=f"Material_{i}")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    r = depth / recursion_depth
    b = 1 - depth / recursion_depth
    bsdf.inputs['Base Color'].default_value = (r, 0, b, 1)
    bsdf.inputs['Alpha'].default_value = 0.5
    mat.blend_method = 'BLEND'
    
    obj.data.materials.append(mat)

print(f"Created {len(all_meshes)} tetrahedra")