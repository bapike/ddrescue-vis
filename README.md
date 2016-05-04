# ddrescue-vis: Visualize GNU ddrescue's log file as a Scalable Vector Graphics (SVG) image

This program takes a [GNU ddrescue](https://www.gnu.org/software/ddrescue/)
log file and constructs a Scalable Vector Graphics (SVG) image to
graphically depict where errors or unread regions lie on the disc/disk.
Naturally, its output depends on having significant knowledge of
the geometry of the disc/disk, which may be difficult.

Currently, it has only been used to visualize the scratches
on DVDs.
There is much room for improvement.

## Example usage
```bash
ddrescue -b 2048 -d -v /dev/sr0 image.iso image.log
ddrescue-vis image.log
```

## Dependencies
This depends on:
 * the python library [svgwrite](https://pypi.python.org/pypi/svgwrite/)
 * having logfiles produced from [GNU ddrescue](https://www.gnu.org/software/ddrescue/)

## Similar projects
Somewhat similar projects include:
 * [ddrescueview](http://ddrescueview.sourceforge.net) visualizes the state of the blocks in a ddrescue operation, but not where they are on the disk
 * [dvdisaster](http://dvdisaster.net/) can visualize the parts of a disc that are damaged, provided you have a error correction file [](see, e.g., http://dvdisaster.net/downloads/manual.pdf, page 23)

## License
Copyright 2015, 2016  Brian Pike

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

