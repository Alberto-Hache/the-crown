# Paths to project source.
RUN_PATH=./
SOURCE_PATH=./thecrown/
TEST_PATH=./tests/

# Path for outputs.
RUN_OUTPUT_PATH=$(SOURCE_PATH)output/
TEST_OUTPUT_PATH=$(TEST_PATH)test_outputs/

export PYTHONPATH:=./$(SOURCE_PATH):./$(TEST_PATH):$(PYTHONPATH)

# Installation of required libraries.
init:
	pip install -r requirements.txt

# Run a default game.
run:
	python $(RUN_PATH)crown.py

# Run all unit tests.
test:
	python $(TEST_PATH)test_players.py -v
	python $(TEST_PATH)test_crownutils.py -v
	python $(TEST_PATH)test_board.py -v
	python $(TEST_PATH)test_gameplay.py -v

# Run some specific test.
test-latest:
	python $(TEST_PATH)test_players.py -v

# Run profiling for key negamax() function at depth 5.
profile:
	python $(TEST_PATH)profiler.py Profiler.negamax_depth_5 -v \
	> $(TEST_OUTPUT_PATH)profile_negamax_depth_5.txt

# Run profiling for key negamax() function at depth 4.
profile-4:
	python $(TEST_PATH)profiler.py Profiler.negamax_depth_4 -v \
	> $(TEST_OUTPUT_PATH)profile_negamax_depth_4.txt

# Run profiling for some auxiliary game functions.
profile-aux:
	python $(TEST_PATH)profiler.py Profiler.generate_pseudomoves -v \
	> $(TEST_OUTPUT_PATH)profile_generate_pseudomoves.txt
	python $(TEST_PATH)profiler.py Profiler.pre_evaluate_pseudomoves -v \
	> $(TEST_OUTPUT_PATH)profile_pre_evaluate_pseudomoves.txt
	python $(TEST_PATH)profiler.py Profiler.position_attacked -v \
	> $(TEST_OUTPUT_PATH)profile_position_attacked.txt

# Clean unnecessary files.
clean-run:
	rm -f $(RUN_OUTPUT_PATH)*.txt
clean-test:
	rm -f $(TEST_OUTPUT_PATH)profile_*.txt
	rm -f $(TEST_OUTPUT_PATH)output.txt
clean: clean-run clean-test
