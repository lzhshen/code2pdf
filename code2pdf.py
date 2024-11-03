import os
import sys
import argparse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.units import mm

def register_custom_font(font_path):
    """Registers the DejaVuSansMono.ttf font."""
    font_name = 'DejaVuSansMono'
    pdfmetrics.registerFont(TTFont(font_name, font_path))
    return font_name

def filter_directories(dirs):
    """Filters out directories starting with '.' and '__pycache__'."""
    return [d for d in dirs if not (d.startswith('.') or d == '__pycache__')]

def build_directory_tree(root_dir):
    """Builds a directory tree structure."""
    dir_tree = []
    file_paths = []

    for current_path, dirs, files in os.walk(root_dir):
        # Filter out unwanted directories
        dirs[:] = filter_directories(dirs)
        relative_path = os.path.relpath(current_path, root_dir)
        indent_level = relative_path.count(os.sep)
        dir_tree.append(('    ' * indent_level) + os.path.basename(current_path) + '/')

        # Add files
        for file in files:
            file_path = os.path.join(current_path, file)
            file_relative_path = os.path.relpath(file_path, root_dir)
            dir_tree.append(('    ' * (indent_level + 1)) + file)
            file_paths.append(file_relative_path)

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

def write_files_to_pdf(c, root_dir, file_paths, font_name, font_size, text_pos):
    """Writes the contents of each file to the PDF."""
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
                    c.drawString(text_pos[0], text_pos[1], line.rstrip())
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
    font_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'DejaVuSansMono.ttf')

    if not os.path.exists(font_path):
        print(f"Font file 'DejaVuSansMono.ttf' not found in the script directory.")
        sys.exit(1)

    # Register the custom font
    font_name = register_custom_font(font_path)

    # Build the directory tree and get the list of file paths
    dir_tree, file_paths = build_directory_tree(project_directory)

    # Create the PDF
    c = canvas.Canvas(output_pdf, pagesize=A4)
    font_size = 10
    text_pos = [20 * mm, A4[1] - 50 * mm]  # Starting position

    # Write the directory tree to the PDF
    text_pos = write_directory_tree_to_pdf(c, dir_tree, font_name, font_size, text_pos)

    # Write the files content to the PDF
    text_pos = write_files_to_pdf(c, project_directory, file_paths, font_name, font_size, text_pos)

    # Save the PDF
    c.save()
    print(f"PDF generated successfully: {output_pdf}")

if __name__ == "__main__":
    main()