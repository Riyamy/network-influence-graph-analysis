Place your source interaction CSVs here. At minimum the repo expects an edge list CSV named edges.csv with columns:

- source: id of source node (string or integer)
- target: id of target node
- weight: numeric interaction weight (optional, defaults to 1)
- timestamp: optional, ISO format
- interaction_type: optional

If your raw data contains events (userA, userB, timestamp, event_type), preprocess them into an aggregated edge list with counts or summed weights per pair.
