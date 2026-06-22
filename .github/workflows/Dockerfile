# Use the official Python 3.11 image
FROM python:3.11

# Set the working directory inside the cloud server
WORKDIR /code

# Install system-level dependencies required by PyMuPDF
RUN apt-get update && apt-get install -y mupdf mupdf-tools

# Copy the requirements file and install Python libraries
COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# Copy your actual application code into the server
COPY . /code/

# Open the specific network port that Hugging Face expects
EXPOSE 7860

# Start the FastAPI application on port 7860
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]
