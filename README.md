# WSA-Tray-Helper
**Start/Stop and Monitor Windows Subsystem for Android from System Tray.**


## Preview:


![Screenshot 2024-02-12 085831](https://github.com/7gxycn08/WSA-Tray-Helper/assets/121936658/407b6036-5cb5-4b1f-9737-f69b2324f29d)


# v1.0.1.0 New Features:
- **Added WSA Backup and Restore options.**
- **Backup and restore WSA virtual drive contained in `LocalCache` folder locally.**
- **Useful to preserve WSA internal files and apps when doing a complete reinstall.**
- **Due to WSA limitations apps will require to be reinstalled to show up again In windows but app data will be preserved.** 
- **Full list of changes in** ![Releases](https://github.com/7gxycn08/WSA-Tray-Helper/releases/tag/v1.0.1.0)


# How to add custom commands:
- **In Dependencies folder there is a file called `Commands.ini`**
- **Under at_start key add your cmd commands ex: `at_start = command1, command2, command3` space sensitive.**
- **Then check the `Custom Commands` box In tray menu.**
- **When WSA starts the commands will be executed in the background.**
- **You can run stuff like:**
- **`adb connect 127.0.0.1:58526`**
- **`adb shell sh /storage/emulated/0/Android/data/moe.shizuku.privileged.api/start.sh`**
- **`adb kill-server`**


## Contributing

**Pull requests are welcome. For major changes, please open an issue first**
**to discuss what you would like to change.**

## License

MIT License

Copyright (c) 2023 7gxycn08

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.




