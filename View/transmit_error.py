from random import random

def transmit_error(encoded_message, error_probability):
    # Метод для внесения ошибки в переданное сообщение с заданной вероятностью
    transmitted_message = ''
    for bit in encoded_message:
        if random() < error_probability:
            # Инвертируем бит с вероятностью error_probability
            transmitted_message += '1' if bit == '0' else '0'
        else:
            transmitted_message += bit
    return transmitted_message