import os  # File operations
import math  # Math functions
from PIL import Image  # Image processing
import numpy as np  # Numerical operations


class LZWCoding:
    def __init__(self, filename, data_type):
        self.filename = filename
        self.data_type = data_type
        self.codelength = None

    def compress_image_file(self):
        current_directory = os.path.dirname(os.path.realpath(__file__))
        input_file = self.filename + '.bmp'
        input_path = os.path.join(current_directory, input_file)

        output_file = self.filename + '.bin'
        output_path = os.path.join(current_directory, output_file)

        # Read image and compute difference image
        image = Image.open(input_path).convert('L')
        width, height = image.size
        difference_image = self.compute_difference_image(image)

        # Flatten difference image into 1D array
        diff_data = difference_image.flatten().tolist()

        # Shift values to 0-510 range (since original is -255 to 255)
        diff_data = [x + 255 for x in diff_data]

        # Apply LZW compression
        encoded_data = self.encodeGrayScaledImage(diff_data)
        encoded_string = self.int_list_to_binary_string(encoded_data)
        encoded_string = self.add_code_length_info(encoded_string)
        padded_encoded_string = self.pad_encoded_data(encoded_string)
        byte_array = self.get_byte_array(padded_encoded_string)

        # Save width, height, and compressed data
        width_bytes = width.to_bytes(2, byteorder='big')
        height_bytes = height.to_bytes(2, byteorder='big')

        with open(output_path, 'wb') as out_file:
            out_file.write(width_bytes + height_bytes + bytes(byte_array))

        # Calculate entropy
        entropy_value = self.calculate_entropy(input_path)
        original_size = os.path.getsize(input_path)
        compressed_size = len(byte_array) + 4  # 4 bytes for width, height

        # Print results
        print(f"{input_file} is compressed into {output_file}.")
        print(f"Original Size: {original_size:,} bytes")
        print(f"Entropy: {entropy_value:.4f}")
        print(f"Code Length: {self.codelength} bits")
        print(f"Compressed Size: {compressed_size:,} bytes")
        print(f"Compression Ratio: {original_size / compressed_size:.2f}")

        return output_path

    def compute_difference_image(self, image):
        img_array = np.array(image, dtype=np.int16)
        diff_img = np.zeros_like(img_array)
        diff_img[:, 0] = img_array[:, 0]  # Keep first column
        diff_img[:, 1:] = img_array[:, 1:] - img_array[:, :-1]  # Row-wise difference
        diff_img[1:, 0] -= diff_img[:-1, 0]  # Column-wise difference
        return diff_img

    def calculate_entropy(self, image_path):
        img = Image.open(image_path).convert("L")
        img_array = np.array(img)
        hist, _ = np.histogram(img_array, bins=256, range=(0, 256), density=True)
        hist = hist[hist > 0]
        entropy = -np.sum(hist * np.log2(hist))
        return entropy

    def encodeGrayScaledImage(self, image_data):
        if not image_data:
            return []

        dict_size = 511  # Since values are between 0 and 510
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
        bitstring = ""
        for num in int_list:
            bitstring += format(num, f'0{self.codelength}b')
        return bitstring

    def add_code_length_info(self, bitstring):
        return format(self.codelength, '08b') + bitstring

    def pad_encoded_data(self, encoded_data):
        extra_bits = (8 - len(encoded_data) % 8) % 8
        padding_info = format(extra_bits, '08b')
        return padding_info + encoded_data + '0' * extra_bits

    def get_byte_array(self, padded_encoded_data):
        return bytearray(int(padded_encoded_data[i:i+8], 2) for i in range(0, len(padded_encoded_data), 8))

    def decompress_image_file(self):
        current_directory = os.path.dirname(os.path.realpath(__file__))
        input_file = self.filename + '.bin'
        input_path = os.path.join(current_directory, input_file)
        output_file = self.filename + '_decompressed.bmp'
        output_path = os.path.join(current_directory, output_file)

        with open(input_path, 'rb') as in_file:
            bytes_data = in_file.read()

        width = int.from_bytes(bytes_data[:2], byteorder='big')
        height = int.from_bytes(bytes_data[2:4], byteorder='big')
        bytes_data = bytes_data[4:]

        bit_string = ''.join(bin(byte)[2:].rjust(8, '0') for byte in bytes_data)
        bit_string = self.remove_padding(bit_string)
        bit_string = self.extract_code_length_info(bit_string)
        encoded_data = self.binary_string_to_int_list(bit_string)
        diff_data = self.decodeImage(encoded_data)

        # Restore original values from 0-510 range
        diff_data = [x - 255 for x in diff_data]
        diff_image = np.array(diff_data, dtype=np.int16).reshape(height, width)

        original_image = np.zeros_like(diff_image)
        original_image[:, 0] = diff_image[:, 0]

        for j in range(1, width):
            original_image[:, j] = original_image[:, j - 1] + diff_image[:, j]

        for i in range(1, height):
            original_image[i, 0] = original_image[i - 1, 0] + diff_image[i, 0]

        restored_image = np.clip(original_image, 0, 255).astype(np.uint8)
        img = Image.fromarray(restored_image)
        img.save(output_path)

        print(f"{input_file} is decompressed into {output_file}.")
        print(f"Restored Image Dimensions: {width}x{height}")
        return output_path

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
