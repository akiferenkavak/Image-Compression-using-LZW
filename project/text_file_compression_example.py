from LZW import LZWCoding

# read and compress the file sample.txt
filename = 'sample'
lzw = LZWCoding(filename, 'text')
output_path = lzw.compress_text_file()
