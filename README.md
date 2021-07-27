# markad-autocut
An automatic recording cut script for VDR using markad, in Python

This script will cut recordings made by [VDR](http://www.tvdr.de/) using the
[markad tool](https://github.com/kfb77/vdr-plugin-markad/).

This script accepts a single command line argument. It can be a path of a
single .rec directory or a path of VDR series recordings. For example:

```
python3 autocut.py /mnt/Videos/VDR/Wheeler_Dealers/Some_episode/2021-07-26.20.03.6-0.rec
```
or
```
python3 autocut.py /mnt/Videos/VDR/Wheeler_Dealers
```

This script will replace the original .ts files with the cut .ts file. **Be
careful, you might lose data!**

TODO:
- Use real logging instead of prints
- Allow changing configuration
- Add type hints
- Add tests

# License
Copyright (C) 2021 Ville-Pekka Vainio

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
