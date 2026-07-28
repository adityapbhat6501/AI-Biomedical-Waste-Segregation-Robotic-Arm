# lib/

This directory is reserved for private project libraries — self-contained
code units that could be reused across multiple projects.

**Examples of files placed here:**
- A custom I2C scanner utility
- A motor encoder library specific to this hardware revision
- A FreeRTOS task wrapper library

**For this firmware project**, no private libraries are currently needed.
All functionality is implemented directly in `src/`. This directory is
present to maintain compatibility with PlatformIO and the Arduino project layout.

If you migrate this project to **PlatformIO**, place library directories here
with a `library.json` manifest in each sub-directory.
