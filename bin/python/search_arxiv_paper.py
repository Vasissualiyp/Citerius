import arxiv


# Construct the default API client.
client = arxiv.Client()

# Search for the 10 most recent articles matching the keyword "quantum."
search = arxiv.Search(
  query = "multiscale initial conditions hahn astrophysics",
  max_results = 10,
  sort_by = arxiv.SortCriterion.Relevance,
  sort_order = arxiv.SortOrder.Descending
)

results = client.results(search)

# `results` is a generator; you can iterate over its elements one by one...

for r in client.results(search):
  print(f"{r.title},{r.authors}")

# ...or exhaust it into a list. Careful: this is slow for large results sets.

#all_results = list(results)
#print([f"{r.title}, {r.authors}" for r in all_results])
