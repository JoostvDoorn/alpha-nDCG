def test_AlphaNDCG():
    import time
    # TODO: Figure out if I can add these files in the repo
    alpha_nDCG_obj = AlphaNDCG('example/qrels-for-ndeval.txt')
    ndeval = "ndeval"
    qrel = "example/qrels-for-ndeval.txt"
    results = "example/results-cata.txt"
    output = check_output([ndeval, qrel, results])
    keys = None
    results = dict()

    for line in output.splitlines():
        if keys is None:
            keys = line.split(",")
        else:
            split_line = line.split(",")
            results[split_line[1]] = {key:split_line[i] for i, key in enumerate(keys)}
    ranking = defaultdict(list)
    with open('results-cata.txt', 'r') as f:
        for line in f.readlines():
            qid, _, did, rank, score, _ = line.split()
            ranking[qid].append(did)
    for qid in results:
        actual = alpha_nDCG_obj.compute(ranking[qid], qid, depth=20)
        desired = float(results[qid]['alpha-nDCG@20'])
        assert_almost_equal(actual, desired, decimal=3)