
# Sokoban Verification

Sokoban, Japanese for “warehouse keeper”, is a transport puzzle created by
Hiroyuki Imabayashi in 1980. The goal of the game is simple, the warehouse
keeper must push the boxes to designated locations in the warehouse.
The warehouse is depicted as a grid with walls creating a labyrinth. The
following are rules that must be respected:

* Warehouse keeper can only move horizontally or vertically in the grid, one cell at a time.
* Boxes can only be pushed, not pulled, into an empty space.
* Warehouse keeper and boxes cannot enter “wall” cells.

In this project our goal is to try solving the Sokoban game using formal verification. To generalize the problem to some general board, we used Python, and to write and run all the verification specifications we used nuXmv.
## Authors

- [@BoazGur](https://github.com/BoazGur)
- [@Dekel23](https://github.com/Dekel23)


## Installation

1. Clone the repository:

```bash
git clone https://github.com/BoazGur/SokobanVerficiation
cd SokobanVerficiation
```

2. Ensure Python3 and libraries:

* Verify you have Python 3 installed and accessible through your system PATH.
* The required libraries (```subprocess```, ```itertools```, ```time```, ```os```, ```re```) should be included in most Python installations by default. 

3. Donwload nuXmv:

* Download nuXmv from: https://nuxmv.fbk.eu/download.html
* Add nuXmv to PATH.

## Usage

1. Create a Sokoban board:

* Within the ```boards/``` directory, create a new text file (```.txt```) containing your Sokoban board layout in XSB format (example below).

```
----#####----------
----#---#----------
----#$--#----------
--###--$##---------
--#--$-$-#---------
###-#-##-#---######
#---#-##-#####--..#
#-$--$----------..#
#####-###-#@##--..#
----#-----#########
----#######--------
```

Key symbols:

* ```@```   warehouse keeper
* ```+```   warehouse keeper on goal
* ```$```   box
* ```*```   box on goal
* ```#```   wall
* ```.```   goal
* ```-```   floor

2. Write you nuXmv specification:

* Modify the ```specs.txt``` file. Each line should contain a single nuXmv specification for verification.

```nuXmv
LTLSPEC !F(done)
```

3. Run the verification script:

* Open a terminal and navigate to the ```SokobanVerification/``` directory.


```bash
python3 run_nuxmv.py
```

Output:
* ```smvs/``` directory: Contains all generated nuXmv files during runtime.
* ```output/``` directory: Contains the verification results for each board using the standard method.
* ```outputBDD/``` directory: Contains the verification results for each board using the BDD method.
* ```outputSAT/``` directory: Contains the verification results for each board using the SAT method.
* ```iterativeSmvs/``` directory: Contains all generated nuXmv files during the iterative method.
* ```outputIterative/``` directory: Contains the verification results for each board using the iterative method.
