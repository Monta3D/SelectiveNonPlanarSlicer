def parse_gcode_line(line):
    """Parse a line of G-code and return a dictionary of its components."""
    parts = line.split()
    cmd = parts[0]
    params = {}
    for part in parts[1:]:
        if part[0] in 'XYZEF':
            params[part[0]] = float(part[1:])
    return cmd, params

def generate_gcode_line(cmd, params):
    """Generate a G-code line from a command and parameters dictionary."""
    line = cmd
    for key, value in params.items():
        line += f" {key}{value:.6f}"
    return line

def translate_coordinates(input_file, output_file, dx, dy, dz):
    with open(input_file, 'r') as f:
        lines = f.readlines()

    new_lines = []

    for line in lines:
        if line.startswith('G') and any(coord in line for coord in 'XYZ'):
            cmd, params = parse_gcode_line(line)
            if 'X' in params:
                params['X'] += dx
            if 'Y' in params:
                params['Y'] += dy
            if 'Z' in params:
                params['Z'] += dz
            if 'E' in params:
                params['E'] += de
            if 'F' in params:
                params['F'] += df
            new_line = generate_gcode_line(cmd, params)
            new_lines.append(new_line + '\n')
        else:
            new_lines.append(line)

    with open(output_file, 'w') as f:
        f.writelines(new_lines)

# Traslation parameters
dx = 1.74
dy = -1.84
dz = -0.10
de = 0
df = 0

# Input and output file
input_file = 'flow\\nonplanar_surf4.gcode'
output_file = 'flow\\nonplanar_surf_4.gcode'

# Run the traslation
translate_coordinates(input_file, output_file, dx, dy, dz)
