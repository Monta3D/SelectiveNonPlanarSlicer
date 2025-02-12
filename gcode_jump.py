import math

def calculate_distance(point1, point2):
    """Evaluate the euclide distance between two point in 3D."""
    return math.sqrt((point2['X'] - point1['X'])**2 + (point2['Y'] - point1['Y'])**2)

def parse_gcode_line(line):
    """Extract the coordinate from a G-code line."""
    coordinates = {}
    for part in line.split():
        if part.startswith(('X', 'Y', 'Z', 'E')):
            axis = part[0]
            try:
                coordinates[axis] = float(part[1:])
            except ValueError:
                pass
    return coordinates

def remove_extrusion(line):
    """Remove the E coordinate from a G-code line."""
    return ' '.join(part for part in line.split() if not part.startswith('E'))

def modify_gcode(input_file, output_file):
    """Modify the G-code file to add Z movement when necessary."""
    with open(input_file, 'r') as infile, open(output_file, 'w') as outfile:
        for _ in range(300):  # Jump first 300 lines
            next(infile, None)
        
        previous_point = None
        for line in infile:
            stripped_line = line.strip()
            if stripped_line.startswith('G'):  # Onòly G-code command
                current_point = parse_gcode_line(stripped_line)
                if 'X' in current_point and 'Y' in current_point:  # Ignore command without XY coordinate
                    if previous_point:
                        distance = calculate_distance(previous_point, current_point)
                        if distance > 2:
                            # Define the Z lift refered to the travel distance
                            if distance <= 50:
                                z_lift = 2
                            elif distance <= 80:
                                z_lift = 10
                            elif distance <= 130:
                                z_lift = 30
                            elif distance <= 200:
                                z_lift = 40
                            else:
                                z_lift = 100 
                            
                            max_z = max(previous_point.get('Z', 0), current_point.get('Z', 0))
                            outfile.write(f"G1 Z{max_z + z_lift:.3f}\n")
                            # travel movement without Z and E
                            horizontal_movement = remove_extrusion(f"G1 X{current_point['X']:.3f} Y{current_point['Y']:.3f}")
                            outfile.write(horizontal_movement + "\n")
                            # Z coordinate at the arruval point
                            z_lowering = remove_extrusion(f"G1 Z{current_point['Z']:.3f}")
                            outfile.write(z_lowering + "\n")
                        else:
                            outfile.write(line)
                    else:
                        outfile.write(line)
                    previous_point = current_point
                else:
                    outfile.write(line)
            else:
                # Scrive tutto ciò che non è un comando G-code con coordinate
                outfile.write(line)

# File di input e output
input_file = 'Test dep non planare\\np_auto.gcode'
output_file = 'Test dep non planare\\np_auto_jump.gcode'

# Esegui la modifica del G-code
modify_gcode(input_file, output_file)

print("\nModify completed. File saved as", output_file)
