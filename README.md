# WriteSong

A simple Flask web app that lets users write text, convert it to Suno-style lyrics using OpenAI, and generate a song using a placeholder API call. Users can sign up, log in, and manage their own lyrics.

## Features
- User sign‑up, log in, and logout.
- Convert any text to Suno-style lyrics (requires `OPENAI_API_KEY`).
- Placeholder API call to convert lyrics to a song.
- Each user can view their own saved lyrics.

## Setup
1. Install dependencies:
   ```bash
   python -m pip install -r requirements.txt
   ```
2. Export your OpenAI API key:
   ```bash
   export OPENAI_API_KEY=your_key_here
   ```
3. Run the app:
   ```bash
   python app.py
   ```
4. Visit `http://localhost:5000` in your browser.

## Notes
- The `generate_song` function in `app.py` is a placeholder for a real API call to convert lyrics to music.
- Database is stored in `db.sqlite3` in the project root.
