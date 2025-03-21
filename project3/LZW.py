import os  # File operations
import math  # Math functions
from PIL import Image  # Image processing
import numpy as np  # Numerical operations


class LZWCoding:
    def __init__(self, filename, data_type, filepath, outputpath):
        self.filename = filename
        self.data_type = data_type
        self.codelength = None
        self.filepath = filepath
        self.outputpath = outputpath

    def compress_image_file(self):
        # Get paths
        input_path = self.filepath
        input_file = os.path.basename(input_path)
        output_path = self.outputpath
        output_file = os.path.basename(output_path)

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

        #Calculate entropy of difference image
        hist, _ = np.histogram(difference_image.flatten(), bins=511, range=(-255, 256), density=True)
        hist = hist[hist > 0]  # Filter out zero probabilities
        entropy_value_difference_img = -np.sum(hist * np.log2(hist))
        
        # Print results
        print(f"{input_file} is compressed into {output_file}.")
        print(f"Original Size: {original_size:,} bytes")
        print(f"Entropy of original image: {entropy_value:.4f}")
        print(f"Code Length: {self.codelength} bits")
        print(f"Compressed Size: {compressed_size:,} bytes")
        print(f"Compression Ratio: {original_size / compressed_size:.2f}")
        print(f"Entropy of Difference Image: {entropy_value_difference_img:.4f}")

        info = [
            f"{input_file} is compressed into {output_file}.",
            f"Original Size: {original_size:,} bytes",
            f"Entropy of original image: {entropy_value:.4f}",
            f"Code Length: {self.codelength} bits",
            f"Compressed Size: {compressed_size:,} bytes",
            f"Compression Ratio: {original_size / compressed_size:.2f}",
            f"Entropy of Difference Image: {entropy_value_difference_img:.4f}"
        ]


        return output_path, info

    def compute_difference_image(self, image):
        # Convert image to numpy array
        img_array = np.array(image, dtype=np.int16)
        height, width = img_array.shape
        diff_img = np.zeros_like(img_array)
        
        # First pixel stays the same
        diff_img[0, 0] = img_array[0, 0]
        
        # First row: horizontal difference
        for j in range(1, width):
            diff_img[0, j] = img_array[0, j] - img_array[0, j-1]
            
        # First column: vertical difference
        for i in range(1, height):
            diff_img[i, 0] = img_array[i, 0] - img_array[i-1, 0]
            
        # Rest of the image: compute difference from left pixel
        for i in range(1, height):
            for j in range(1, width):
                diff_img[i, j] = img_array[i, j] - img_array[i, j-1]
                
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

        # Initialize dictionary with single symbols (0-510)
        dict_size = 511  # Values range from 0 to 510
        dictionary = {str(i): i for i in range(dict_size)}
        
        # Start with first symbol
        w = str(image_data[0])
        result = []

        # Process the rest of the data
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

        # Add the last pattern
        result.append(dictionary[w])
        
        # Calculate required bits for each code
        self.codelength = math.ceil(math.log2(dict_size))
        
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
        # Get paths
        input_path = self.filepath
        input_file = os.path.basename(input_path)
        output_path = self.outputpath
        output_file = os.path.basename(output_path)

        with open(input_path, 'rb') as in_file:
            bytes_data = in_file.read()

        # Extract width and height
        width = int.from_bytes(bytes_data[:2], byteorder='big')
        height = int.from_bytes(bytes_data[2:4], byteorder='big')
        bytes_data = bytes_data[4:]

        # Convert bytes to binary string
        bit_string = ''.join(format(byte, '08b') for byte in bytes_data)
        
        # Remove padding and extract code length
        bit_string = self.remove_padding(bit_string)
        bit_string = self.extract_code_length_info(bit_string)
        
        # Convert binary string to integer codes
        encoded_data = self.binary_string_to_int_list(bit_string)
        
        # Decode the LZW compression
        diff_data = self.decodeImage(encoded_data)
        
        # Restore original values from 0-510 range
        diff_data = [x - 255 for x in diff_data]
        
        # Reshape to 2D array
        diff_image = np.array(diff_data, dtype=np.int16).reshape(height, width)
        
        # Reconstruct the original image from differences
        original_image = self.reconstruct_from_difference(diff_image)
        
        # Ensure pixel values are in valid range
        restored_image = np.clip(original_image, 0, 255).astype(np.uint8)
        
        # Save as BMP
        img = Image.fromarray(restored_image)
        img.save(output_path)

        print(f"{input_file} is decompressed into {output_file}.")
        print(f"Restored Image Dimensions: {width}x{height}")
        return output_path

    def reconstruct_from_difference(self, diff_image):
        height, width = diff_image.shape
        original_image = np.zeros_like(diff_image)
        
        # First pixel stays the same
        original_image[0, 0] = diff_image[0, 0]
        
        # Reconstruct first row
        for j in range(1, width):
            original_image[0, j] = original_image[0, j-1] + diff_image[0, j]
            
        # Reconstruct first column
        for i in range(1, height):
            original_image[i, 0] = original_image[i-1, 0] + diff_image[i, 0]
            
        # Reconstruct the rest of the image
        for i in range(1, height):
            for j in range(1, width):
                original_image[i, j] = original_image[i, j-1] + diff_image[i, j]
                
        return original_image

    def remove_padding(self, padded_encoded_data):
        extra_bits = int(padded_encoded_data[:8], 2)
        return padded_encoded_data[8:-extra_bits] if extra_bits > 0 else padded_encoded_data[8:]

    def extract_code_length_info(self, bitstring):
        self.codelength = int(bitstring[:8], 2)
        return bitstring[8:]

    def binary_string_to_int_list(self, bitstring):
        return [int(bitstring[i:i+self.codelength], 2) for i in range(0, len(bitstring), self.codelength)]

    def decodeImage(self, encoded_values):
        if not encoded_values:
            return []
            
        # Initialize the dictionary with single values (0-510)
        dictionary = {}
        for i in range(511):
            dictionary[i] = [i]
            
        # Start with first code
        w = dictionary[encoded_values[0]]
        result = w.copy()
        
        # Process the rest of the codes
        for i in range(1, len(encoded_values)):
            k = encoded_values[i]
            
            if k in dictionary:
                entry = dictionary[k]
            elif k == len(dictionary):
                entry = w + [w[0]]
            else:
                raise ValueError(f"Invalid code: {k}")
                
            result.extend(entry)
            
            # Add new pattern to dictionary
            if len(dictionary) < 2**self.codelength:
                dictionary[len(dictionary)] = w + [entry[0]]
                
            w = entry.copy()
            
        return result