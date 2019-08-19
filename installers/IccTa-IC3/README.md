# IccTa-IC3
This installer installs the latest version of [IccTa](https://github.com/lilicoding/soot-infoflow-android-iccta) with IC3 setups.

## Requirements
The requirements are as follows:
 * Linux OS to run on
 * Unused port 1234 (for a mysql instance)

## Possible problems
One problem occuring regularly is:
`mysqld: error while loading shared libraries: libaio.so.1: cannot open shared object file: No such file or directory`.

In order to fix it, you can either:
* `sudo apt-get install libaio1` (or similar, requires root)
* Download libaio1 locally somehow, and add location to `LD_LIBRARY_PATH`

Another problem is
`Unable to determine if daemon is running: No such file or directory`
Just retry operation.

The last problem we know of
A `Java.Lang.NullPointerException` in soot, followed by many other errors.
This problem seems to appear if you have multiple installations of IccTa-IC3. If this is the case, and you have installation `A` and `B`, you will notice installation `A` works, while installation `B` does not work and crashes with a `NullPointerException`. Try to delete .ivy2, and .sbt directories in your home directory

## Notes
We assigned port 1234 for the mysql instance,
but this can be changed to another port, should this be required.
Just replace the '1234' in [install.py](https://github.com/Sebastiaan-Alvarez-Rodriguez/Meizodon/blob/master/installers/IccTa-IC3/install.py) on line 20 and on line 146 with your desired port.


Also:
A keen eye will see
```
[IccTA] epicc provider is used.
``` 
in the logs. This is not true. IC3 is used, and not epicc.