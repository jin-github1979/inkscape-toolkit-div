import os
import subprocess
import sys
from bs4 import BeautifulSoup
import shutil

class SVGOptimizer:
    def __init__(self, input_dir, output_dir):
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.ensure_output_dir()

    def ensure_output_dir(self):
        """Ensure the output directory exists."""
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def optimize_svg_with_bs4(self, svg_file):
        """Optimize a single SVG file using BeautifulSoup for basic cleanup."""
        try:
            input_path = os.path.join(self.input_dir, svg_file)
            output_path = os.path.join(self.output_dir, svg_file)

            with open(input_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Parse and prettify SVG using BeautifulSoup
            soup = BeautifulSoup(content, 'xml')
            
            # Remove comments
            for comment in soup.find_all(string=lambda text: isinstance(text, str) and text.strip().startswith('<!--')):
                comment.extract()
            
            # Write optimized SVG
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(str(soup))

            print(f"Optimized: {svg_file} -> saved to {output_path}")
            return output_path

        except Exception as e:
            print(f"Error optimizing {svg_file}: {str(e)}")
            # Fallback: just copy the file
            try:
                shutil.copy2(os.path.join(self.input_dir, svg_file), 
                           os.path.join(self.output_dir, svg_file))
                return os.path.join(self.output_dir, svg_file)
            except Exception as copy_error:
                print(f"Failed to copy {svg_file}: {str(copy_error)}")
                return None

    def optimize_svg(self, svg_file):
        """Optimize a single SVG file, trying svgo first, falling back to Python implementation."""
        try:
            input_path = os.path.join(self.input_dir, svg_file)
            output_path = os.path.join(self.output_dir, svg_file)

            # Try SVGO command if available
            result = subprocess.run(['svgo', input_path, '-o', output_path],
                                    check=True, text=True, capture_output=True)

            print(f"Optimized with SVGO: {svg_file} -> saved to {output_path}")
            return output_path

        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            if isinstance(e, FileNotFoundError):
                print(f"SVGO not found, using Python fallback for {svg_file}")
            else:
                print(f"SVGO error for {svg_file}: {e.stderr}")
            
            # Fallback to Python-based optimization
            return self.optimize_svg_with_bs4(svg_file)

        except Exception as e:
            print(f"Unexpected error with {svg_file}: {str(e)}")
            return None

    def optimize_all_svgs(self):
        """Optimize all SVG files in the input directory."""
        try:
            if not os.path.exists(self.input_dir):
                print(f"Input directory does not exist: {self.input_dir}")
                return
            
            svg_files = [f for f in os.listdir(self.input_dir) if f.endswith('.svg')]
        except PermissionError:
            print(f"Permission denied accessing directory: {self.input_dir}")
            return
        except Exception as e:
            print(f"Error accessing input directory: {str(e)}")
            return
        
        if not svg_files:
            print("No SVG files found in the input directory.")
            return
        
        for svg_file in svg_files:
            self.optimize_svg(svg_file)

if __name__ == "__main__":
    # Basic command line interface for the script
    if len(sys.argv) != 3:
        print("Usage: python optimize_svg.py <input_directory> <output_directory>")
        sys.exit(1)

    input_directory = sys.argv[1]
    output_directory = sys.argv[2]

    optimizer = SVGOptimizer(input_directory, output_directory)
    optimizer.optimize_all_svgs()

# TODO: Add support for more SVGO options.
# TODO: Implement logging instead of print statements for better monitoring.
# TODO: Handle edge cases with non-SVG files in input directory.
# TODO: Enhance Python-based optimization using other listed dependencies like svgpathtools
