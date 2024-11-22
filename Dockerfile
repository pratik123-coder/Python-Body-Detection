# Use an official Node.js image as the base for the container
FROM node:16

# Install Python, pip, and necessary dependencies for OpenCV
RUN apt-get update && apt-get install -y \
    python3 python3-pip libgl1 libglib2.0-0 && \
    pip3 install --upgrade pip

# Set working directory inside the container
WORKDIR /app

# Copy Node.js server files
COPY backend/package*.json ./
COPY backend/app.js ./

# Install Node.js dependencies
RUN npm install

# Copy Python files
COPY backend/PeopleCounter.py backend/Person.py ./

# Install Python dependencies
RUN pip3 install opencv-python opencv-python-headless numpy

# Create necessary directories for uploads and processed videos
RUN mkdir -p /app/uploads /app/processed

# Expose port 8000 for the Node.js server
EXPOSE 8000

# Start the Node.js server
CMD ["node", "app.js"]