# Semantic Space Clustering Recommender System
A Recommender System based on Semantic Space Clustering.

## How to use
The MovieLens 1M database saved in the data directory only contains the movie names, so to gather the plots, genres and reviews you must first extract it from IMDb by running:
```bash
python datahandler/imdb_extractor.py
```
Once fetched the info, you can now run the Recommender System:
```bash
python3 main.py
```
## Dependencies
- [Gensim](https://github.com/RaRe-Technologies/gensim): Library that implements the Paragraph Vector algorithm.
- [IMDbPy](https://imdbpy.sourceforge.io/): Used for searching on IMDb.
- [ImdbPie](https://github.com/richardasaurus/imdb-pie): Used for retrieving reviews from IMDb.
- [NumPy](http://www.numpy.org): Normal computing.
- [Scikit-Learn](https://github.com/scikit-learn/scikit-learn): Used to normalize the DensityPeakCluster decision graph, allowing to automatically choose the density and distance threshold.
- [Matplotlib](http://matplotlib.sourceforge.net/): Used only if you want to plot the clusters for debugging.
