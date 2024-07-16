import logging
from random import randint, random

class Hamming1511:
    @staticmethod
    def encode_message(message):
        binary_data = text_to_binary(message)  # Преобразование текста в бинарные данные
        frames = split_into_frames(binary_data, 11)  # Разделение на 11-битовые фреймы

        encoded_frames = []
        for frame in frames:
            # Кодирование каждого фрейма
            encoded_frame = Hamming1511.encode_frame(frame)
            encoded_frames.append(encoded_frame)

        return join_frames(encoded_frames)  # Объединение фреймов в одну строку и возврат

    @staticmethod
    def encode_frame(frame):
        encoded_frame = ['0'] * 15
        j = 0
        for i in range(15):
            if i + 1 not in [1, 2, 4, 8]:  # Skip parity bit positions (1, 2, 4, 8)
                encoded_frame[i] = frame[j]
                j += 1

        encoded_frame[0] = str(Hamming1511.calculate_parity(encoded_frame, [0, 2, 4, 6, 8, 10, 12, 14]))
        encoded_frame[1] = str(Hamming1511.calculate_parity(encoded_frame, [1, 2, 5, 6, 9, 10, 13, 14]))
        encoded_frame[3] = str(Hamming1511.calculate_parity(encoded_frame, [3, 4, 5, 6, 11, 12, 13, 14]))
        encoded_frame[7] = str(Hamming1511.calculate_parity(encoded_frame, [7, 8, 9, 10, 11, 12, 13, 14]))

        return ''.join(encoded_frame)

    @staticmethod
    def calculate_parity(encoded_message, positions):
        parity = 0
        for pos in positions:
            if encoded_message[pos] == '1':
                parity ^= 1
        return parity

    @staticmethod
    def check_error(encoded_message):
        parity1 = Hamming1511.calculate_parity(encoded_message, [0, 2, 4, 6, 8, 10, 12, 14])
        parity2 = Hamming1511.calculate_parity(encoded_message, [1, 2, 5, 6, 9, 10, 13, 14])
        parity4 = Hamming1511.calculate_parity(encoded_message, [3, 4, 5, 6, 11, 12, 13, 14])
        parity8 = Hamming1511.calculate_parity(encoded_message, [7, 8, 9, 10, 11, 12, 13, 14])
        return parity1 + (parity2 << 1) + (parity4 << 2) + (parity8 << 3)

    @staticmethod
    def _replace_at(string, index, replacement):
        if index > len(string) - 1:
            return string
        return string[:index] + replacement + string[index + 1:]

    @staticmethod
    def fixed_error(encoded_message):
        error_index = Hamming1511.check_error(encoded_message)
        if error_index != 0:
            encoded_message = Hamming1511._replace_at(
                encoded_message, error_index - 1,
                '0' if encoded_message[error_index - 1] == '1' else '1'
            )
        return encoded_message

    @staticmethod
    def decode_message(encoded_message):
        frames = split_into_frames(encoded_message, 15)  # Разделение закодированного сообщения на фреймы

        decoded_frames = []
        for frame in frames:
            # Исправление ошибок
            fixed_frame = Hamming1511.fixed_error(frame)
            # Декодирование каждого фрейма
            decoded_frame = Hamming1511.decode_frame(fixed_frame)
            decoded_frames.append(decoded_frame)
        
        return binary_to_text(join_frames(decoded_frames)).rstrip('\x00')  # Преобразование бинарных данных обратно в текст

    @staticmethod
    def decode_frame(encoded_frame):
        decoded_frame = []
        for i in range(15):
            if i + 1 not in [1, 2, 4, 8]:  # Skip parity bit positions
                decoded_frame.append(encoded_frame[i])
        return ''.join(decoded_frame)

def transmit_error(encoded_message, error_probability):
    frames = split_into_frames(encoded_message, 15)  # Разделение закодированного сообщения на фреймы
    # Внесение ошибок в каждый фрейм
    errored_frames = [transmit_error_in_frame(frame, error_probability) for frame in frames]
    # Объединение фреймов обратно в одну строку и возврат
    return join_frames(errored_frames)

def transmit_error_in_frame(frame, error_probability):
    if random() < error_probability:
        error_index = randint(0, len(frame) - 1)
        frame = Hamming1511._replace_at(frame, error_index, '1' if frame[error_index] == '0' else '0')
    return frame

def text_to_binary(text):
    return ''.join(format(ord(char), '016b') for char in text)  # 16 бит для русских символов

def binary_to_text(binary):
    chars = [chr(int(binary[i:i+16], 2)) for i in range(0, len(binary), 16)]
    return ''.join(chars)

def split_into_frames(binary_message, frame_size=11):
    frames = [binary_message[i:i+frame_size] for i in range(0, len(binary_message), frame_size)]
    # Дополнение последнего фрейма до 11 бит, если необходимо
    if len(frames[-1]) < frame_size:
        frames[-1] = frames[-1].ljust(frame_size, '0')
    return frames

def join_frames(frames):
    return ''.join(frames)

# Testing the Hamming1511 class
def test_hamming():
    original_text = "I am fine, thanks"
    binary_data = text_to_binary(original_text)
    print("Original Text:", original_text)
    print("Binary Data:", binary_data)

    # Encode the message
    encoded_message = Hamming1511.encode_message(original_text)
    print("Encoded Message:", encoded_message)

    # Introduce errors into the transmitted data
    errored_message = transmit_error(encoded_message, 0.9)
    print("Errored Message:", errored_message)

    # Decode the message
    decoded_message = Hamming1511.decode_message(errored_message)
    print("Decoded Text:", decoded_message)

# Run the test
test_hamming()
