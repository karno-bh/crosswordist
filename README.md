# Crosswordist

Crosswordist is an application that generates random crosswords.

![Execution Example](images/crossword_032.svg)

Example of a generated crossword.

Generated examples in this document are done by some free found file of the English words. However,
it seems that are not only English words, but whatever whenever typed in some text :-). So, I
don't know if those words either exist or not, valid or invalid. **These words just exist in the
file of all English words that I have**.

## Getting Started

### Installation

Get the repository content. Change directory to 'compressed_seq_ops' and install 'fast' version of
compressed bitmap index by running setup.py in this directory.
```shell
$ python setup.py install
```
**Technical note**, for better isolation run installations in a separate Python virtual environment.

The compilation depends on the C runtime installed on your system. If the compilation fails, find
relevant information how to install prerequisites of C runtime for C based Python
extension compilation. *It is possible to run crossword generation without compilation of C module
you will need to specify that 'slow' index (i.e., written in Python) should be used.*

In the root directory of the repository run install of setup.py for the application itself. Once the
application is installed you may run it by typing "crosswordist"
```shell
$ crosswordist
usage: crosswordist [-h] [-m {index,crossword}] -i INDEX [-wf WORDS_FILE] [-gsi GRID_SIZE] [-gu GRID_UNUSED_PERCENTAGE] [-gsy {X,D,NO}] [-gto GRID_GENERATION_TIMEOUT_SECONDS] [-gw GRID_MIN_WORD_LENGTH] [-cit {fast,slow}]
                    [-cgt CROSSWORD_GENERATION_TIMEOUT_SECONDS] [-o OUTPUT_DIR] [-nc NUMBER_OF_CROSSWORDS] [-pp PICTURE_PIXELS] [-v {0,1,2}]
crosswordist: error: the following arguments are required: -i/--index
```

### Running

To run the application you need to provide an index file (compressed bitmaps by word lengths). This
index file should be prepared before. Thus, the application runs in two modes. Firstly, the index
file should be prepared and then this file should be used for crossword generation. For both modes
index file is mandatory. To prepare an index file you need to have a file with words. Words' file
should be provided by external sources and not is included. **Note**, a file of words should be in
upper case and each word is a line in a file.
```shell
# File names are given for example
# The process requires a time. To see prints you may add "-v 2" (verbosity level) to the arguments
$ crosswordist --mode index --words-file ~/Download/words_upper.txt --index /tmp/index.json
```
**Technical note**, the separation of index creation and its usage is mainly driven by the fact that
index preparation takes a time while written in Python. Interesting, that while profiling the most
slow space is converting stream of booleans to bytes. On the other hand this operation should be
performed (almost) only once and thus instead of struggling with performance index preparation moved
out as a separate step. The expressiveness and readability of Python counts more than converting
one file with static data to another even if it takes half a minute.

When index preparation is done. You may run a crossword generation. For all parameters that affect
the generation you may run the application with '--help' flag. However, all parameters have their
predefined values and should be provided by a need. In the most rudiment form you may run the
generation by only specifying the index file.
```shell
$ crosswordist -i /tmp/index.json
$ ls -l ./out | wc -l
101
```
This will create 'out' directory in your current directory and will generate crossword graphic
files in SVG format (currently only SVG is supported). Not all crosswords are fully filled since
finding solution is still NP Hard and a generation may be timed out. If you run the generation in
most available verbose mode ("-v 2") the generated grids and solutions will be printed out. For 
example:

