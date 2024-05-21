import logging
from rest_framework.decorators import api_view
from rest_framework.response import Response
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from .hamming_code import encode_message, decode_message
from .transmit_error import transmit_error
import requests
from random import random

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
    try:
        data = request.data.get('data')
        num = request.data.get('num')
        size = request.data.get('size')
        time = request.data.get('time')
        
        if not data or num is None or size is None or time is None:
            logger.error('Данные сегмента потеряны')
            return Response({'error': 'Данные сегмента потеряны'}, status=400)
        
        segment = {
            'data': data,
            'num': num,
            'size': size,
            'time': time,
        }
        
        response = process_segment(segment)
        return response
    except Exception as e:
        logger.exception('Внутренняя ошибка сервера')
        return Response({'error': 'Внутренняя ошибка сервера'}, status=500)

def process_segment(segment):
    try:
        # Извлечение данных из сегмента
        data = segment.get('data')

        encoded_data = encode_message(data)
        error_probability = 0.11
        transmitted_data = transmit_error(encoded_data, error_probability)
        decoded_data = decode_message(transmitted_data)
        
        if random() < 0.01:
            logger.error('Сегмент потерян')
            return Response({'error': 'Сегмент потерян'}, status=400)
        
        segment['data'] = decoded_data
        response = requests.post('http://pinspire.site:5500/api/v1/segment/put', json=segment)
        
        # Логирование содержимого ответа
        logger.debug(f"Response status code: {response.status_code}")
        logger.debug(f"Response content: {response.content}")
        
        # Попытка декодирования ответа как JSON
        try:
            response_data = response.json()
        except requests.JSONDecodeError:
            logger.error('Ответ сервера не является корректным JSON')
            return Response({'error': 'Ответ сервера не является корректным JSON'}, status=500)
        
        return Response(response_data)
    except requests.RequestException as e:
        logger.exception('Ошибка при отправке запроса')
        return Response({'error': 'Ошибка при отправке запроса'}, status=500)
    except Exception as e:
        logger.exception('Ошибка в process_segment')
        raise

