
from utils import *


row_units = [cross(r, cols) for r in rows]
column_units = [cross(rows, c) for c in cols]
square_units = [cross(rs, cs) for rs in ('ABC','DEF','GHI') for cs in ('123','456','789')]

def define_diagonal():
    diagonal1 = []
    diagonal2 = []
    for i in range(0, len(rows)):
        value = rows[i] + cols[i]
        diagonal1.append(value)
    for i in range(0, len(rows)):
        value = rows[i] + cols[len(cols)-i-1]
        diagonal2.append(value)
    return [diagonal1, diagonal2]

diagonal_units = define_diagonal()
unitlist = row_units + column_units + square_units + diagonal_units

# TODO: Update the unit list to add the new diagonal units
unitlist = unitlist


# Must be called after all units (including diagonals) are added to the unitlist
units = extract_units(unitlist, boxes)
peers = extract_peers(units, boxes)


def naked_twins(values):
    """Eliminate values using the naked twins strategy.

    Parameters
    ----------
    values(dict)
        a dictionary of the form {'box_name': '123456789', ...}

    Returns
    -------
    dict
        The values dictionary with the naked twins eliminated from peers

    Notes
    -----
    Your solution can either process all pairs of naked twins from the input once,
    or it can continue processing pairs of naked twins until there are no such
    pairs remaining -- the project assistant test suite will accept either
    convention. However, it will not accept code that does not process all pairs
    of naked twins from the original input. (For example, if you start processing
    pairs of twins and eliminate another pair of twins before the second pair
    is processed then your code will fail the PA test suite.)

    The first convention is preferred for consistency with the other strategies,
    and because it is simpler (since the reduce_puzzle function already calls this
    strategy repeatedly).
    """ 
    # TODO: Implement this function!
    for value in values:
        #rows
        group = []
        for peer in peers[value]:
            if peer[0] == value[0]:
                group.append(peer)
        values = eliminate_twins(group, value, values)
        #columns
        group = []
        for peer in peers[value]:
            if peer[1] == value[1]:
                group.append(peer)
        values = eliminate_twins(group, value, values)
        #diagonals
        group = []
        if value in diagonal_units:
            for peer in peers[value]:
                if peer[1] == value[1]:
                    group.append(peer)
            values = eliminate_twins(group, value, values)
        #boxes
        group = []
        for square in square_units:
            if value in square:
                group = square
        values = eliminate_twins(group, value, values)

    return values


def eliminate_twins(peer_group, value, values):
    potential_twins = []
    twins = []
    for peer in peer_group:
        if len(values[peer]) == 2:
            potential_twins.append(peer)
    for i in range(0, len(potential_twins)):
        for j in range(i+1, len(potential_twins)):
            if (values[potential_twins[i]]) == (values[potential_twins[j]]):
                twins.append(values[potential_twins[i]])
    for twin in twins:
        for peer in peer_group:
            if values[peer] != twin:
                values[peer] = values[peer].replace(twin[0], '')
                values[peer] = values[peer].replace(twin[1], '')

    return values



    return values

def grid_values(grid):
    """Convert grid string into {<box>: <value>} dict with '123456789' value for empties.

    Args:
        grid: Sudoku grid in string form, 81 characters long
    Returns:
        Sudoku grid in dictionary form:
        - keys: Box labels, e.g. 'A1'
        - values: Value in corresponding box, e.g. '8', or '123456789' if it is empty.
    """
    values = []
    all_digits = '123456789'
    for c in grid:
        if c == '.':
            values.append(all_digits)
        elif c in all_digits:
            values.append(c)
    assert len(values) == 81
    return dict(zip(boxes, values))

def eliminate(values):
    """Eliminate values from peers of each box with a single value.

    Go through all the boxes, and whenever there is a box with a single value,
    eliminate this value from the set of values of all its peers.

    Args:
        values: Sudoku in dictionary form.
    Returns:
        Resulting Sudoku in dictionary form after eliminating values.
    """
    for key in boxes:
        if len(values[key]) == 1:
            value = values[key]
            for peer in peers[key]:
                '''remove the corresponding values'''
                if value in values[peer]: 
                    values[peer] = str.replace(values[peer], value, '')

    return values

def only_choice(values):
    """Finalize all values that are the only choice for a unit.

    Go through all the units, and whenever there is a unit with a value
    that only fits in one box, assign the value to this box.

    Input: Sudoku in dictionary form.
    Output: Resulting Sudoku in dictionary form after filling in only choices.
    """
    # TODO: Implement only choice strategy here
    for value in values:
        for option in values[value]:
            only_choice = True
            for peer in peers[value]:
                if option in values[peer]:
                    only_choice = False
            if only_choice:
                values[value] = option
            
    return values

def reduce_puzzle(values):
    stalled = False
    while not stalled:
        # Check how many boxes have a determined value
        solved_values_before = len([box for box in values.keys() if len(values[box]) == 1])

        # Your code here: Use the Eliminate Strategy
        values = eliminate(values)
        # Your code here: Use the Only Choice Strategy
        values = only_choice(values)
        values = naked_twins(values)
        # Check how many boxes have a determined value, to compare
        solved_values_after = len([box for box in values.keys() if len(values[box]) == 1])
        # If no new values were added, stop the loop.
        stalled = solved_values_before == solved_values_after
        # Sanity check, return False if there is a box with zero available values:
        if len([box for box in values.keys() if len(values[box]) == 0]):
            return False
    return values

def search(values):
    "Using depth-first search and propagation, create a search tree and solve the sudoku."
    # First, reduce the puzzle using the previous function
    values = reduce_puzzle(values)
    if values is False:
        return False
    if is_solved(values):
        return values
        
    # Choose one of the unfilled squares with the fewest possibilities
    index = ''
    lowest_num = 9
    for value in values:
        if len(values[value]) > 1:
            if len(values[value]) < lowest_num:
                lowest_num = len(values[value])
                index = value
                
    # Now use recursion to solve each one of the resulting sudokus, and if one returns a value (not False), return that answer!

    for option in values[index]:
        copy = values.copy()
        copy[index] = option
        result = search(copy)
        if result:
            return result

def is_solved(values):
    for value in values:
        if len(values[value]) > 1:
            return False
    return True

def solve(grid):
    """Find the solution to a Sudoku puzzle using search and constraint propagation

    Parameters
    ----------
    grid(string)
        a string representing a sudoku grid.
        
        Ex. '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'

    Returns
    -------
    dict or False
        The dictionary representation of the final sudoku grid or False if no solution exists.
    """
    values = grid2values(grid)
    values = search(values)
    return values

if __name__ == "__main__":
    diag_sudoku_grid = '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    display(grid2values(diag_sudoku_grid))
    result = solve(diag_sudoku_grid)
    display(result)

    try:
        import PySudoku
        PySudoku.play(grid2values(diag_sudoku_grid), result, history)

    except SystemExit:
        pass
    except:
        print('We could not visualize your board due to a pygame issue. Not a problem! It is not a requirement.')
