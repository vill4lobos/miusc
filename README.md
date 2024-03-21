# miusc

Suite of miscellanous experimental tools related to music.

## What we have at the moment

#### Under development

These are tools that need improvements or extra features to achieve satisfactory results, but already work as intended: 

- pyalbum
    
    TUI application for viewing albums ordered by genre

- miusconv

    CLI application to convert lossless music files to lossy containers

#### Being rewritten

These are some old tools that I am refactoring at the moment, mainly to achieve POSIX compliance:

- miuscheck

    CLI application to possibly check for transcodes in lossless files (used together with miusconv)

- miusget

    CLI application to find music online by name (used together with pyalbum)

## Usage

Like most things in this repository at the moment, this is a work in progress too.

But you can clone this repository, and run the package inside the project directory:

```
python3 pyalbum
```

Or change the permissions, and run with Bash:

```
chmod +x miusconv.sh
./miusconv.sh
```
## Future Improvements

- Create wrapper for selecting tools
- Rewrite bashisms for portability
- Maybe write some web UI for pyalbum
- Review improvements for miuscheck detection
- Release all 4 tools on main
