import os  # the os module is used for file and directory operations
import math  # the math module provides access to mathematical functions
from PIL import Image  # the Image class is used for image operations
import numpy as np  # the numpy library is used for numerical

# A class that implements the LZW compression and decompression algorithms as
# well as the necessary utility methods for text files.
# ------------------------------------------------------------------------------
class LZWCoding:
   # A constructor with two input parameters
   # ---------------------------------------------------------------------------
   def __init__(self, filename, data_type):
      # use the input parameters to set the instance variables
      self.filename = filename
      self.data_type = data_type   # e.g., 'text'
      # initialize the code length as None 
      # (the actual value is determined based on the compressed data)
      self.codelength = None






   # A method that compresses the contents of an image file to a binary output
   # file and returns the path of the output file.
   # ---------------------------------------------------------------------------
   def compress_image_file(self):
    current_directory = os.path.dirname(os.path.realpath(__file__))
    input_file = self.filename + '.bmp'
    input_path = os.path.join(current_directory, input_file)

    output_file = self.filename + '.bin'
    output_path = os.path.join(current_directory, output_file)

    # Görüntüyü oku ve fark görüntüsünü oluştur
    image = Image.open(input_path).convert('L')
    width, height = image.size
    difference_image = self.compute_difference_image(image)

    # Fark görüntüsünü 1D diziye çevir
    diff_data = difference_image.flatten().tolist()

    # LZW sıkıştırma uygula
    encoded_data = self.encodeGrayScaledImage(diff_data)
    encoded_string = self.int_list_to_binary_string(encoded_data)
    encoded_string = self.add_code_length_info(encoded_string)
    padded_encoded_string = self.pad_encoded_data(encoded_string)
    byte_array = self.get_byte_array(padded_encoded_string)

    # Width ve height bilgilerini dosyaya ekle
    width_bytes = width.to_bytes(2, byteorder='big')
    height_bytes = height.to_bytes(2, byteorder='big')

    with open(output_path, 'wb') as out_file:
        out_file.write(width_bytes + height_bytes + bytes(byte_array))

    # Entropi hesapla
    entropy_value = self.calculate_entropy(input_path)
    original_size = os.path.getsize(input_path)
    compressed_size = len(byte_array) + 4  # 4 byte = width + height

    # Sonuçları yazdır
    print(f"{input_file} is compressed into {output_file}.")
    print(f"Original Size: {original_size:,} bytes")
    print(f"Entropy: {entropy_value:.4f}")
    print(f"Code Length: {self.codelength} bits")
    print(f"Compressed Size: {compressed_size:,} bytes")
    print(f"Compression Ratio: {original_size / compressed_size:.2f}")

    return output_path
   


   def compute_difference_image(self, image):
        """ Compute the difference image using row-wise and column-wise differences """
        img_array = np.array(image, dtype=np.int16)

        # İlk sütunu sakla, geri kalanı satır farkına çevir
        diff_img = np.zeros_like(img_array)
        diff_img[:, 0] = img_array[:, 0]  # İlk sütun olduğu gibi kalsın

        # Satır farkı hesapla
        diff_img[:, 1:] = img_array[:, 1:] - img_array[:, :-1]

        # İlk piksel pivot olarak alınır, kalan sütun farkı hesaplanır
        diff_img[1:, 0] -= diff_img[:-1, 0]

        return diff_img



   def calculate_entropy(self, image_path):
      # Load the grayscale image
      img = Image.open(image_path).convert("L")  # Convert to grayscale if not already
    
      # Convert image to a NumPy array
      img_array = np.array(img)
    
      # Compute histogram (256 bins for grayscale images)
      hist, _ = np.histogram(img_array, bins=256, range=(0, 256), density=True)
    
      # Remove zero probabilities to avoid log(0) errors
      hist = hist[hist > 0]
    
      # Compute entropy
      entropy = -np.sum(hist * np.log2(hist))
    
      return entropy
   
   

   # A method that encodes the grayscale image data into a list of integer values
   # by using the LZW compression algorithm and returns the resulting list.
   # ---------------------------------------------------------------------------
   def encodeGrayScaledImage(self, image_data):
      # Görüntü verisi boşsa, boş liste döndür
      if not image_data:
         return []
      
      # Başlangıç sözlüğünü oluştur (0-255 arasındaki değerler için)
      dict_size = 256
      dictionary = {}
      for i in range(dict_size):
         dictionary[str(i)] = i  # Anahtarları string olarak saklıyoruz
      
      w = str(image_data[0])  # İlk değeri alıp string'e çevir
      result = []
      
      # İkinci değerden itibaren kodlama işlemini başlat
      for i in range(1, len(image_data)):
         k = str(image_data[i])
         wk = w + "," + k
         
         if wk in dictionary:
               w = wk
         else:
               result.append(dictionary[w])
               dictionary[wk] = dict_size
               dict_size += 1
               w = k
      
      # Son karakter dizisini ekle
      result.append(dictionary[w])
      
      self.codelength = np.ceil(np.log2(len(dictionary))).astype(int)
      return result

   # A method that converts the integer list returned by the compress method
   # into a binary string and returns the resulting string.
   # ---------------------------------------------------------------------------
   def int_list_to_binary_string(self, int_list):
      # initialize the binary string as an empty string
      bitstring = ''
      # concatenate each integer in the input list to the binary string
      for num in int_list:
         # using codelength bits to compress each value
         for n in range(self.codelength):
            if num & (1 << (self.codelength - 1 - n)):
               bitstring += '1'
            else:
               bitstring += '0'
      # return the resulting binary string
      return bitstring

   # A method that adds the code length to the beginning of the binary string
   # that corresponds to the compressed data and returns the resulting string.
   # (the compressed data should contain everything needed to decompress it)
   # ---------------------------------------------------------------------------
   def add_code_length_info(self, bitstring):
      # create a binary string that stores the code length as a byte
      codelength_info = '{0:08b}'.format(self.codelength)
      # add the code length info to the beginning of the given binary string
      bitstring = codelength_info + bitstring
      # return the resulting binary string
      return bitstring

   # A method for adding zeros to the binary string (the compressed data)
   # to make the length of the string a multiple of 8.
   # (This is necessary to be able to write the values to the file as bytes.)
   # ---------------------------------------------------------------------------
   def pad_encoded_data(self, encoded_data):
      # compute the number of the extra bits to add
      if len(encoded_data) % 8 != 0:
         extra_bits = 8 - len(encoded_data) % 8
         # add zeros to the end (padding)
         for i in range(extra_bits):
            encoded_data += '0'
      else:   # no need to add zeros
         extra_bits = 0
      # add a byte that stores the number of added zeros to the beginning of
      # the encoded data
      padding_info = '{0:08b}'.format(extra_bits)
      encoded_data = padding_info + encoded_data
      # return the resulting string after padding
      return encoded_data

   # A method that converts the padded binary string to a byte array and returns 
   # the resulting array. 
   # (This byte array will be written to a file to store the compressed data.)
   # ---------------------------------------------------------------------------
   def get_byte_array(self, padded_encoded_data):
      # the length of the padded binary string must be a multiple of 8
      if (len(padded_encoded_data) % 8 != 0):
         print('The compressed data is not padded properly!')
         exit(0)
      # create a byte array
      b = bytearray()
      # append the padded binary string to byte by byte
      for i in range(0, len(padded_encoded_data), 8):
         byte = padded_encoded_data[i : i + 8]
         b.append(int(byte, 2))
      # return the resulting byte array
      return b
   

   # A method to remove the padding info and the added zeros from the compressed
   # binary string and return the resulting string.
   def remove_padding(self, padded_encoded_data):
      # extract the padding info (the first 8 bits of the input string)
      padding_info = padded_encoded_data[:8]
      encoded_data = padded_encoded_data[8:]
      # remove the extra zeros (if any) and return the resulting string
      extra_padding = int(padding_info, 2) 
      if extra_padding != 0:
         encoded_data = encoded_data[:-1 * extra_padding]
      return encoded_data

   def extract_code_length_info(self, bitstring):
      # the first 8 bits of the input string contains the code length info
      codelength_info = bitstring[:8]
      self.codelength = int(codelength_info, 2)
      # return the resulting binary string after removing the code length info
      return bitstring[8:]
   
   # A method that converts the compressed binary string to a list of int codes
   # and returns the resulting list.
   # ---------------------------------------------------------------------------
   def binary_string_to_int_list(self, bitstring):
      # generate the list of integer codes from the binary string
      int_codes = []
      # for each compressed value (a binary string with codelength bits)
      for bits in range(0, len(bitstring), self.codelength):
         # compute the integer code and add it to the list
         int_code = int(bitstring[bits: bits + self.codelength], 2)
         int_codes.append(int_code)
      # return the resulting list
      return int_codes

   # A method that reads the contents of a compressed binary file, performs
   # decompression and writes the decompressed output to a text file.
   # ---------------------------------------------------------------------------
   def decompress_image_file(self):
    current_directory = os.path.dirname(os.path.realpath(__file__))
    input_file = self.filename + '.bin'
    input_path = os.path.join(current_directory, input_file)
    output_file = self.filename + '_decompressed.bmp'
    output_path = os.path.join(current_directory, output_file)

    with open(input_path, 'rb') as in_file:
        bytes_data = in_file.read()

    # İlk 4 byte genişlik ve yükseklik bilgisi
    width = int.from_bytes(bytes_data[:2], byteorder='big')
    height = int.from_bytes(bytes_data[2:4], byteorder='big')
    bytes_data = bytes_data[4:]

    # Sıkıştırılmış veriyi oku
    bit_string = ''.join(bin(byte)[2:].rjust(8, '0') for byte in bytes_data)
    bit_string = self.remove_padding(bit_string)
    bit_string = self.extract_code_length_info(bit_string)
    encoded_data = self.binary_string_to_int_list(bit_string)
    diff_data = self.decodeImage(encoded_data)

    # Difference Image'i geri 2D forma çevir
    diff_image = np.array(diff_data, dtype=np.int16).reshape(height, width)

    # Orijinal görüntüyü farklardan geri oluştur
    original_image = np.zeros_like(diff_image)

    # İlk sütunu aynen al
    original_image[:, 0] = diff_image[:, 0]

    # Satır farklarını geri al
    for j in range(1, width):
        original_image[:, j] = original_image[:, j - 1] + diff_image[:, j]

    # İlk satırı aynen al, geri kalan sütunları tamamla
    for i in range(1, height):
        original_image[i, 0] = original_image[i - 1, 0] + diff_image[i, 0]

    # 0-255 arasına getir ve uint8 formatına çevir
    restored_image = np.clip(original_image, 0, 255).astype(np.uint8)

    # Görüntüyü kaydet
    img = Image.fromarray(restored_image)
    img.save(output_path)

    print(f"{input_file} is decompressed into {output_file}.")
    print(f"Restored Image Dimensions: {width}x{height}")
    return output_path
   
   # A method that decodes a list of encoded integer values into a string (text) 
   # by using the LZW decompression algorithm and returns the resulting output.
   # ---------------------------------------------------------------------------
   def decodeImage(self, encoded_values):
      # Build initial dictionary for grayscale images (0-255 values)
      dict_size = 256
      dictionary = {}
      for i in range(dict_size):
         dictionary[i] = [i]  # Piksel değerlerini liste olarak saklıyoruz
      
      # Boş veri kontrolü
      if not encoded_values:
         return []
      
      # İlk değeri al
      w = dictionary[encoded_values[0]]
      result = w.copy()  # Sonuç listesine ekle
      
      # Diğer kodlanmış değerleri çözümle
      for i in range(1, len(encoded_values)):
         k = encoded_values[i]
         
         # Sözlükte varsa değeri al
         if k in dictionary:
               entry = dictionary[k]
         # Özel durum: k sözlük boyutuna eşitse
         elif k == dict_size:
               entry = w + [w[0]]  # İlk karakteri tekrarla
         else:
               raise ValueError('Bad compressed k: %s' % k)
         
         # Sonuç listesine ekle
         result.extend(entry)
         
         # Sözlüğe yeni değer ekle
         dictionary[dict_size] = w + [entry[0]]
         dict_size += 1
         
         # w'yu güncelle
         w = entry
      
      return result