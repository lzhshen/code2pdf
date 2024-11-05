import os
import sys
import argparse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.units import mm
from matplotlib import font_manager
import pathspec  # Import the pathspec library

def register_custom_font(font_name):
    """Registers the specified font from the system."""
    font_path = None
    for font in font_manager.findSystemFonts(fontpaths=None, fontext='ttf'):
        try:
            if font_name in font_manager.get_font(font).family_name:
                font_path = font
                break
        except RuntimeError:
            continue  # Ignore any fonts that cause errors

    if font_path:
        pdfmetrics.registerFont(TTFont(font_name, font_path))
        print(f"Font '{font_name}' registered from system path: {font_path}")
    else:
        print(f"Font '{font_name}' not found in the system.")
        sys.exit(1)

    return font_name

def normalize_path(path):
    """Normalize path separators to '/'."""
    return path.replace(os.sep, '/')

def parse_ignore_file(root_dir):
    """Parses the .ignore file and returns a PathSpec object."""
    ignore_path = os.path.join(root_dir, '.ignore')
    if not os.path.exists(ignore_path):
        return None

    with open(ignore_path, 'r', encoding='utf-8') as f:
        ignore_patterns = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    spec = pathspec.PathSpec.from_lines('gitignore', ignore_patterns)
    return spec

def should_ignore(path, spec):
    """Checks if the given path matches any of the ignore patterns."""
    if spec is None:
        return False
    # Normalize the path before matching
    path = normalize_path(path)
    # Handle the case where the path is '.'
    if path == '.':
        path = ''
    return spec.match_file(path)

def filter_directories(dirs, current_path, spec, root_dir):
    """Filters out directories based on the ignore patterns."""
    dirs_to_keep = []
    for d in dirs:
        dir_path = os.path.join(current_path, d)
        rel_path = os.path.relpath(dir_path, root_dir)
        rel_path = normalize_path(rel_path)
        # Add a trailing slash to directories when matching
        rel_path_with_slash = rel_path + '/'
        if not should_ignore(rel_path, spec) and not should_ignore(rel_path_with_slash, spec):
            dirs_to_keep.append(d)
        else:
            print(f"Excluding directory: {rel_path}")
    dirs[:] = dirs_to_keep  # Modify dirs in-place to affect os.walk traversal

def build_directory_tree(root_dir):
    """Builds a directory tree structure."""
    dir_tree = []
    file_paths = []

    spec = parse_ignore_file(root_dir)

    for current_path, dirs, files in os.walk(root_dir):
        # Filter out unwanted directories
        filter_directories(dirs, current_path, spec, root_dir)
        relative_path = os.path.relpath(current_path, root_dir)
        relative_path = normalize_path(relative_path)
        if relative_path == '.':
            indent_level = 0
            dir_name = '/'
        else:
            indent_level = relative_path.count('/')
            dir_name = os.path.basename(current_path) + '/'
        dir_tree.append(('    ' * indent_level) + dir_name)

        # Add files
        for file in files:
            file_path = os.path.join(current_path, file)
            file_relative_path = os.path.relpath(file_path, root_dir)
            file_relative_path = normalize_path(file_relative_path)
            if not should_ignore(file_relative_path, spec):
                dir_tree.append(('    ' * (indent_level + 1)) + file)
                file_paths.append(file_relative_path)
            else:
                print(f"Excluding file: {file_relative_path}")

    return dir_tree, file_paths

def write_directory_tree_to_pdf(c, dir_tree, font_name, font_size, text_pos):
    """Writes the directory tree to the PDF."""
    c.setFont(font_name, font_size)
    for line in dir_tree:
        c.drawString(text_pos[0], text_pos[1], line)
        text_pos[1] -= font_size * 1.2  # Move down for next line
        if text_pos[1] < 50 * mm:  # Check for page break
            c.showPage()
            c.setFont(font_name, font_size)
            text_pos[1] = A4[1] - 50 * mm
    c.showPage()
    return text_pos

def wrap_text(text, max_width, font_name, font_size, c):
    """Wraps text to fit within a given width."""
    words = text.split()
    lines = []
    current_line = ""
    for word in words:
        test_line = current_line + word + " "
        if c.stringWidth(test_line, font_name, font_size) > max_width:
            lines.append(current_line.strip())
            current_line = word + " "
        else:
            current_line = test_line
    if current_line:
        lines.append(current_line.strip())
    return lines

def write_files_to_pdf(c, root_dir, file_paths, font_name, font_size, text_pos):
    """Writes the contents of each file to the PDF."""
    max_width = A4[0] - 40 * mm  # 20mm margin on both sides
    for file_relative_path in file_paths:
        file_path = os.path.join(root_dir, file_relative_path)
        # Write the file path as a heading
        c.setFont(font_name, font_size + 2)
        c.drawString(text_pos[0], text_pos[1], file_relative_path)
        text_pos[1] -= (font_size + 2) * 1.5

        if text_pos[1] < 50 * mm:
            c.showPage()
            c.setFont(font_name, font_size)
            text_pos[1] = A4[1] - 50 * mm

        # Write the file content
        c.setFont(font_name, font_size)
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    # Calculate the indentation level in spaces
                    indent_level = len(line) - len(line.lstrip())
                    # Remove trailing whitespace and newlines
                    line_content = line.rstrip()
                    # Wrap the line content while preserving indentation
                    wrapped_lines = wrap_text(line_content, max_width - indent_level * 4, font_name, font_size, c)
                    for wrapped_line in wrapped_lines:
                        # Draw the line with the correct indentation
                        c.drawString(text_pos[0] + indent_level * 4, text_pos[1], wrapped_line)
                        text_pos[1] -= font_size * 1.2
                        if text_pos[1] < 50 * mm:
                            c.showPage()
                            c.setFont(font_name, font_size)
                            text_pos[1] = A4[1] - 50 * mm
        except Exception as e:
            # Handle any errors reading the file
            c.drawString(text_pos[0], text_pos[1], f"Error reading file: {e}")
            text_pos[1] -= font_size * 1.2

        # Add some space before the next file
        text_pos[1] -= font_size * 2
        if text_pos[1] < 50 * mm:
            c.showPage()
            c.setFont(font_name, font_size)
            text_pos[1] = A4[1] - 50 * mm

    return text_pos

def main():
    parser = argparse.ArgumentParser(description='Convert source code files into a PDF document.')
    parser.add_argument('project_directory', help='The path to the project directory.')
    parser.add_argument('output_pdf', help='The output PDF file name.')
    args = parser.parse_args()

    project_directory = args.project_directory
    output_pdf = args.output_pdf
    font_name = 'WenQuanYi Micro Hei'  # Change this to a font available on your system if needed

    # Register the custom font from the system
    font_name = register_custom_font(font_name)

    # Build the directory tree and get the list of file paths
    dir_tree, file_paths = build_directory_tree(project_directory)

    # Create the PDF
    c = canvas.Canvas(output_pdf, pagesize=A4)
    font_size = 10
    text_pos = [20 * mm, A4[1] - 50 * mm]  # Starting position

    # Write the directory tree to the PDF
    text_pos = write_directory_tree_to_pdf(c, dir_tree, font_name, font_size, text_pos)

    # Write the files' content to the PDF
    text_pos = write_files_to_pdf(c, project_directory, file_paths, font_name, font_size, text_pos)

    # Save the PDF
    c.save()
    print(f"PDF generated successfully: {output_pdf}")

if __name__ == "__main__":
    main()