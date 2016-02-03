# alpha-nDCG

Python implementation of alpha nDCG, tested with ndeval (test program code is provided, except no files to try them out).

## Usage

Single query, returns score
```python
from alpha_nDCG import AlphaNDCG
alpha_nDCG = AlphaNDCG('ndeval-format-qrel')
alpha_nDCG.compute(['docid1', 'docid2', 'docid3'], 'qid')
```

Multiple queries, returns dict of scores
```python
alpha_nDCG.compute_multi([
	(['docid1', 'docid2', 'docid3'], 'qid1'),
	(['docid1', 'docid2', 'docid3'], 'qid2')
])
```

By default computes alpha-nDCG@20. To change depth set depth.

```python
alpha_nDCG.compute(['docid1', 'docid2', 'docid3'], 'qid', depth=20)
```

## References
Clarke, Charles LA, et al. "Novelty and diversity in information retrieval evaluation." Proceedings of the 31st annual international ACM SIGIR conference on Research and development in information retrieval. ACM, 2008. [\[pdf\]](http://plg.uwaterloo.ca/~gvcormac/novelty.pdf)
