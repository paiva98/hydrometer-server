# Use uma imagem base do Python
FROM python:3.8

# Defina o diretório de trabalho no contêiner
WORKDIR /app

# Instale a biblioteca libGL
RUN apt-get update && apt-get install -y libgl1-mesa-glx

# Copie o arquivo requirements.txt para o contêiner
COPY requirements.txt ./

# Instale as dependências listadas em requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copie o restante dos arquivos do seu aplicativo para o contêiner
COPY . .

# Execute o seu aplicativo
CMD [ "python", "./app.py" ]
