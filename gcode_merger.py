
file_path = "Test dep non planare\\hill_hole_0.2mm_PLA_X1_2h59m.gcode"
gcode_surf1 = "Test dep non planare\\np_hill_hole.gcode"
gcode_surf2 = "comp_utensile\\Empty.gcode"
gcode_surf3 = "comp_utensile\\Empty.gcode"
gcode_surf4 = "comp_utensile\\Empty.gcode"

new_file_path = "Test dep non planare\\marrige_hill_hole.gcode"
num_parola = 2      #number of the word from the top

# Empty file is necessary if we want to merge less than 4 non planar surface "\\Empty.gcode"

count = 0

# Keyword
keyword = "stop printing object"   #stop printing object (2)    #non planar layer (1)

# Read the first gcode surface file
with open(gcode_surf1, 'r') as first_file:
    gcode_surf1 = first_file.readlines()

# Read the second gcode surface file
with open(gcode_surf2, 'r') as second_file:
    gcode_surf2 = second_file.readlines()

# Read the third gcode surface file
with open(gcode_surf3, 'r') as third_file:
    gcode_surf3 = third_file.readlines()

# Read the fourth gcode surface file
with open(gcode_surf4, 'r') as fourth_file:
    gcode_surf4 = fourth_file.readlines()

# Read the main gcode file
with open(file_path, 'r') as file:
    lines = file.readlines()

# Find the index of the line containing the keyword
index = None
for i, line in enumerate(lines):
    if keyword in line:              # Search the keyword
        count = count + 1
        if count == num_parola:
            index = i
            break

# Verify if the word has been found
if index is not None and index + 1 < len(lines):
    lines.insert(index + 1, "\n\n;Spazio 1\n\n")
    lines[index + 2:index + 2] = gcode_surf1
    index = index + 2 + len(gcode_surf1)        #index refresh
    lines.insert(index, "\n\n;Spazio 2\n\n")

    lines[index + 1:index + 1] = gcode_surf2
    index = index + 2 + len(gcode_surf2)        #index refresh
    lines.insert(index, "\n\n;Spazio 3\n\n")

    lines[index + 1:index + 1] = gcode_surf3
    index = index + 2 + len(gcode_surf3)        #index refresh
    lines.insert(index, "\n\n;Spazio 4\n\n")

    lines[index + 1:index + 1] = gcode_surf4
    index = index + 2 + len(gcode_surf4)        #index refresh
    lines.insert(index, "\n\n;Spazio 5\n\n")
else:
    print(f"The keyword '{keyword}' is not in the main file.")

# Write the modified content back to a new file
with open(new_file_path, 'w') as new_file:
    new_file.writelines(lines)
