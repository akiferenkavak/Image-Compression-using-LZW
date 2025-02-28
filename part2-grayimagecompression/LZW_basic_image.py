from PIL import Image
import numpy as np
import os
from collections import Counter
import math

def compress_image(image_path, compressed_file):
    """Open an image, apply LZW compression, and save the result."""
    
    print(f"Reading the image from {image_path} and converting it to grayscale...")
    img = Image.open(image_path).convert("L")
    pixels = np.array(img).flatten()
    
    print("Initializing LZW dictionary with standard grayscale values...")
    dict_size = 256
    dictionary = {bytes([i]): i for i in range(dict_size)}
    
    w = bytes()
    compressed = []
    
    print("Processing pixels and performing LZW compression...")
    for pixel in pixels:
        wc = w + bytes([pixel])
        if wc in dictionary:
            w = wc
        else:
            compressed.append(dictionary[w])
            dictionary[wc] = dict_size
            dict_size += 1
            w = bytes([pixel])
    
    if w:
        compressed.append(dictionary[w])
    
    print(f"Writing compressed data to {compressed_file}...")
    with open(compressed_file, "wb") as f:
        for code in compressed:
            f.write(code.to_bytes(2, byteorder='big'))
    
    print("Compression completed successfully.")
    return compressed_file

def decompress_image(compressed_file, output_image_path, original_shape):
    """Load a compressed file, decompress it, and restore the image."""
    
    print(f"Reading compressed data from {compressed_file}...")
    with open(compressed_file, "rb") as f:
        compressed = [int.from_bytes(f.read(2), byteorder='big') for _ in range(os.path.getsize(compressed_file) // 2)]
    
    print("Initializing dictionary for decompression...")
    dict_size = 256
    dictionary = {i: bytes([i]) for i in range(dict_size)}
    
    w = bytes([compressed.pop(0)])
    decompressed = [w]
    
    print("Decoding compressed data back into pixel values...")
    for k in compressed:
        if k in dictionary:
            entry = dictionary[k]
        elif k == dict_size:
            entry = w + w[:1]
        else:
            raise ValueError(f"Invalid compressed code: {k}")
        
        decompressed.append(entry)
        dictionary[dict_size] = w + entry[:1]
        dict_size += 1
        w = entry
    
    print(f"Reconstructing the image and saving to {output_image_path}...")
    pixels = np.frombuffer(b''.join(decompressed), dtype=np.uint8)
    restored_img = Image.fromarray(pixels.reshape(original_shape))
    restored_img.save(output_image_path)
    print("Decompression completed successfully.")
    
    return output_image_path

def calculate_image_metrics(original_image_path, compressed_file):
    """Calculate entropy, compression ratio, and other metrics for analysis."""
    print("Retrieving file sizes for comparison...")
    original_size = os.path.getsize(original_image_path)
    compressed_size = os.path.getsize(compressed_file)
    
    print("Computing pixel distribution to estimate entropy...")
    img = Image.open(original_image_path).convert("L")
    pixels = np.array(img).flatten()
    histogram = Counter(pixels)
    total_pixels = len(pixels)
    entropy = -sum((count / total_pixels) * math.log2(count / total_pixels) for count in histogram.values())
    
    print("Calculating compression statistics...")
    compression_ratio = compressed_size / original_size
    compression_factor = original_size / compressed_size
    space_saving = (original_size - compressed_size) / original_size
    
    print(f"Original File Size: {original_size} bytes")
    print(f"Compressed File Size: {compressed_size} bytes")
    print(f"Compression Ratio: {compression_ratio:.4f}")
    print(f"Compression Factor: {compression_factor:.4f}")
    print(f"Space Saving: {space_saving:.4f}")
    print(f"Entropy: {entropy:.4f} bits/pixel")
    
    return entropy, compression_ratio, compression_factor, space_saving

if __name__ == "__main__":
    image_path = "gray.png"
    compressed_file = "compressed.lzw"
    restored_image_path = "restored_image.png"
    
    print("Extracting original image dimensions...")
    img = Image.open(image_path).convert("L")
    original_shape = img.size[::-1]
    
    print("Starting the compression process...")
    compress_image(image_path, compressed_file)
    
    print("Beginning the decompression process...")
    decompress_image(compressed_file, restored_image_path, original_shape)
    
    print("Analyzing compression efficiency...")
    calculate_image_metrics(image_path, compressed_file)