# Results

this branch contains the results of our experiments
for publications about this tool.
If you have any questions, please contact the authors.

## Removed data
To compress data, and to not distribute apks from
[AndroZoo](https://androzoo.uni.lu/) without their permission,
we removed directories with the following names:
 * apktool-gen
 * assets
 * bin
 * lib
 * res
 * src

Also, we removed all files matching the following patterns:
 * `*.class`
 * `*.dex`


## Downloading
To download these results, one could execute
```sh
git clone git@github.com:Sebastiaan-Alvarez-Rodriguez/Meizodon.git -b experiments
```
or
```sh
wget https://github.com/Sebastiaan-Alvarez-Rodriguez/Meizodon/blob/experiments/results.tar.gz
```