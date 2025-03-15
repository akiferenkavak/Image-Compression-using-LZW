from LZW import LZWCoding

# read and compress the file sample.bmp
filename = 'sample_gray_scaled'
lzw = LZWCoding(filename, 'image')
output_path = lzw.compress_image_file()