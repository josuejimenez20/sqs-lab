import boto3
import json
import io
import os
from PIL import Image

s3 = boto3.client('s3')
sqs = boto3.client('sqs')

# Configuración del segundo bucket y SQS
DEST_BUCKET = 'elNombreBucketDestino'
QUEUE_URL = 'direccionDeTuSQS'

def lambda_handler(event, context):
    # 1. Capturar datos del evento de S3
    bucket_origen = event['Records'][0]['s3']['bucket']['name']
    nombre_archivo = event['Records'][0]['s3']['object']['key']
    
    # 2. Descargar y procesar imagen (Gris)
    response = s3.get_object(Bucket=bucket_origen, Key=nombre_archivo)
    img = Image.open(io.BytesIO(response['Body'].read())).convert('L')
    
    # 3. Guardar en bucket intermedio
    buffer = io.BytesIO()
    img.save(buffer, format="JPEG")
    s3.put_object(Bucket=DEST_BUCKET, Key=nombre_archivo, Body=buffer.getvalue())
    
    # 4. Enviar mensaje a SQS con la "dirección" del archivo
    mensaje = {
        "archivo": nombre_archivo,
        "bucket": DEST_BUCKET
    }
    
    sqs.send_message(
        QueueUrl=QUEUE_URL,
        MessageBody=json.dumps(mensaje)
    )
    
    return {
        'statusCode': 200,
        'body': json.dumps('Procesamiento inicial y envío a SQS exitoso')
    }