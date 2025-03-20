import os
import numpy as np
from PIL import Image

class LZWCoding:
    def __init__(self, filename, data_type, filepath, outputpath):
        self.filename = filename
        self.codelength = None
        self.data_type = data_type
        self.filepath = filepath
        self.outputpath = outputpath

    def compress_image_file(self):
        # Get paths
        input_path = self.filepath
        input_file = os.path.basename(input_path)
        output_path = self.outputpath
        output_file = os.path.basename(output_path)

        image = Image.open(input_path).convert('RGB')
        width, height = image.size
        r, g, b = image.split()

        # Her kanal için sıkıştırma işlemi uygula
        self.compress_channel(np.array(r), width, height, '_R.bin')
        self.compress_channel(np.array(g), width, height, '_G.bin')
        self.compress_channel(np.array(b), width, height, '_B.bin')

        original_size = os.path.getsize(input_path)
        compressed_size = sum(os.path.getsize(output_path + suffix) for suffix in ['_R.bin', '_G.bin', '_B.bin'])
        compression_ratio = original_size / compressed_size

        print(f"Compression completed for {input_file}")
        info = [f"Width: {width}, Height: {height}",
                f"Original size: {original_size} bytes",
                f"Compressed size: {compressed_size} bytes",
                f"Compression ratio: {compression_ratio
                }"
                ]

        return [output_file + '_R.bin', output_file + '_G.bin', output_file + '_B.bin'], info

    def compress_channel(self, channel_data, width, height, suffix):
        channel_data = channel_data.flatten().tolist()

        encoded_data = self.encodeGrayScaledImage(channel_data)
        encoded_string = self.int_list_to_binary_string(encoded_data)
        encoded_string = self.add_code_length_info(encoded_string)
        padded_encoded_string = self.pad_encoded_data(encoded_string)
        byte_array = self.get_byte_array(padded_encoded_string)

       # output_path = f"{self.filename}{suffix}"
        output_path = self.outputpath + suffix
        with open(output_path, 'wb') as out_file:
            out_file.write(width.to_bytes(2, byteorder='big'))
            out_file.write(height.to_bytes(2, byteorder='big'))
            out_file.write(bytes(byte_array))

        print(f"Saved compressed channel: {output_path}")

    def encodeGrayScaledImage(self, image_data):
        if not image_data:
            return []

        dict_size = 256
        dictionary = {bytes([i]): i for i in range(dict_size)}
        w = bytes([image_data[0]])
        result = []

        for i in range(1, len(image_data)):
            k = bytes([image_data[i]])
            wk = w + k
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
        output_path = self.outputpath + "_decompressed.bmp"
        img.save(output_path)
        print(f"Decompressed image saved as {output_path}")

        return output_path

    def decompress_channel(self, suffix):
        #input_path = self.filename + suffix
        input_path = self.filepath + suffix
        with open(input_path, 'rb') as in_file:
            bytes_data = in_file.read()

        width = int.from_bytes(bytes_data[:2], byteorder='big')
        height = int.from_bytes(bytes_data[2:4], byteorder='big')
        bytes_data = bytes_data[4:]

        bit_string = "".join(bin(byte)[2:].rjust(8, '0') for byte in bytes_data)
        bit_string = self.remove_padding(bit_string)
        bit_string = self.extract_code_length_info(bit_string)
        encoded_data = self.binary_string_to_int_list(bit_string)
        decoded_data = self.decodeImage(encoded_data)

        image_array = np.array(decoded_data, dtype=np.uint8).reshape(height, width)
        return Image.fromarray(image_array)

    def remove_padding(self, padded_encoded_data):
        extra_bits = int(padded_encoded_data[:8], 2)
        return padded_encoded_data[8:-extra_bits] if extra_bits > 0 else padded_encoded_data[8:]

    def extract_code_length_info(self, bitstring):
        self.codelength = int(bitstring[:8], 2)
        return bitstring[8:]

    def binary_string_to_int_list(self, bitstring):
        return [int(bitstring[i:i+self.codelength], 2) for i in range(0, len(bitstring), self.codelength)]

    def decodeImage(self, encoded_values):
        dictionary = {i: bytes([i]) for i in range(256)}
        w = dictionary[encoded_values.pop(0)]
        result = bytearray(w)

        for k in encoded_values:
            if k in dictionary:
                entry = dictionary[k]
            elif k == len(dictionary):
                entry = w + w[:1]
            else:
                raise ValueError("Decompression error: Invalid dictionary key")

            result.extend(entry)
            dictionary[len(dictionary)] = w + entry[:1]
            w = entry

        return list(result)