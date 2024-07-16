import logging
import asyncio
from rest_framework.decorators import api_view
from rest_framework.response import Response
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from .hamming_code import Hamming1511, transmit_error
import requests
from random import random
import json

# Настройка логирования
logger = logging.getLogger(__name__)

segment_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'data': openapi.Schema(type=openapi.TYPE_STRING),
        'num': openapi.Schema(type=openapi.TYPE_INTEGER),
        'size': openapi.Schema(type=openapi.TYPE_INTEGER),
        'time': openapi.Schema(type=openapi.TYPE_INTEGER),
    },
    example={
        'data': 'Sample data',
        'num': 4,
        'size': 15,
        'time': 1711902448
    }
)

@swagger_auto_schema(
    method='post',
    request_body=segment_schema,
    responses={
        200: openapi.Schema(type=openapi.TYPE_OBJECT, properties={'status': openapi.Schema(type=openapi.TYPE_STRING)}),
        400: "Ошибка: данные сегмента потеряны",
        500: "Внутренняя ошибка сервера"
    }
)
@api_view(['POST'])
def receive_segment(request):
    """
    Получает сегмент, в случае положительного ответа, отправляет сегмент на обработку
    и дальнейшую отправку на транспортный уровень
    """
    logger.info("Запрос получен")

    try:
        # Получение данных в формате JSON из запроса
        request_data = request.data
        logger.info(f"Получен запрос: {request_data}")

        data = request_data.get('data')
        num = request_data.get('num')
        size = request_data.get('size')
        time = request_data.get('time')

        if not data or num is None or size is None or time is None:
            logger.error('Данные сегмента потеряны')
            return Response({'error': 'Данные сегмента потеряны'}, status=400)

        segment = {
            'data': data,
            'num': num,
            'size': size,
            'time': time,
        }
        process_segment(request_data)
        return Response({'status': 'Сегмент получен'}, status=200)
    except json.JSONDecodeError:
        logger.exception('Ошибка декодирования JSON')
        return Response({'error': 'Ошибка декодирования JSON'}, status=400)
    except Exception as e:
        logger.exception('Внутренняя ошибка сервера')
        return Response({'error': 'Внутренняя ошибка сервера'}, status=500)

def process_segment(segment):
    try:
        # Извлечение данных из сегмента
        data = segment.get('data')
        
        if data is None:
            raise ValueError("Segment does not contain 'data' field.")
        
        # Кодирование сообщения
        encoded_data = Hamming1511.encode_message(data)
        logger.info(f"Encoded data: {encoded_data}")
        
        # Внесение ошибки
        error_probability = 0.11
        transmitted_data = transmit_error(encoded_data, error_probability)
        logger.info(f"Transmitted data with error: {transmitted_data}")
        
        # Декодирование сообщения
        decoded_data = Hamming1511.decode_message(transmitted_data)
        logger.info(f"Decoded data: {decoded_data}")

        # Логирование данных перед проверкой
        logger.debug(f"Original data: '{data}'")
        logger.debug(f"Decoded data: '{decoded_data}'")

        # Проверка соответствия исходных данных и декодированных данных
        if data != decoded_data:
            logger.error('Сегмент потерян: данные не совпадают после декодирования')
            return Response({'error': 'Сегмент потерян: данные не совпадают после декодирования'}, status=400)

        segment['data'] = decoded_data

        if random() < 0.01:
            logger.error('Сегмент потерян')
            return Response({'error': 'Сегмент потерян'}, status=400)

        # Отправка данных в формате JSON в POST-запросе
        response = requests.post('http://192.168.251.124:5500/api/v1/segment/put', json=segment)

        # Логирование содержимого ответа
        logger.debug(f"Response status code: {response.status_code}")
        logger.debug(f"Response content: {response.content}")

        # Попытка декодирования ответа как JSON
        try:
            response_data = response.json()
        except json.JSONDecodeError:
            logger.error('Ответ сервера не является корректным JSON')
            return Response({'error': 'Ответ сервера не является корректным JSON'}, status=500)

        return Response(response_data)
    except requests.RequestException as e:
        logger.exception('Ошибка при отправке запроса')
        return Response({'error': 'Ошибка при отправке запроса'}, status=500)
    except Exception as e:
        logger.exception('Ошибка в process_segment')
        return Response({'error': 'Внутренняя ошибка сервера'}, status=500)

