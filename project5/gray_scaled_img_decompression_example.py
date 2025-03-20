import os
from LZW import LZWCoding

# Geri açılacak dosyanın adı
filename = 'sample_img'

# LZW sınıfını başlat
lzw = LZWCoding(filename)

# Üç `.bin` dosyasını geri aç ve renkli görüntüyü oluştur
output_path = lzw.decompress_image_file()

print("Decompression complete! Image saved as:", output_path)

# Orijinal ve decompressed dosyayı karşılaştır
current_directory = os.path.dirname(os.path.realpath(__file__))

original_file = filename + '.bmp'
original_path = os.path.join(current_directory, original_file)

decompressed_file = filename + '_decompressed.bmp'
decompressed_path = os.path.join(current_directory, decompressed_file)

# Dosyaları binary olarak oku ve karşılaştır
with open(original_path, 'rb') as file1, open(decompressed_path, 'rb') as file2:
    original_bytes = file1.read()
    decompressed_bytes = file2.read()

# Sonucu yazdır
if original_bytes == decompressed_bytes:
    print(f"{original_file} and {decompressed_file} are IDENTICAL ✅")
else:
    print(f"{original_file} and {decompressed_file} are DIFFERENT ❌")