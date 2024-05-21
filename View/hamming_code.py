from math import log2, ceil

def encode_message(message):
    # Метод для кодирования сообщения [15,11]-кодом Хэмминга
    # Добавление контрольных битов
    data_bits = list(message)
    n = len(data_bits)
    m = ceil(log2(n + 1))
    encoded_message = ['0'] * (n + m)
    j = 0
    k = 0
    for i in range(n + m):
        if (i + 1) & i:  # проверка на степень двойки
            encoded_message[i] = data_bits[j]
            j += 1
        else:
            encoded_message[i] = '0'
    # Вычисление контрольных битов
    for i in range(m):
        encoded_message[2**i - 1] = str(calculate_parity(encoded_message, i))
    return ''.join(encoded_message)

def calculate_parity(encoded_message, parity_bit_index):
    # Вычисление значения контрольного бита
    parity = 0
    for i in range(len(encoded_message)):
        if i & (1 << parity_bit_index):
            if encoded_message[i] == '1':
                parity = parity ^ 1
    return parity

def decode_message(message):
    # Метод для декодирования сообщения [15,11]-кодом Хэмминга
    # Вычисление индекса ошибочного бита
    n = len(message)
    m = ceil(log2(n + 1))
    error_index = 0
    for i in range(m):
        parity = calculate_parity(message, i)
        if parity != int(message[2**i - 1]):
            error_index += 2**i
    if error_index != 0:
        # Исправление ошибки
        message = message[:error_index - 1] + ('0' if message[error_index - 1] == '1' else '1') + message[error_index:]
    # Удаление контрольных битов
    decoded_message = ''
    for i in range(len(message)):
        if not ((i + 1) & i):
            decoded_message += message[i]
    return decoded_message