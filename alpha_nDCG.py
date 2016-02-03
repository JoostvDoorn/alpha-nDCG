import numpy as np
from math import log
from collections import defaultdict
from subprocess import check_output
from numpy.testing import assert_almost_equal


class keydefaultdict(defaultdict):
    def __missing__(self, key):
        if self.default_factory is None:
            raise KeyError( key )
        else:
            ret = self[key] = self.default_factory(key)
            return ret


class AlphaNDCG(object):
    def __init__(self, qrel_file):
        self.p = 0.5
        self.alpha = 0.5
        self.gfs = [lambda x: x]
        self.max_dcg = defaultdict(default_factory=0)
        self.topics = defaultdict(set)
        query_dd = lambda: defaultdict(int)
        document_dd = lambda: defaultdict(query_dd)
        self.qrel_judgements_dict = defaultdict(document_dd)
        self.load_qrel_judgements(qrel_file)
        self.discount = keydefaultdict(lambda rank: log(rank + 2, 2))

    def ideal_dcg(self, dids, topics, qid, depth=20):
        # Greedy approach
        topicgain = defaultdict(lambda: 1.0)
        dids_left = self.qrel_judgements_dict[qid].keys()
        dcgs = [0.0]
        for rank in range(min(len(dids), depth)):
            # Compute gain
            g = [self.ideal_gain(did, topics, qid, topicgain) for did in dids_left]
            idx = np.argmax(g)
            max_g = g[idx]
            max_did = dids_left[idx]
            # Increment topic gain
            for tid in topics:
                if self.qrel_judgements_dict[qid][max_did][tid] > 0:
                    topicgain[tid] *= 1.0 - self.alpha
            dids_left.pop(idx)
            dg = max_g / self.discount[rank]
            dcgs.append(dg+dcgs[-1])
        return dcgs[1:]

    def ideal_gain(self, did, topics, qid, topicgain):
        _gain = 0.0
        for tid in topics:
            if self.qrel_judgements_dict[qid][did][tid]>0:
                _gain += topicgain[tid]
        return _gain

    def load_qrel_judgements(self, qrel_file_path):
        with open(qrel_file_path, 'r') as f:
            for line in f:
                split_line = [value.strip() for value in line.split() if len(value.strip()) > 0]
                query_id, topic_id, document_id, judgement = split_line
                self.qrel_judgements_dict[query_id][document_id][topic_id] = int(judgement)
                if self.qrel_judgements_dict[query_id][document_id][topic_id] > 0:
                    self.topics[query_id].add(topic_id)

    def compute(self, dids, qid, depth=20):
        if qid not in self.topics:
            # TODO: idealIdealAlphaNdcg
            raise NotImplementedError
        if qid not in self.max_dcg:
            self.max_dcg[qid] = self.ideal_dcg(dids, self.topics[qid], qid)
        return self.ndcg(self.dcg(dids, self.topics[qid], qid), self.max_dcg[qid], depth=depth)

    def dcg(self, r, topics, qid):
        return reduce(lambda dcgs, d: self._dcg(d, topics, qid, dcgs), \
                      enumerate(r), [defaultdict(lambda: 1.0), [0]])[1][1:]

    def _dcg(self, d, topics, qid, dcgs):
        rank, did = d
        topicgain = dcgs[0]
        dg = self.gain(did, topics, qid, topicgain) / self.discount[rank]
        dcg = dcgs[1] + [dg + dcgs[1][-1]]
        return [topicgain, dcg]

    def gain(self, did, topics, qid, topicgain):
        _gain = 0.0
        for tid in topics:
            if self.qrel_judgements_dict[qid][did][tid] > 0:
                _gain += topicgain[tid]
                topicgain[tid] *= 1.0 - self.alpha
        return _gain

    def ndcg(self, r, max_dcg, depth=20):
        return r[depth-1]/max_dcg[depth-1]
