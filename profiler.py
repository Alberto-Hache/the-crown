import cProfile
import tests

cProfile.run('tests.profiler()', sort='tottime')
