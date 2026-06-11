# ImageDiff

Web tool to compare and highlight differences between two images (built with Flask and Pillow).

## Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/sev-/ImageDiff.git
   cd ImageDiff
   ```

2. **Create a virtual environment**

   **Linux / macOS**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

   **Windows**
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## Setting things up
### SCREENSHOT_DIR

 > The directory which stores the screenshots of the scenes

```tree
SCREENSHOTS_DIR/
  <target>/
    <build_number>/
      <movie_name>/
        998.png
        1000.png
        1100.png
```

### CACHE_DIR(Must be writable)

> The application builds comparison timelines and stores computed results in a cache.


Paths can be configured in config.py 

## Running the server

Start the application:

```bash
python app.py
```

Open in your browser:

```
http://127.0.0.1:5001
```
