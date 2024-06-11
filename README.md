# stdlib_py_typist
Typing Game (in Japanese) Built with Python Standard Library Created for Personal Practice.  
This works without any external libraries. No need requirements.txt!  

## Requirements
- python3

## How to Use
1. Clone this repository
   ```sh
   git clone https://github.com/tanakai0/stdlib_py_typist.git
   cd stdlib_py_typist
   ```
2. Run the game
   ```sh
   python main.py
   ```
   Alternatively, you can activate `main.exe` if provided.

## 🎵 Sound Configuration

- **Windows OS Enhanced**: Windows users can take full advantage of the winsound library particularly optimized for Windows operating systems!

- **How to Configure**: Place your own .wav sound files in the assets/sound directory and rename variables in src/constants.py. Once you've added your sound files, you can set sounds for title screens, correct answers and incorrect answers.

## ⚠️ Caution

### Sound Support

1. **Windows OS Only**: This program utilizes the winsound library for sound effects. Therefore, sound may not work on operating systems other than Windows.

### Database Security

2. **SQL Injection**: This program uses SQL databases. Be cautious of SQL injection vulnerabilities when making changes to the database code.

### User Responsibility and License

3. **Use at Your Own Risk**: Usage and modification of this program are done at your own responsibility. Please refer to the MIT License for more details.

### Language in UI

4. **Target Audience and Language**: This project is primarily targeted at a Japanese audience. As such, quiz content, UI text, and some code comments are in Japanese.

## License
This project is licensed under the MIT License. See the LICENSE file for details.

