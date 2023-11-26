from flask import Flask, request, jsonify
from flask_cors import CORS
from PIL import Image
import torch
import io
import numpy as np
from datetime import datetime

from database import BancoDeDados


app = Flask(__name__)
CORS(app)
device = torch.device('cpu')
model = torch.hub.load('ultralytics/yolov5', 'custom', path='./best.pt').to(device)

bd = BancoDeDados('database.db')

@app.route('/send_image', methods=['POST'])
def send_image():
    try:
        code = request.headers.get('code')  # Pega o código do cabeçalho da requisição
        image = request.data  # Pega a imagem do corpo da requisição

        print(code)

        image_pil = Image.open(io.BytesIO(image))
        # image_pil.save("temp.jpg")
        image_numpy = np.array(image_pil)
        
        results = model(image_numpy)
        my_number = ''

        # Ordenar as caixas delimitadoras da direita para a esquerda
        bboxes = results.pandas().xyxy[0].sort_values(by='xmin', ascending=False)

        # Extrair ROIs contidas nas bounding boxes
        for _, pred in bboxes.iterrows():
            # xmin, ymin, xmax, ymax = pred[:4]  # Extrair apenas as coordenadas (xmin, ymin, xmax, ymax)
            label = pred['name']  # Extrair o rótulo previsto

            my_number += label

        my_number = my_number[::-1]

        print(f'\n\nO número no display é {my_number}\n\n')

        bd.insert(code, my_number)

        return jsonify({"mensagem": f'Predição {my_number} salva com sucesso.'})

    except Exception as e:
        return jsonify({"erro": str(e)})
    
@app.route('/recent_values', methods=['GET'])
def recent_values():
    try:
        res = bd.search_recent()

        values = [{"code": row[0], "value": row[1], "date": row[2]} for row in res]

        return jsonify(values)

    except Exception as e:
        return jsonify({"erro": str(e)})
    
@app.route('/get_hydrometers', methods=["GET"])
def get_hydrometers():
    try:
        days = request.args.get('days', default = 1, type = int)
        print(days)
        res = bd.get_hydrometers_with_predictions(days)

        hydrometers = {}
        for id, code, name, value, date in res:
            if id not in hydrometers:
                hydrometers[id] = {'code': code, 'name': name, 'predictions': []}
            hydrometers[id]['predictions'].append({'value': value, 'date': date})

        return list(hydrometers.values())
    
    except Exception as e:
        return jsonify({"erro": str(e)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)

