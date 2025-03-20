import os  # the os module is used for file and directory operations
import math  # the math module provides access to mathematical functions
from PIL import Image  # the Image class is used for image operations
import numpy as np  # the numpy library is used for numerical

# A class that implements the LZW compression and decompression algorithms as
# well as the necessary utility methods for text files.
# ------------------------------------------------------------------------------
class LZWCoding:
    # Constructor with input parameters
    def __init__(self, filename, data_type, filepath, outputpath):
        # Use the input parameters to set the instance variables
        self.filename = filename
        self.data_type = data_type   # e.g., 'text' or 'image'
        # Initialize the code length as None 
        # (the actual value is determined based on the compressed data)
        self.codelength = None
        self.filepath = filepath
        self.outputpath = outputpath

    # Method that compresses the contents of an image file to a binary output file
    def compress_image_file(self):
        # Get paths
        input_path = self.filepath
        input_file = os.path.basename(input_path)
        output_path = self.outputpath
        output_file = os.path.basename(output_path)

        # Read the contents of the input file
        image = Image.open(input_path).convert('L')
        width, height = image.size  # Get width and height
        image_data = np.array(image, dtype=np.uint8).flatten().tolist()

        # Encode the image data by using the LZW compression algorithm
        encoded_image_as_integers = self.encodeGrayScaledImage(image_data)
        encoded_image = self.int_list_to_binary_string(encoded_image_as_integers)
        encoded_image = self.add_code_length_info(encoded_image)
        padded_encoded_image = self.pad_encoded_data(encoded_image)
        byte_array = self.get_byte_array(padded_encoded_image)

        # Width and Height information in binary format (2 bytes width, 2 bytes height)
        width_bytes = width.to_bytes(2, byteorder='big')  
        height_bytes = height.to_bytes(2, byteorder='big')

        # Write width and height to the compressed file
        with open(output_path, 'wb') as out_file:
            out_file.write(width_bytes + height_bytes + bytes(byte_array))

        # Calculate entropy
        entropy_value = self.calculate_entropy(input_path)

        # Get original file size (in bytes)
        original_file_size = os.path.getsize(input_path)

        # Compression statistics
        compressed_size = len(byte_array) + 4  # 4 bytes = width + height
        compression_ratio = original_file_size / compressed_size

        info = [
            f"{input_file} is compressed into {output_file}.",
            f"Original Image Size: {width}x{height} ({width * height:,} pixels)",
            f"Original File Size: {original_file_size:,} bytes",
            f"Entropy of the image: {entropy_value:.4f}",
            f"Code Length: {self.codelength} bits",
            f"Compressed File Size: {compressed_size:,} bytes",
            f"Compression Ratio: {compression_ratio:.2f}"
        ]

        return output_path, info

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

    # Method that encodes the grayscale image data using LZW compression
    def encodeGrayScaledImage(self, image_data):
        # If image data is empty, return empty list
        if not image_data:
            return []
        
        # Create initial dictionary (values 0-255)
        dict_size = 256
        dictionary = {}
        for i in range(dict_size):
            dictionary[str(i)] = i  # Store keys as strings
        
        w = str(image_data[0])  # Get first value and convert to string
        result = []
        
        # Start coding from the second value
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
        
        # Add the last character sequence
        result.append(dictionary[w])
        
        self.codelength = np.ceil(np.log2(len(dictionary))).astype(int)
        return result

    # Method to convert integer list to binary string
    def int_list_to_binary_string(self, int_list):
        # Initialize the binary string as an empty string
        bitstring = ''
        # Concatenate each integer in the input list to the binary string
        for num in int_list:
            # Using codelength bits to compress each value
            for n in range(self.codelength):
                if num & (1 << (self.codelength - 1 - n)):
                    bitstring += '1'
                else:
                    bitstring += '0'
        # Return the resulting binary string
        return bitstring

    # Method to add code length info to the binary string
    def add_code_length_info(self, bitstring):
        # Create a binary string that stores the code length as a byte
        codelength_info = '{0:08b}'.format(self.codelength)
        # Add the code length info to the beginning of the given binary string
        bitstring = codelength_info + bitstring
        # Return the resulting binary string
        return bitstring

    # Method for padding the binary string to make the length a multiple of 8
    def pad_encoded_data(self, encoded_data):
        # Compute the number of extra bits to add
        if len(encoded_data) % 8 != 0:
            extra_bits = 8 - len(encoded_data) % 8
            # Add zeros to the end (padding)
            for i in range(extra_bits):
                encoded_data += '0'
        else:   # No need to add zeros
            extra_bits = 0
        # Add a byte that stores the number of added zeros to the beginning
        padding_info = '{0:08b}'.format(extra_bits)
        encoded_data = padding_info + encoded_data
        # Return the resulting string after padding
        return encoded_data

    # Method to convert padded binary string to byte array
    def get_byte_array(self, padded_encoded_data):
        # The length of the padded binary string must be a multiple of 8
        if (len(padded_encoded_data) % 8 != 0):
            print('The compressed data is not padded properly!')
            exit(0)
        # Create a byte array
        b = bytearray()
        # Append the padded binary string byte by byte
        for i in range(0, len(padded_encoded_data), 8):
            byte = padded_encoded_data[i : i + 8]
            b.append(int(byte, 2))
        # Return the resulting byte array
        return b

    # Method to remove padding info and added zeros
    def remove_padding(self, padded_encoded_data):
        # Extract the padding info (first 8 bits)
        padding_info = padded_encoded_data[:8]
        encoded_data = padded_encoded_data[8:]
        # Remove the extra zeros if any
        extra_padding = int(padding_info, 2) 
        if extra_padding != 0:
            encoded_data = encoded_data[:-1 * extra_padding]
        return encoded_data

    # Method to extract code length info
    def extract_code_length_info(self, bitstring):
        # The first 8 bits contain the code length info
        codelength_info = bitstring[:8]
        self.codelength = int(codelength_info, 2)
        # Return the binary string after removing the code length info
        return bitstring[8:]
   
    # Method to convert binary string to integer list
    def binary_string_to_int_list(self, bitstring):
        # Generate list of integer codes from binary string
        int_codes = []
        # For each compressed value (binary string with codelength bits)
        for bits in range(0, len(bitstring), self.codelength):
            # Compute the integer code and add it to the list
            int_code = int(bitstring[bits: bits + self.codelength], 2)
            int_codes.append(int_code)
        # Return the resulting list
        return int_codes

    # Method to decompress an image file
    def decompress_image_file(self):
        # Assume filepath given by GUI
        input_path = self.filepath
        input_file = os.path.basename(input_path)
        output_path = self.outputpath
        output_file = os.path.basename(output_path)

        with open(input_path, 'rb') as in_file:
            bytes_data = in_file.read()

        # First 4 bytes contain width and height info
        width = int.from_bytes(bytes_data[:2], byteorder='big')
        height = int.from_bytes(bytes_data[2:4], byteorder='big')

        # Compressed data (after width and height)
        bytes_data = bytes_data[4:]

        # Convert to binary string
        bit_string = ''.join(bin(byte)[2:].rjust(8, '0') for byte in bytes_data)

        bit_string = self.remove_padding(bit_string)
        bit_string = self.extract_code_length_info(bit_string)
        encoded_image = self.binary_string_to_int_list(bit_string)
        decompressed_image = self.decodeImage(encoded_image)

        # Recreate the image with correct dimensions
        img = Image.fromarray(np.array(decompressed_image, dtype=np.uint8).reshape(height, width))
        img.save(output_path)

        # Get decompressed file size
        decompressed_file_size = os.path.getsize(output_path)

        # Print decompression information
        print(f"{input_file} is decompressed into {output_file}.")
        print(f"Restored Image Dimensions: {width}x{height}")
        print(f"Decompressed File Size: {decompressed_file_size:,} bytes")

        return output_path
   
    # Method that decodes a list of encoded integer values using LZW decompression
    def decodeImage(self, encoded_values):
        # Build initial dictionary for grayscale images (0-255 values)
        dict_size = 256
        dictionary = {}
        for i in range(dict_size):
            dictionary[i] = [i]  # Store pixel values as lists
        
        # Check for empty data
        if not encoded_values:
            return []
        
        # Get first value
        w = dictionary[encoded_values[0]]
        result = w.copy()  # Add to result list
        
        # Decode other encoded values
        for i in range(1, len(encoded_values)):
            k = encoded_values[i]
            
            # If in dictionary, get the value
            if k in dictionary:
                entry = dictionary[k]
            # Special case: k equals dictionary size
            elif k == dict_size:
                entry = w + [w[0]]  # Repeat first character
            else:
                raise ValueError('Bad compressed k: %s' % k)
            
            # Add to result list
            result.extend(entry)
            
            # Add new value to dictionary
            dictionary[dict_size] = w + [entry[0]]
            dict_size += 1
            
            # Update w
            w = entry
        
        return result
    
    # Methods for text compression and decompression (placeholders)
    def compress_text_file(self):
        # This should be implemented in your other LZW code
        # Return a dummy result for now
        return self.outputpath, ["Text compression not implemented in this example"]
    
    def decompress_text_file(self):
        # This should be implemented in your other LZW code
        # Return a dummy result for now
        return self.outputpath
    
    # Methods for colored image compression and decompression (placeholders)
    def compress_colored_image_file(self):
        # This should be implemented in your other LZW code
        # Return a dummy result for now
        return self.outputpath, ["Colored image compression not implemented in this example"]
    
    def decompress_colored_image_file(self):
        # This should be implemented in your other LZW code
        # Return a dummy result for now
        return self.outputpath