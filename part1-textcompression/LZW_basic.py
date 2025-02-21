import os

def compress(uncompressed):
    """Performs LZW compression and returns the compressed integer codes."""
    dict_size = 256
    dictionary = {chr(i): i for i in range(dict_size)}

    w = ""
    result = []
    for c in uncompressed:
        wc = w + c
        if wc in dictionary:
            w = wc
        else:
            result.append(dictionary[w])
            dictionary[wc] = dict_size
            dict_size += 1
            w = c

    if w:
        result.append(dictionary[w])
    
    return result

def decompress(compressed):
    """Decompresses the LZW compressed integer codes back to the original text."""
    from io import StringIO

    dict_size = 256
    dictionary = {i: chr(i) for i in range(dict_size)}

    result = StringIO()
    w = chr(compressed.pop(0))
    result.write(w)
    
    for k in compressed:
        if k in dictionary:
            entry = dictionary[k]
        elif k == dict_size:
            entry = w + w[0]  # Special case: The new entry is not yet in the dictionary
        else:
            raise ValueError(f'Invalid compressed code: {k}')
        
        result.write(entry)
        dictionary[dict_size] = w + entry[0]
        dict_size += 1
        w = entry
    
    return result.getvalue()


def save_compressed_to_file(compressed, filename="compressed.bin"):
    """Writes the compressed integer sequence to a binary file."""
    binary_string = ''.join(format(num, '016b') for num in compressed)  # Convert integers to 16-bit binary strings
    padding = 8 - (len(binary_string) % 8)  # Calculate padding to make length a multiple of 8
    binary_string = format(padding, '08b') + binary_string + ('0' * padding)  # Add padding information at the beginning
    
    byte_array = bytearray(int(binary_string[i:i+8], 2) for i in range(0, len(binary_string), 8))
    
    with open(filename, "wb") as f:
        f.write(byte_array)


def read_compressed_from_file(filename="compressed.bin"):
    """Reads a binary compressed file and converts it back to an integer sequence."""
    with open(filename, "rb") as f:
        byte_data = f.read()
    
    binary_string = ''.join(format(byte, '08b') for byte in byte_data)
    padding = int(binary_string[:8], 2)  # The first 8 bits indicate the number of padding bits added
    binary_string = binary_string[8:-padding] if padding else binary_string[8:]  # Remove padding
    
    compressed = [int(binary_string[i:i+16], 2) for i in range(0, len(binary_string), 16)]  # Convert back to 16-bit integers
    
    return compressed


def calculate_compression_metrics(original_file, compressed_file):
    """Calculates and prints compression metrics."""
    original_size = os.path.getsize(original_file)
    compressed_size = os.path.getsize(compressed_file)
    
    CR = compressed_size / original_size  # Compression Ratio
    CF = original_size / compressed_size  # Compression Factor
    SS = (original_size - compressed_size) / original_size  # Space Saving

    print(f"Original File Size: {original_size} bytes")
    print(f"Compressed File Size: {compressed_size} bytes")
    print(f"Compression Ratio (CR): {CR:.4f}")
    print(f"Compression Factor (CF): {CF:.4f}")
    print(f"Space Saving (SS): {SS:.4f}")


def lzw_compression_pipeline(input_filename="input.txt", compressed_filename="compressed.bin", decompressed_filename="decompressed.txt"):
    """Executes the entire LZW compression and decompression process."""
    
    # Read the original text
    with open(input_filename, "r", encoding="utf-8") as f:
        original_text = f.read()
    
    # Perform LZW compression
    compressed_data = compress(original_text)
    
    # Save the compressed data to a file
    save_compressed_to_file(compressed_data, compressed_filename)
    
    # Read the compressed file and decompress
    compressed_data_from_file = read_compressed_from_file(compressed_filename)
    decompressed_text = decompress(compressed_data_from_file)
    
    # Save the decompressed text to a file
    with open(decompressed_filename, "w", encoding="utf-8") as f:
        f.write(decompressed_text)
    
    # Compare the original and decompressed text
    if original_text == decompressed_text:
        print("Successfully compressed and decompressed. The original text matches perfectly!")
    else:
        print("Error: The decompressed text does not match the original.")
    
    # Calculate and display compression metrics
    calculate_compression_metrics(input_filename, compressed_filename)


# Run the pipeline:
lzw_compression_pipeline()
