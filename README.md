# SelectiveNonPlanarSlicer
CustomSurfaceSlicer is a tool for generating G-code with customizable non-planar printing paths for 3-axis machine. It allows users to select and optimize specific surfaces to enhance the quality and mechanical properties of 3D-printed components, overcoming the limitations of traditional slicers.


# Main advantage:
- no restrictions on the slicer used to generate the G-code for the parallel-layered portion;
- the ability to select specific surfaces for non-planar methodology application;
- the flexibility to modify the extracted surface according to design requirements;
- the capability to introduce new deposition patterns;


The main code generates the non-planar path, while the auxiliary scripts are useful for making small modifications.

*gcodeexport.py*

Executes the generation of the non-planar layer.


Important information:
  - Modify printing parameters (lines 91-115).
  - Modify directory and filename of the mesh file (line 265).
  - Adjust the maximum trajectory size: increase for large objects, decrease for small objects to avoid long processing times.
  - If separate surfaces are not available (line 274):
      - The splitSTLsurfaces function writes to the directory separated_stl_files/non_planar_surface0.stl.
      - If separate surfaces are already available (line 274):
  - Modify the directory and filename of the mesh to match the exact location of the first file.
  - Adjust the maximum angle for keeping the surface non-planar (line 268).
  - The output G-code is saved in the NonPlanarSlicer-main directory (line 121 states that it saves with the filename non_planar + date).
  - The G-code is generated only for non-planar surface 0, ignoring others. If not all extracted surfaces are relevant, rerun the code while changing the filename for G-code generation.


*gcode_merger.py*

Merges up to 4 G-code files for the same component.

  - Modify the planar layer file (at the beginning).
  - Modify the non-planar layer file (at the beginning).
  - Modify the final output file (at the end).


*gcode_shift.py*

Applies a translation on X, Y, and Z to a G-code file.

  - Modify the displacement delta for each axis (at the end).
  - Modify input and output file names (at the end).


*gcode_jump.py*

Skips sections that involve only movement and not material deposition to prevent collision.

  - Modify travel distances and heights.
  - Modify input and output files.
