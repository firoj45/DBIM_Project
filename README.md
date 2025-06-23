# DBIM Toolkit - FastAPI + React

A simple web application with a FastAPI backend and React frontend.

## Setup Instructions

### Backend Setup

1. Create and activate a Python virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install the required Python packages:
   ```bash
   pip install -r requirements.txt
   ```

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install the required npm packages:
   ```bash
   npm install
   ```

## Running the Application

### Development Mode

1. Start the FastAPI backend (from the project root):
   ```bash
   uvicorn main:app --reload
   ```

2. In a new terminal, start the React development server (from the frontend directory):
   ```bash
   cd frontend
   npm start
   ```

3. The application should open in your default browser at `http://localhost:3000`

### Production Build

1. Build the React app for production:
   ```bash
   cd frontend
   npm run build
   ```

2. Start the FastAPI server (it will serve the built React app):
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000
   ```

3. Access the application at `http://localhost:8000`

## API Endpoints

- `GET /api/hello` - Test endpoint that returns a welcome message

## Project Structure

- `/backend` - FastAPI application code
- `/frontend` - React application code
- `main.py` - Main FastAPI application file
- `requirements.txt` - Python dependencies

## License

This project is open source and available under the MIT License.
