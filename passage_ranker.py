from sentence_transformers import SentenceTransformer, CrossEncoder, util
# from principles_chunk import get_chunk
import json


def get_principles_to_chapter():
    with open('principles_to_chapter.json', 'r') as f:
        out = json.load(f)
    return out


def longest_sublist(l):
    sublist = []
    counter = 0
    for i in range(len(l)):
        if counter + len(l[i]) < 2000:
            sublist.append(l[i])
            counter += len(l[i])
        else:
            break
    return "".join(sublist)


def get_chunk():

    corpus = {k: longest_sublist(corpus[k]) for k in list(corpus.keys())}
    return list(corpus.values())


class PassageRanker():
    """Retrive the passage which most matches the query. """

    def __init__(self, passages, adjacent=0):
        self.passages = passages
        self.bi_encoder = self._load_bi_encoder()
        self.cross_encoder = self._load_cross_encoder()
        self.adjacent = adjacent

        truncated_passages = [p[-2000:] for p in self.passages]
        self.corpus_embeddings = self.bi_encoder.encode(
            truncated_passages,
            convert_to_tensor=True,
            show_progress_bar=True
        )

    def _load_bi_encoder(self):
        bi_encoder = SentenceTransformer('multi-qa-mpnet-base-dot-v1')
        bi_encoder.max_seq_length = 2048
        return bi_encoder

    def _load_cross_encoder(self):
        cross_encoder = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-12-v2')
        return cross_encoder

    def search(self, query, top_k=3):
        question_embedding = self.bi_encoder.encode(query, convert_to_tensor=True)
        question_embedding = question_embedding

        hits = util.semantic_search(
            question_embedding,
            self.corpus_embeddings,
            top_k=top_k
        )[0]

        cross_inp = [[query, self.passages[hit['corpus_id']]] for hit in hits]
        cross_scores = self.cross_encoder.predict(cross_inp)

        # Sort results by the cross-encoder scores
        for idx in range(len(cross_scores)):
            hits[idx]['cross-score'] = cross_scores[idx]

        hits = sorted(hits, key=lambda x: x['cross-score'], reverse=True)
        return self._get_chunk_passage(hits)

    def _get_chunk_passage(self, hits):
        res = []
        for hit in hits:
            position = hit['corpus_id']

            for offset in range(0, self.adjacent + 1):
                res.append({
                    'text': self.passages[position + offset].strip(),
                    'score': hit['cross-score']
                })

        return res


def load_passage_ranker():
    chunks = get_chunk()
    return PassageRanker(chunks, adjacent=1)


if __name__ == '__main__':
    ranker = load_passage_ranker()
