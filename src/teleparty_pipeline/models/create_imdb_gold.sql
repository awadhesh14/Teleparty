CREATE TABLE IF NOT EXISTS imdb_titles (
    tconst VARCHAR PRIMARY KEY,
    titleType VARCHAR,
    primaryTitle VARCHAR,
    originalTitle VARCHAR,
    isAdult BOOLEAN,
    startYear INTEGER,
    endYear INTEGER,
    runtimeMinutes INTEGER,
    genres VARCHAR,
    averageRating DOUBLE,
    numVotes INTEGER,
    parentTconst VARCHAR,
    seasonNumber INTEGER,
    episodeNumber INTEGER
);
