import os
import math
import numpy as np
from PIL import Image


class LZWCoding:
    def __init__(self, filename):
        self.filename = filename
        self.codelength = None

    def compress_image_file(self):
        current_directory = os.path.dirname(os.path.realpath(__file__))
        input_file = self.filename + '.bmp'
        input_path = os.path.join(current_directory, input_file)

        image = Image.open(input_path).convert('RGB')
        width, height = image.size
        r, g, b = image.split()

        # R, G, B bileşenlerini Difference Image işleminden geçir
        r_diff = self.compute_difference_image(np.array(r))
        g_diff = self.compute_difference_image(np.array(g))
        b_diff = self.compute_difference_image(np.array(b))

        # Her kanal için sıkıştırma işlemini uygula
        self.compress_channel(r_diff, width, height, '_R.bin')
        self.compress_channel(g_diff, width, height, '_G.bin')
        self.compress_channel(b_diff, width, height, '_B.bin')

        print(f"Compression completed for {input_file}")

    def compress_channel(self, channel_data, width, height, suffix):
        channel_data = channel_data.flatten().tolist()
        channel_data = [x + 255 for x in channel_data]  # -255 ile 255 arasını 0-510 arasına kaydır

        encoded_data = self.encodeGrayScaledImage(channel_data)
        encoded_string = self.int_list_to_binary_string(encoded_data)
        encoded_string = self.add_code_length_info(encoded_string)
        padded_encoded_string = self.pad_encoded_data(encoded_string)
        byte_array = self.get_byte_array(padded_encoded_string)

        output_path = f"{self.filename}{suffix}"
        with open(output_path, 'wb') as out_file:
            out_file.write(width.to_bytes(2, byteorder='big'))
            out_file.write(height.to_bytes(2, byteorder='big'))
            out_file.write(bytes(byte_array))

        print(f"Saved compressed channel: {output_path}")

    def compute_difference_image(self, img_array):
        img_array = img_array.astype(np.int16)
        diff_img = np.zeros_like(img_array)
        diff_img[:, 0] = img_array[:, 0]
        diff_img[:, 1:] = img_array[:, 1:] - img_array[:, :-1]
        diff_img[1:, 0] -= diff_img[:-1, 0]
        return diff_img

    def encodeGrayScaledImage(self, image_data):
        if not image_data:
            return []

        dict_size = 511
        dictionary = {str(i): i for i in range(dict_size)}
        w = str(image_data[0])
        result = []

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

        result.append(dictionary[w])
        self.codelength = np.ceil(np.log2(len(dictionary))).astype(int)
        return result

    def int_list_to_binary_string(self, int_list):
        return "".join(format(num, f'0{self.codelength}b') for num in int_list)

    def add_code_length_info(self, bitstring):
        return format(self.codelength, '08b') + bitstring

    def pad_encoded_data(self, encoded_data):
        extra_bits = (8 - len(encoded_data) % 8) % 8
        padding_info = format(extra_bits, '08b')
        return padding_info + encoded_data + '0' * extra_bits

    def get_byte_array(self, padded_encoded_data):
        return bytearray(int(padded_encoded_data[i:i+8], 2) for i in range(0, len(padded_encoded_data), 8))

    def decompress_image_file(self):
        r_channel = self.decompress_channel('_R.bin')
        g_channel = self.decompress_channel('_G.bin')
        b_channel = self.decompress_channel('_B.bin')

        img = Image.merge("RGB", (r_channel, g_channel, b_channel))
        output_path = self.filename + "_decompressed.bmp"
        img.save(output_path)
        print(f"Decompressed image saved as {output_path}")

    def decompress_channel(self, suffix):
        input_path = self.filename + suffix
        with open(input_path, 'rb') as in_file:
            bytes_data = in_file.read()

        width = int.from_bytes(bytes_data[:2], byteorder='big')
        height = int.from_bytes(bytes_data[2:4], byteorder='big')
        bytes_data = bytes_data[4:]

        bit_string = "".join(bin(byte)[2:].rjust(8, '0') for byte in bytes_data)
        bit_string = self.remove_padding(bit_string)
        bit_string = self.extract_code_length_info(bit_string)
        encoded_data = self.binary_string_to_int_list(bit_string)
        diff_data = self.decodeImage(encoded_data)

        # Shift back from 0-510 range to -255 to 255
        diff_data = [x - 255 for x in diff_data]
        diff_image = np.array(diff_data, dtype=np.int16).reshape(height, width)

        # **DÜZELTİLEN GERI TOPLAMA ALGORİTMASI**
        original_image = np.zeros_like(diff_image, dtype=np.int16)

        # **İlk sütun doğru hesaplanıyor**
        original_image[:, 0] = diff_image[:, 0]
        for i in range(1, height):
            original_image[i, 0] += original_image[i - 1, 0]  # Sütun farklarını topla

        # **İlk satır doğru hesaplanıyor**
        for j in range(1, width):
            original_image[:, j] = original_image[:, j - 1] + diff_image[:, j]  # Satır farklarını topla

        return Image.fromarray(np.clip(original_image, 0, 255).astype(np.uint8))

    def remove_padding(self, padded_encoded_data):
        extra_bits = int(padded_encoded_data[:8], 2)
        return padded_encoded_data[8:-extra_bits] if extra_bits > 0 else padded_encoded_data[8:]

    def extract_code_length_info(self, bitstring):
        self.codelength = int(bitstring[:8], 2)
        return bitstring[8:]

    def binary_string_to_int_list(self, bitstring):
        return [int(bitstring[i:i+self.codelength], 2) for i in range(0, len(bitstring), self.codelength)]

    def decodeImage(self, encoded_values):
        dictionary = {i: [i] for i in range(511)}
        w = dictionary[encoded_values.pop(0)]
        result = w.copy()

        for k in encoded_values:
            entry = dictionary[k] if k in dictionary else w + [w[0]]
            result.extend(entry)
            dictionary[len(dictionary)] = w + [entry[0]]
            w = entry

        return result
