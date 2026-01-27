#COPIA DE MODELO
FROM python:3.11

#CREACION DE RUTA
WORKDIR /python_app

#INSTALACION DE DEPENDECIAS
COPY requirements.txt /python_app/requirements.txt

#INSTALACION DE DEPENDENCIAS
RUN pip install --no-cache-dir -r /python_app/requirements.txt

#ARCHIVOS NECESARIO PARA CODIGO
COPY backend /python_app/backend
COPY src /python_app/src
COPY models /python_app/models
COPY optional_helpers /python_app/optional_helpers
COPY generate_interactive_viz.py /python_app/generate_interactive_viz
COPY predict.py /python_app
COPY data /python_app/data

#FORZA LA CODIFICAION DE ENTRADA Y SALIDA
ENV PYTHONIOENCODING=utf-8
ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8

#EXPONE PUERTO UTILIZADO
EXPOSE 8000

#CORRE LA APLICACION
CMD ["uvicorn", "main:app", "--app-dir", "backend", "--host", "0.0.0.0", "--port", "8000"]


