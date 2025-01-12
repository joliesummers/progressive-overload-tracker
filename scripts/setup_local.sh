#!/bin/bash

# Create .env file for local development
cat > .env << EOL
# Database
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=workout_tracker

# Backend
DATABASE_URL=postgresql://postgres:postgres@db:5432/workout_tracker
JWT_SECRET=your_local_development_secret
JWT_ALGORITHM=HS256

# AWS (to be configured later)
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_DEFAULT_REGION=us-west-2
EOL

# Create local development docker-compose file
cat > docker-compose.local.yml << EOL
version: '3.8'

services:
  backend:
    build: 
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:postgres@db:5432/workout_tracker
    env_file:
      - .env
    volumes:
      - ./backend:/app
    depends_on:
      - db
    networks:
      - app-network
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    volumes:
      - ./frontend:/app
      - /app/node_modules
    depends_on:
      - backend
    networks:
      - app-network
    command: npm run dev

  db:
    image: postgres:15
    ports:
      - "5432:5432"
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres
      - POSTGRES_DB=workout_tracker
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - app-network

volumes:
  postgres_data:

networks:
  app-network:
    driver: bridge
EOL

# Create frontend Dockerfile
cat > frontend/Dockerfile << EOL
FROM node:20-slim

WORKDIR /app

COPY package*.json ./

RUN npm install

COPY . .

EXPOSE 3000

CMD ["npm", "run", "dev"]
EOL

# Make the script executable
chmod +x scripts/setup_local.sh

echo "Local development environment configuration created!"
echo "Next steps:"
echo "1. Review and modify the .env file with your preferred values"
echo "2. Run 'docker-compose -f docker-compose.local.yml build'"
echo "3. Run 'docker-compose -f docker-compose.local.yml up'"