```shell
$ crosswordist -i /tmp/index.json -v 2
Starting Crosswords Generation. 
The operation is time intensive, please be patient...
Generating Crossword Number 1
Generated Random Grid:
■ ■ □ □ □ □ ■ □ □ □ ■
■ □ □ □ □ □ ■ □ □ □ □
■ □ □ □ □ □ ■ □ □ □ □
□ □ □ ■ ■ □ □ □ □ □ □
□ □ □ □ □ □ □ □ □ □ ■
□ □ □ □ □ □ □ □ □ □ □
■ □ □ □ □ □ □ □ □ □ □
□ □ □ □ □ □ ■ ■ □ □ □
□ □ □ □ ■ □ □ □ □ □ ■
□ □ □ □ ■ □ □ □ □ □ ■
■ □ □ □ ■ □ □ □ □ ■ ■

Result: Found. Passed time: 0.13107085227966309 seconds. Found ratio: 1.0.
■ ■ S A P S ■ A A R ■
■ O M B R E ■ B M E T
■ C A R U M ■ A P P D
R T L ■ ■ I S C H A R
P A L E A R C T I C ■
G E N T L E F O L K S
■ T E A R T H R O A T
C E S T U I ■ ■ C G I
U R S I ■ R O C H E ■
R I E S ■ E V I U S ■
■ D S M ■ D A I S ■ ■
...
```

If you did not compile the 'fast' compressed index you are still able to run the crossword
generation by providing as an argument the type of index. The following command will generate
crosswords by using 'slow' index and as well will print generated solutions:
```shell
$ crosswordist -i /tmp/index.json --compressed-index-type slow -v 2
Starting Crosswords Generation. 
The operation is time intensive, please be patient...
Generating Crossword Number 1
Generated Random Grid:
■ □ □ □ □ ■ □ □ □ □ ■
□ □ □ □ □ ■ □ □ □ □ ■
□ □ □ □ □ □ □ □ □ □ □
□ □ □ ■ ■ □ □ □ □ □ □
■ □ □ □ □ □ □ □ □ □ □
■ ■ ■ □ □ □ □ □ ■ ■ ■
□ □ □ □ □ □ □ □ □ □ ■
□ □ □ □ □ □ ■ ■ □ □ □
□ □ □ □ □ □ □ □ □ □ □
■ □ □ □ □ ■ □ □ □ □ □
■ □ □ □ □ ■ □ □ □ □ ■

Result: Found. Passed time: 2.772378444671631 seconds. Found ratio: 1.0.
■ D S R I ■ A R F S ■
R A C O N ■ M O R T ■
E M A C E R A T I O N
H A W ■ ■ A D E M P T
■ L L A N G O L L E N
■ ■ ■ V O G U L ■ ■ ■
D E M I P E S A D E ■
M A E N A D ■ ■ O M V
T R I G L Y C E R Y L
■ L E E R ■ L P C D F
■ A R R Y ■ R A Y E ■
...
```

## Background

This project was born as a challenge if it's possible to generate randomly a crossword. The idea is
pretty simple: given a list of words, a random valid crossword should be generated from the list.
Since there are many types of crosswords and this project is a kind of challenge american crossword
type was chosen (american crossword type has much more intersections and words than other types).

### Technical Details for Nerds

From the technical point of view the main algorithm is built from two main parts. First the
generation of the valid grid and second is the finding a solution for the grid. 

Generating a grid is a Las Vegas randomized algorithm. By given percentage and symmetry type 
a grid is generated following the rules (i.e., one rule: there should be a for some minimal word
length).

The second part and the heart is the finding solution - a Constraint Satisfaction Problem.
The crossword is represented as a multigraph (i.e., the word and all its intersection with other
words by cells coordinates). First, from all words in the crossword the word with minimal variants
is chosen (this is in order to reduce the search space). Once a word is substituted all its letters 
are propagated to adjacent words. If a propagation has a meaning, that is propagated letters have a
variation that forms a word then, again, from all words in the crossword one with minimal variants
is chosen. If a dead end is reached, the algorithm backtracks.

Since one of the main parts of the algorithm is searching words, there should be a fast way to find
words by provided letters (and as a derivative existence of words by a given letters, and the number
of variations). This is done by a compressed bitmap index. The compression itself is a homemade byte
based compressed index (yes, I know about machine word aligning and so on, for the simplicity byte
based compressed index chose). The compressed bitmap index allows making queries faster, jumping
over the unneeded chunks in another indexes while performing boolean operations. As well, it allows
to reduce the storage. There are two implementation of compressed bitmap index. One is in Python,
second is a CPython C extension.

**A note regarding alphabets**, currently only latin alphabet is supported. This is not too hard
to enhance the algorithm to take an arbitrary alphabets and non-english corpus of words. For the
sake of simplicity only English is used.

