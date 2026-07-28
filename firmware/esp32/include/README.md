# include/

This directory is reserved for third-party or shared header files that do not
belong to a specific source module within `src/`.

**Examples of files placed here:**
- Vendor-provided `.h` files without a matching `.c` counterpart
- Shared type definitions used across multiple projects
- Platform abstraction headers

**For this firmware project**, all module headers live in `src/` beside their
corresponding `.c` files. This directory is present to maintain compatibility
with the standard ESP32 Arduino project layout.
