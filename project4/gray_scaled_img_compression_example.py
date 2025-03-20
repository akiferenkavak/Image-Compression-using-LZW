from LZW import LZWCoding

# Sıkıştırılacak dosyanın adı (renkli BMP dosyası)
filename = 'sample_img'

# LZW sıkıştırma sınıfını başlat
lzw = LZWCoding(filename)

# Görüntüyü sıkıştır (R, G, B bileşenlerini ayrı sıkıştırır)
output_paths = lzw.compress_image_file()

print("Compression complete! The following files were generated:")
print(output_paths)