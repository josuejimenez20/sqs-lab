import boto3
import json
import io
from PIL import Image, ImageOps, ImageDraw

s3 = boto3.client('s3')
BUCKET_FINAL = 'NombreSegundoBucket'

def lambda_handler(event, context):
    for record in event['Records']:
        # 1. Leer instrucciones de SQS
        body = json.loads(record['body'])
        nombre_archivo = body['archivo']
        bucket_intermedio = body['bucket']
        
        # 2. Descargar de la vitrina intermedia
        response = s3.get_object(Bucket=bucket_intermedio, Key=nombre_archivo)
        img = Image.open(io.BytesIO(response['Body'].read())).convert("RGB")
        
        # 3. Recorte Circular
        size = (min(img.size), min(img.size))
        img = ImageOps.fit(img, size, centering=(0.5, 0.5))
        mask = Image.new('L', size, 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0) + size, fill=255)
        img.putalpha(mask)
        
        # 4. Guardar en bucket final (como PNG para transparencia)
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        
        s3.put_object(
            Bucket=BUCKET_FINAL,
            Key=nombre_archivo.replace('.jpg', '.png'),
            Body=buffer.getvalue(),
            ContentType='image/png'
        )
        
    return {"status": "OK", "message": "Recorte finalizado"}