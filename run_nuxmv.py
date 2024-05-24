from smv_writer import SMVWriter
from smv_writer_iterative import SMVWriterIterative
import time
import subprocess
import os
import re

dictonary = {
    "shtrudel": "@",
    "plus": "+",
    "dollar": "$",
    "star": "*",
    "solamit": "#",
    "dot": ".",
    "minus": "-"
}

def main():
    # Get boards txt files
    board_paths = os.listdir('boards/')
    writers = import_writers(board_paths)
    
    # For each SMV_writer, create the SMV file
    for i, writer in enumerate(writers):
        writer.write_smv()
        writer.export_smv('smvs/' + board_paths[i][:-4] + '.smv')

    # For each board file run the SMV tests, not including borad8
    for i, path in enumerate(board_paths[:-1:]):
        # Part 2, simple nuXmv run, we run board7 in SAT mode instead
        if path[:-4] != "board7":
            run('smvs/' + path[:-4] + '.smv')
        # Part 3, run in SAT mode
        run_SAT('smvs/' + path[:-4] + '.smv')
        # Part 3, run in BDD mode
        run_BDD('smvs/' + path[:-4] + '.smv')
        # Part 4, run with our iterative algorithm
        run_iterative(writers[i].board, path[:-4])
    
    # For part 4, Run board8.txt on SAT and iterative (checking on bigger more complex boards)
    run_iterative(writers[-1].board, "board8")
    run_SAT('smvs/' + "board8" + '.smv')

def run_iterative(board, _id):
    board_copy = board.copy() # Make a copy of the board
    total_time = 0 # Set nuXmv run time to 0
    box_counter = sum(row.count('$') for row in board_copy) # Contains the initial number of boxes on the floor
    i = 0 # set iteration to 0
    while any('$' in row for row in board_copy): # While there is box on floor
        i += 1

        if i > box_counter: # If iteration bigger than initial number of boxes on the floor, set board as unsolvable
            print(f'Board {_id} not winnable')
            break
        
        # Create new SMV interative writer, and create the SMV file
        path = 'iterativeSmvs/' + _id + '_box_iteration' + str(i) + '.smv' # Path for new SMV file
        writer_iterative = SMVWriterIterative(specs_path='specs.txt', board=board_copy)
        writer_iterative.write_smv()
        writer_iterative.export_smv(path)

        start = time.time()

        # Run nuXmv in interactive mode
        nuxmv_process = subprocess.Popen(
            ["nuXmv", "-int", path],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            universal_newlines=True
        )

        # Send SAT commands to nuXmv, with max 15 steps
        commands = "go_bmc\ncheck_ltlspec_bmc -k 15\nquit\n"
        stdout, _ = nuxmv_process.communicate(input=commands)

        end = time.time()
        total_time += end - start

        # Save output to file
        output_filename = path.split(".")[0] + ".out"
        with open('outputIterative/' + output_filename.split('/')[1], "w") as f:
            # Write the output and the time to file
            f.write(stdout)
            f.write("time in seconds: " + str(end - start))
        print(f"Output saved to outputIterative/{output_filename}")

        # Extract new state of board
        board_copy = regex_proccessing(stdout, len(writer_iterative.board), len(writer_iterative.board[0]))
        if board_copy is None: # If returned None than not solvable
            print(f'Board {_id} not winnable')
            break

    # Save total nuXmv run time to file
    with open('outputIterative/' + _id + '_time.txt', 'w') as f:
        f.write('time in seconds: ' + str(total_time))

# Reading the output file and returning the new board state, if not solvable return None
def regex_proccessing(output, rows, cols):
    # Search if not solable
    if re.search('-- specification.*is true', output) or re.search('-- no counterexample found with bound 15', output):
        return None
    
    # Modify the board with all the last changes
    board = [[] for _ in range(rows)]
    for i in range(rows):
        for j in range(cols):
            last_change = re.findall(f'v_{i}{j} = ([a-z]+)', output)[-1]
            board[i].append(dictonary[last_change])

    return board

# Run SMV
def run(path):
    # Run nuXmv
    nuxmv_process = subprocess.Popen(
        ["nuXmv", path],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        universal_newlines=True
    )

    stdout, _ = nuxmv_process.communicate()

    # Save output to file
    output_filename = path.split(".")[0] + ".out"
    with open('output/' + output_filename.split('/')[1], "w") as f:
        # Write the output to file
        f.write(stdout)
    print(f"Output saved to output/{output_filename}")

# Run SMV in BDD mode
def run_BDD(path):
    start = time.time()

    # Run nuXmv in interactive mode
    nuxmv_process = subprocess.Popen(
        ["nuXmv", "-int", path],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        universal_newlines=True
    )

    # Send BDD commands to nuXmv
    commands = "go\ncheck_ltlspec\nquit\n"
    stdout, _ = nuxmv_process.communicate(input=commands)

    end = time.time()

    # Save output to file
    output_filename = path.split(".")[0] + ".out"
    with open('outputBDD/' + output_filename.split('/')[1], "w") as f:
        # Write the output and the time to file
        f.write(stdout)
        f.write("time in seconds: " + str(end - start))
    print(f"Output saved to outputBDD/{output_filename}")

# Run SMV in SAT mode
def run_SAT(path):
    start = time.time()
    
    # Run nuXmv in interactive mode
    nuxmv_process = subprocess.Popen(
        ["nuXmv", "-int", path],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        universal_newlines=True
    )

    # Send SAT commands to nuXmv
    # If SMV is for board 8, run for 30 steps, else, for 15.
    commands = ''
    if path == 'smvs/board8.smv':
        commands = "go_bmc\ncheck_ltlspec_bmc -k 30\nquit\n"
    else:
        commands = "go_bmc\ncheck_ltlspec_bmc -k 15\nquit\n"
    stdout, _ = nuxmv_process.communicate(input=commands)

    end = time.time()
    
    # Save output to file
    output_filename = path.split(".")[0] + ".out"
    with open('outputSAT/' + output_filename.split('/')[1], "w") as f:
        # Write the output and the time to file
        f.write(stdout)
        f.write("time in seconds: " + str(end - start))
    print(f"Output saved to outputSAT/{output_filename}")

# Return list of SMV_writers for each board file
def import_writers(board_paths):
    writers = []

    for path in board_paths:
        writers.append(SMVWriter('boards/' + path, 'specs.txt'))

    return writers


if __name__ == '__main__':
    main()