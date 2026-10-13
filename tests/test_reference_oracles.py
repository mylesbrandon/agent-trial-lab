"""Independent numeric oracles; these harness checks do not inflate corpus size."""
import importlib.util
import math
import random
import statistics
from decimal import Decimal, localcontext
from pathlib import Path


def test_numerical_references_against_decimal_statistics_and_invariants():
    root = Path(__file__).resolve().parents[1]
    randomizer = random.Random(20261012)
    modules = {}
    for number in range(5, 12):
        file = next((root/'tasks').glob(f'task_{number:03}_*/reference_solution.py'))
        spec = importlib.util.spec_from_file_location(f'task{number}', file)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        modules[number] = module
    checks = 0
    with localcontext() as context:
        context.prec = 80
        for _ in range(200):
            values = [randomizer.uniform(-1000, 1000) for _ in range(randomizer.randint(2, 15))]
            weights = [randomizer.uniform(0.01, 10) for _ in values]
            expected = sum(Decimal(v)*Decimal(w) for v,w in zip(values,weights))/sum(Decimal(w) for w in weights)
            assert math.isclose(modules[6].weighted_mean(values, weights), float(expected), rel_tol=1e-12, abs_tol=1e-12)
            norm = sum(Decimal(v)**2 for v in values).sqrt()
            assert math.isclose(modules[9].euclidean_norm(values), float(norm), rel_tol=1e-12)
            quartiles = statistics.quantiles(values, n=4, method='inclusive')
            for q, expected in zip((.25,.5,.75), quartiles):
                assert math.isclose(modules[7].linear_quantile(values,q), expected, rel_tol=1e-12, abs_tol=1e-12)
            cut=randomizer.randrange(1,len(values))
            left,right=values[:cut],values[cut:]
            def moments(items):
                return (len(items), statistics.mean(items), statistics.pvariance(items)*len(items))
            got=modules[10].merge_moments(moments(left),moments(right))
            expected=moments(values)
            assert got[0]==expected[0]
            assert math.isclose(got[1],expected[1],rel_tol=1e-10,abs_tol=1e-10)
            assert math.isclose(got[2],expected[2],rel_tol=1e-10,abs_tol=1e-10)
            scaled=modules[8].minmax_scale(values)
            assert min(scaled)==0 and max(scaled)==1 and len(scaled)==len(values)
            probs=modules[5].stable_softmax(values)
            assert all(0<=x<=1 for x in probs) and math.isclose(sum(probs),1,abs_tol=1e-12)
            shifted=modules[5].stable_softmax([x+10000 for x in values])
            assert all(math.isclose(a,b,rel_tol=1e-10,abs_tol=1e-12) for a,b in zip(probs,shifted))
            edges=[-500,-100,0,150,500]
            counts=[0]*4
            for x in values:
                for j,(a,b) in enumerate(zip(edges,edges[1:])):
                    if a<=x<b or (j==3 and x==b):
                        counts[j]+=1
                        break
            assert modules[11].histogram_counts(values,edges)==counts
            checks+=9
