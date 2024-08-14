import argparse
import convert
from PIL import Image

# Create an ArgumentParser object
parser = argparse.ArgumentParser(description='Process some images.')

# Add orientation parameter
parser.add_argument('image_file', type=str, help='Input image file')
parser.add_argument('--dir', choices=['landscape', 'portrait'], help='Image direction (landscape or portrait)')
parser.add_argument('--mode', choices=['scale', 'cut'], default='scale', help='Image conversion mode (scale or cut)')
parser.add_argument('--dither', type=int, choices=[Image.NONE, Image.FLOYDSTEINBERG], default=Image.FLOYDSTEINBERG, help='Image dithering algorithm (NONE(0) or FLOYDSTEINBERG(3))')

# Parse command line arguments
args = parser.parse_args()

# Get input parameter
input_filename = args.image_file
display_direction = args.dir
display_mode = args.mode
display_dither = Image.Dither(args.dither)

convert.convert(input_filename, display_direction, display_mode, display_dither)