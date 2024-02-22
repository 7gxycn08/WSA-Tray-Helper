# WSA-Tray-Helper

Start/Stop and Monitor Windows Subsystem for Android (WSA) directly from your system tray!

## Features

- **Easy Start/Stop**: Control WSA directly from the system tray with a simple click.
- **Monitoring**: Visual indicators to show whether WSA is running or not.
- **Backup and Restore**: Easily backup and restore WSA's virtual drive, preserving internal files and apps.

## What's New in v1.0.1.2

- Added custom backup location via ini file to address backup issue with different configurations.
- Full list of changes available in [Releases](https://github.com/7gxycn08/WSA-Tray-Helper/releases/tag/v1.0.1.2).

## Getting Started

### Installation

1. Download the latest release from the [Releases page](https://github.com/7gxycn08/WSA-Tray-Helper/releases).
2. Run `WSA-Tray-Helper-win64-setup.exe` to install WSA-Tray-Helper.

### Usage

- **Start/Stop WSA**: Right-click the tray icon and select `Start WSA` or `Stop WSA`.
- **Monitor WSA**: The tray icon changes based on WSA's state:
  - Running: ![wsaon](https://github.com/7gxycn08/WSA-Tray-Helper/assets/121936658/36ecc638-4fc4-4327-b458-91caa27ebd4c)
  - Not Running: ![stop](https://github.com/7gxycn08/WSA-Tray-Helper/assets/121936658/6fe31d62-831a-425e-85ab-518bfb40789e)

### Adding Custom Commands

1. Navigate to the `dependencies` folder and open `Commands.ini`.
2. Under the `at_start` key, add your CMD commands (e.g., `at_start = command1, command2`).
3. Check the `Custom Commands` box in the tray menu to execute these commands everytime WSA starts.

## Preview

![Screenshot](https://github.com/7gxycn08/WSA-Tray-Helper/assets/121936658/407b6036-5cb5-4b1f-9737-f69b2324f29d)

## Contributing

We welcome contributions of all kinds! For major changes, please open an issue first to discuss what you'd like to change. Pull requests are also welcome.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

Copyright (c) 2023 7gxycn08

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
