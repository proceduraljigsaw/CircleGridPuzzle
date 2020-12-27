# Circle Grid Puzzle Generator

This thing generates lasercut jigsaw puzzles based on something I found on the web. All is in millimeters. Max piece circles must be at least 2x min piece circles for this to work, it will not generate anything otherwise. I plan to fix this behaviour.
You may export to SVG in three ways:
* **Export SVG**: export each piece individually outlined, with red 0.1mm outline. Piece vectors overlap on piece borders. This is good if you want to separate and nest the pieces for individual cutting on a milling machine or something with "nonzero" cut width.
* **Export SVG Colored**: Same as before, but with black 1mm outline and randomly colored pieces. 
* **Export SVG no overlap**: piece contours broken down in non-overlapping paths. No vector duplication, ideal for direct laser cutting.

## How it works

The algorithm is pretty naive, thrashes the memory and it's pretty inefficient, but it ultimately works. Expect generation times in the range of several seconds to 2 minutes for large sizes. It's artificially limited to 80x80 because more than that takes a lot of time to generate and it's impractical.anyways.

## Limitations and quirks

* Quickly thrown together, very un-pythonic and not well thought. But it works.


