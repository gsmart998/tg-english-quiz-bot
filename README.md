# Quiz Bot

## Overview

This project is a Telegram bot that allows users to create and participate in vocabulary quizzes. Users can manually add word-translation pairs and test their knowledge through interactive quizzes.

### Features

- Add custom word-translation pairs.
    
- Randomized quiz questions with multiple-choice answers.
    
- Tracks user scores and awards points for correct answers.
    
- Configurable quiz notifications.
    

## Installation

### Prerequisites

- Python 3.12 or higher
    
- SQLite (for the database)
    
- Dependencies listed in `requirements.txt`
    

### Steps

1. **Clone the repository**:
    
    ```
    git clone https://github.com/gsmart998/tg-english-quiz-bot
    cd tg-english-quiz-bot
    ```
    
2. **Create and activate a virtual environment**:
    
    ```
    python -m venv venv
    source venv/bin/activate  # Linux/MacOS
    venv\Scripts\activate     # Windows
    ```
    
3. **Install dependencies**:
    
    ```
    pip install -r requirements.txt
    ```
    

    
5. **Configure environment variables**: Create a `.env` file in the project root and configure the following:
    
    ```
    TG_TOKEN=<Your Telegram Bot Token>
    DATABASE_URL="sqlite:///db/sqlite.db"
    ```
    
6. **Run the bot**:
    
    ```
    python src/app/main.py
    ```
    

---

## Project Structure

```
├── db
│   └── sqlite.db           # Database file
├── logs
│   └── app.log             # Log file
├── README.md
├── requirements.txt        # Dependencies
└── src
    ├── app
    │   ├── app_config.py   # Bot configuration
    │   ├── bot_handlers.py # Bot command handlers
    │   ├── bot.py          # Telegram bot logic
    │   ├── handlers.py     # Event handlers
    │   ├── logger_config.py # Logging configuration
    │   ├── main.py         # Main entry point
    │   ├── scheduler.py    # Quiz notification scheduler
    │   └── text_templates.py # Predefined text messages
    ├── database
    │   ├── crud.py         # Database operations
    │   ├── database.py     # Database initialization
    │   ├── models.py       # ORM models
```

---

## Dependencies

Dependencies are managed using `requirements.txt`:

```
APScheduler==3.11.0
certifi==2024.8.30
charset-normalizer==3.4.0
greenlet==3.1.1
idna==3.10
pyTelegramBotAPI==4.23.0
python-dotenv==1.0.1
requests==2.32.3
SQLAlchemy==2.0.36
telebot==0.0.5
typing_extensions==4.12.2
tzlocal==5.2
urllib3==2.2.3
```



---

## Usage

### Telegram Bot

- **Main Commands**:
    
    - `/start` - Start the bot.
        
    - `/quiz` - Start a new quiz.
        
    - `/score` - Show your current score.
        
    - `/add` - Add new word-translation pairs.
        
    - `/settings` - Configure bot settings.
        
    - `/help` - List of available commands.
        

### Adding New Words

To add new words, send the following command:

```
/add
en_word_1  ru_word_1
en_word_2  ru_word_2
```

**Note**: There must be **two spaces** between the word and its translation!
### Launch quiz
After adding your words, you can run the quiz with the `/quiz` command.

---

## Logging

All significant events, including errors and successful operations, are logged in the `logs/app.log` file.

---

## Future Enhancements

- Implement a leaderboard.
    
- Expand support for multiple languages. 