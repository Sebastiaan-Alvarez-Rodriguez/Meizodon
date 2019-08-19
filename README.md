# Meizodon
Research project about Android static analysis tools and their practical outputs. This framework is made to do 3 things: 
 * Installing tools. Currently supported:
   * Amandroid
   * Droidsafe
   * IccTa - IC3
   * JN-SAF
 * Running installed analysis tools in batches, over multiple cores
 * Analyzing batch output, to determine the classifications for each analysis

You want to add a method to the list above for your own research/fun? Please see the [Wiki](https://github.com/Sebastiaan-Alvarez-Rodriguez/Meizodon/wiki/Main). If you are done, put everything in a branch `add_<tool_name>` and make a merge request. Sharing is caring!

## Dataset
We generated results for the papers we wrote for this work. The results can be found in the [experiments branch](https://github.com/Sebastiaan-Alvarez-Rodriguez/Meizodon/tree/experiments).

# Requirements
You will only need Python v3.3 or newer (preferably the latest version compatible with python3).  

Of course, installers may have additional requirements. For each installer, read the readme, found in every installer's directory [here](https://github.com/Sebastiaan-Alvarez-Rodriguez/Meizodon/tree/master/installers)

# Installation
1. Install above requirements (if you do not have them already)
2. `git clone` this repository

# Usage
Run `run.py` with python and choose whatever you want. Current options:
 * `[A]nalyse`: analyse results from finished execution
 * `[E]xecute`: execute a tool on a dataset
 * `Re[S]tart`: restart an execution
 * `[I]nstall`: install a static analysis tool
 * `[R]econfigure`: Reconfigure a static analysis tool
 * `[Q]uit`: stop program

Options E and R only become available once you have installed a tool.
Option S only becomes available if you terminated execution at some point,
when it was not yet finished.
Option A only becomes available once you appear to have some results in `Meizodon/results/`

## Execution notes
During execution, you will not see any tool output,
since a lot of IO slows down progressing.
Also, multiple processes print lines all through each other, 
which is not very readable.
Instead, errors and information are logged to files: 
You will find a `results/<datetime>/<tool>/<apk>/out.log` and
`results/<datetime>/<tool>/<apk>/errors.log` for each analysis you perform. 
`out.log` contains standard output, and `errors.log` contains all errors,
and all warnings, if any.

During execution, only startup of analysis is printed, and finish status of analysis (success/succes+warnings/errors/timeout) is printed.

If your apk analysis execution was killed before it was finished, you can restart it with the `Re[S]tart` option.

# Output
This framework was created to support easy analysis of the outcome.
The relevant outputs are listed below.

## After execution
If execution is successful, the following output is available in `results/<datetime>/results.csv` (in this order):
 1. `<tool name>`
 2. `<apk name>`
 3. True/False, depending on whether apk listed actually is malware (this is given when providing paths to apk files)
 4. `<execution time>` in seconds (with accuracy depending on OS)
 5. True/False, depending on whether execution had warnings
 6. True/False, depending on whether execution was successful
Note: An error which was not fatal is not seen as error. So, an analysis can be successful, even though it produced errors, as long as it gives output (so no fatal error)

## After analysis
After analysing an execution, the following output is available in `analysed/<datetime>/out.csv` (in this order):
 1. `<tool name>`
 2. `<apk name>`
 3. True/False, depending on whether apk listed actually is malware
 4. `<execution time>` in seconds (with accuracy depending on OS)
 5. True/False, depending on whether execution had warnings
 6. True/False, depending on whether execution was successful
 7. True/False, depending on whether execution had timeout
 8. `<apk size>`, in bytes
 9. True/False, denoting whether the specific tool classifies `<apk_name>` as malware. This field is always False if analysis was not successful
Note: If timeout is reached, successful field is always set to False