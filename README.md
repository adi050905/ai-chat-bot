# Advanced AI Chatbot with Database Storage

A sophisticated Flask-based chatbot application with persistent data storage using SQLite database.

- **Google Gemini AI**: Primary AI service for intelligent responses
- **Fallback AI**: Backup responses when primary service is unavailable
- **Message History**: Complete conversation history with timestamps
- **Session Management**: Create, rename, delete, and switch between sessions
- **Statistics**: Real-time database statistics and user metrics

### 🎨 Advanced Frontend
- **Modern UI**: Glassmorphism design with gradient backgrounds
- **Dark/Light Theme**: Toggle between themes
- **Responsive Design**: Works on desktop and mobile
- **Animated Particles**: Interactive background animations

### Prerequisites
1. **Clone or download** this project to your local machine

2. **Run the startup script** (Windows):
   ```bash
   start_chatbot.bat
   ```

   Or **manual setup**:
   ```bash
   # Create virtual environment
   python -m venv chatbot_env
   
   # Activate virtual environment (Windows)
   chatbot_env\Scripts\activate
   
   # Install dependencies
   pip install -r requirements.txt
   
   # Run the application
   python app.py
   ```

3. **Open your browser** and go to:
   ```
   http://localhost:5000
   ```

## Project Structure

```
ai-chatbot/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── start_chatbot.bat     # Windows startup script
├── .env.example          # Environment variables template
├── templates/
│   └── index.html        # Main chat interface
├── static/
│   ├── style.css         # Styling
│   └── script.js         # Frontend functionality
└── chatbot_env/          # Virtual environment (auto-created)
```

## Customization

### Adding Real AI Integration

The current implementation uses simple rule-based responses. To integrate with a real AI service:

1. **OpenAI Integration**: 
   - Get an API key from OpenAI
   - Copy `.env.example` to `.env` and add your API key
   - Modify the `get_ai_response()` function in `app.py`

2. **Other AI Services**:
   - Update the `get_ai_response()` function to call your preferred AI API
   - Add necessary dependencies to `requirements.txt`

### Customizing the Interface

- **Styling**: Edit `static/style.css` to change colors, fonts, and layout
- **Functionality**: Modify `static/script.js` to add new features
- **Layout**: Update `templates/index.html` to change the structure

## API Endpoints

- `GET /` - Main chat interface
- `POST /api/chat` - Send message and get AI response
- `GET /api/health` - Health check endpoint

## Development

### Running in Development Mode

The application runs with `debug=True` by default, enabling:
- Auto-reload on code changes
- Detailed error messages
- Debug toolbar

### Adding Features

1. Backend changes: Modify `app.py`
2. Frontend changes: Update files in `static/` and `templates/`
3. Dependencies: Add to `requirements.txt`

## Troubleshooting

### Common Issues

1. **Port already in use**: Change the port in `app.py` (line with `app.run()`)
2. **Dependencies not found**: Make sure virtual environment is activated
3. **Permission errors**: Run as administrator on Windows

### Logs and Debugging

- Check the console output where you ran the application
- Browser developer tools for frontend issues
- Flask debug mode provides detailed error information

## Contributing

Feel free to fork this project and submit pull requests for improvements!

## License

This project is open source and available under the MIT License.