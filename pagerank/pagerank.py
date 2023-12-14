import os
import random
import re
import sys

DAMPING = 0.85
SAMPLES = 10000


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    return pages


def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """
    distribution = {}

    if (len(corpus[page]) > 0):
        # Probability choose a link at random chosen from all pages in the corpus
        for p in corpus:
            distribution[p] = (1 - damping_factor)/len(corpus)

        # Probability choose a link at random linked to by `page`
        for pageLink in corpus[page]:
            distribution[pageLink] += damping_factor/len(corpus[page])
    else:
        # Equal probability if the page has no outgoing links,
        for p in corpus:
            distribution[p] = 1/len(corpus)

    return distribution

def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    distribution = {}
    for page in corpus:
        distribution[page] = 0

    # Choose random page at first
    page, _ = random.choice(list(corpus.items()))

    for i in range(1, n):
        curr_distribution = transition_model(corpus, page, damping_factor)
        
        # calculate the distribution
        for page in distribution:
            distribution[page] = ((i - 1) * distribution[page] + curr_distribution[page]) / i

        # choose new page based on the distribution
        pages, probabilities = zip(*curr_distribution.items())
        page = random.choices(pages, weights = probabilities, k = 1)[0]

    return distribution


def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    distribution = {}
    flag = True
    N = len(corpus)
    tolerance = 0.001

    for page in corpus:
        distribution[page] = 1/N

    while flag:
        flag = False

        for page in corpus:
            sigma = 0

            # sum of the sigma from all pageLink that links to the current page
            for pageLink in corpus:
                if pageLink != page and page in corpus[pageLink]:
                    sigma += distribution[pageLink]/len(corpus[pageLink])

            # calculate the new distribution of the current page
            newDistribution = (1 - damping_factor)/N + damping_factor*sigma

            # if any differences between new and old distribution is larger than tolerance
            # continue while loop
            if (abs(newDistribution - distribution[page]) > tolerance):
                flag = True

            distribution[page] = newDistribution
    
    return distribution


if __name__ == "__main__":
    main()
