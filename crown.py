###############################################################################
# Execute The Crown
# passing on the arguments received.
###############################################################################

# Standard library imports
import sys
sys.path.append('thecrown')

# Local application imports
from thecrown.main import run_the_crown

# Main program.
if __name__ == "__main__":
    run_the_crown(sys.argv[1:])
