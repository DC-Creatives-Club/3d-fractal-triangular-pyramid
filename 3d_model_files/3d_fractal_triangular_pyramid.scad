// Parameters
size = 30;
nozzle_width = 0.4;
scale_factor = 0.5;
recursion_depth = 3;

module tetra(s) {
    points = [
        [0, 0, 0],
        [s, 0, 0],
        [s/2, (sqrt(3)/2)*s, 0],
        [s/2, (sqrt(3)/6)*s, sqrt(6)/3 * s]
    ];
    faces = [
        [0, 1, 2],  // base
        [0, 1, 3],  // side 1
        [1, 2, 3],  // side 2
        [2, 0, 3]   // side 3
    ];
    polyhedron(points=points, faces=faces);
}


// Simpler approach using known tetrahedron geometry
module fractal_tetra_simple(s, depth) {
    if (s >= nozzle_width && depth > 0) {
        //echo(str("depth: ", depth, " size: " , s))
        color([depth/recursion_depth, 0, 1-depth/recursion_depth], 0.5) tetra(s);
        
        next_size = s * scale_factor;
            // For a regular tetrahedron, we can use known angles
            // The angle between adjacent faces is about 70.5 degrees
            
            // Face centers at 2/3 height for the three upper faces
            h = sqrt(6)/3 * s;  // tetrahedron height
            face_height = h * 2/3;
            
            // Front face
            // u = [s,0,0], v = [s/2,sqrt(3)/6 * s, sqrt(6)/3 * s]
            echo(str("depth=", depth, " face=front"));
            rotate([acos(1/3), 0, 0])  // this is arccos(1/3) ~ 70.53deg
            translate(0.18 * [s,0,0])
            translate(0.15 * [s/2,sqrt(3)/2 * s, 0])
            fractal_tetra_simple(next_size, depth - 1);
            
            // Right face
            // u = [s, 0, 0], v = [s/2, sqrt(3)/6 * s, sqrt(6)/3 * s];
            echo(str("depth=", depth, " face=right"));
            rotate([2*(90-acos(1/3)), 0, 60]) // twice the angle between the face and 90deg
            translate(0.18 * [s, 0, 0])
            translate(0.15 * [s/2, sqrt(3)/6 * s, sqrt(6)/3 * s])
            fractal_tetra_simple(next_size, depth - 1);
            
            // Left face
            // u = [-s/2, -sqrt(3)/2 * s, 0], v = [0, -sqrt(3)/3 * s, sqrt(6)/3 * s];
            echo(str("depth=", depth, " face=left"));
            edge_vector = [1/2, (sqrt(3)/2), 0]; // [s,0,0] - [s/2,(sqrt(3)/2)*s,0]
            translate([3/4 * s, sqrt(3)/4 * s, 0])
            rotate([0, 0, 60])
            rotate(-2*(90-acos(1/3)), edge_vector)
            translate(-0.18 * [s/2, sqrt(3)/2 * s, 0])
            translate(0.15 * [0, -sqrt(3)/3 * s, sqrt(6)/3 * s])
            fractal_tetra_simple(next_size, depth - 1);
    }
}

// Main call - try the simple version first
fractal_tetra_simple(size, recursion_depth);

echo("Tetrahedral Fractal Parameters:");
echo(str("Base Size: ", size));
echo(str("Scale Factor: ", scale_factor));  
echo(str("Recursion Depth: ", recursion_depth));