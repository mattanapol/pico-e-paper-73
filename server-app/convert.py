#encoding: utf-8

import sys
import os.path
from PIL import Image, ImagePalette, ImageOps
import time

def convert(input_filename, 
            display_direction = None, 
            display_mode = 'scale', 
            display_dither = Image.FLOYDSTEINBERG):
    # Check whether the input file exists
    if not os.path.isfile(input_filename):
        print(f'Error: file {input_filename} does not exist')
        sys.exit(1)

    # Read input image
    input_image = Image.open(input_filename)

    # Get the original image size
    width, height = input_image.size

    # Specified target size
    if display_direction:
        if display_direction == 'landscape':
            target_width, target_height = 800, 480
        else:
            target_width, target_height = 480, 800
    else:
        if  width > height:
            target_width, target_height = 800, 480
        else:
            target_width, target_height = 480, 800
        
    if display_mode == 'scale':
        # Computed scaling
        scale_ratio = max(target_width / width, target_height / height)

        # Calculate the size after scaling
        resized_width = int(width * scale_ratio)
        resized_height = int(height * scale_ratio)

        # Resize image
        output_image = input_image.resize((resized_width, resized_height))

        # Create the target image and center the resized image
        resized_image = Image.new('RGB', (target_width, target_height), (255, 255, 255))
        left = (target_width - resized_width) // 2
        top = (target_height - resized_height) // 2
        resized_image.paste(output_image, (left, top))
    elif display_mode == 'cut':
        # Calculate the fill size to add or the area to crop
        if width / height >= target_width / target_height:
            # The image aspect ratio is larger than the target aspect ratio, and padding needs to be added on the left and right
            delta_width = int(height * target_width / target_height - width)
            padding = (delta_width // 2, 0, delta_width - delta_width // 2, 0)
            box = (0, 0, width, height)
        else:
            # The image aspect ratio is smaller than the target aspect ratio and needs to be filled up and down
            delta_height = int(width * target_height / target_width - height)
            padding = (0, delta_height // 2, 0, delta_height - delta_height // 2)
            box = (0, 0, width, height)

        resized_image = ImageOps.pad(input_image.crop(box), size=(target_width, target_height), color=(255, 255, 255), centering=(0.5, 0.5))


    # Create a palette object
    pal_image = Image.new("P", (1,1))
    pal_image.putpalette( (0,0,0,  255,255,255,  0,255,0,   0,0,255,  255,0,0,  255,255,0, 255,128,0) + (0,0,0)*249)
    
    # The color quantization and dithering algorithms are performed, and the results are converted to RGB mode
    quantized_image = resized_image.quantize(dither=display_dither, palette=pal_image).convert('RGB')

    # Save output image
    time_str = time.strftime('%Y%m%d%H%M%S%f', time.localtime())
    # output_filename = os.path.splitext(input_filename)[0] + '_' + display_mode + '_output.bmp'
    output_filename = f'{time_str}.bmp'
    quantized_image.save(output_filename)

    print(f'Successfully converted {input_filename} to {output_filename}')
    return output_filename

