DROP TABLE IF EXISTS person;
CREATE TABLE person (
    id int NOT NULL AUTO_INCREMENT KEY,
    name varchar(100) NOT NULL,
);
DROP TABLE IF EXISTS person;
CREATE TABLE person (
    id int NOT NULL AUTO_INCREMENT KEY,
    name varchar(100) NOT NULL,
);

DROP TABLE IF EXISTS actor;
CREATE TABLE actor (
    id int NOT NULL AUTO_INCREMENT KEY,
    movie int NOT NULL,
    person int NOT NULL,

    FOREIGN KEY (movie) REFERENCES movie(id),
    FOREIGN KEY (person) REFERENCES person(id)
);

DROP TABLE IF EXISTS dialogue;
CREATE TABLE dialogue (
    id int NOT NULL AUTO_INCREMENT KEY,
    movie int NOT NULL,
    language int NOT NULL,

    FOREIGN KEY (movie) REFERENCES movie(id),
    FOREIGN KEY (language) REFERENCES language(id)
);

DROP TABLE IF EXISTS subtitle;
CREATE TABLE subtitle (
    id int NOT NULL AUTO_INCREMENT KEY,
    movie int NOT NULL,
    language int NOT NULL,

    FOREIGN KEY (movie) REFERENCES movie(id),
    FOREIGN KEY (language) REFERENCES language(id)
);

DROP TABLE IF EXISTS production_country;
CREATE TABLE production_country (
    id int NOT NULL AUTO_INCREMENT KEY,
    movie int NOT NULL,
    country int NOT NULL,

    FOREIGN KEY (movie) REFERENCES movie(id),
DROP TABLE IF EXISTS actor;
CREATE TABLE actor (
    id int NOT NULL AUTO_INCREMENT KEY,
    movie int NOT NULL,
    person int NOT NULL,

    FOREIGN KEY (movie) REFERENCES movie(id),
    FOREIGN KEY (person) REFERENCES person(id)
);

DROP TABLE IF EXISTS dialogue;
CREATE TABLE dialogue (
    id int NOT NULL AUTO_INCREMENT KEY,
    movie int NOT NULL,
    language int NOT NULL,

    FOREIGN KEY (movie) REFERENCES movie(id),
    FOREIGN KEY (language) REFERENCES language(id)
);

DROP TABLE IF EXISTS subtitle;
CREATE TABLE subtitle (
    id int NOT NULL AUTO_INCREMENT KEY,
    movie int NOT NULL,
    language int NOT NULL,

    FOREIGN KEY (movie) REFERENCES movie(id),
    FOREIGN KEY (language) REFERENCES language(id)
);

DROP TABLE IF EXISTS production_country;
CREATE TABLE production_country (
    id int NOT NULL AUTO_INCREMENT KEY,
    movie int NOT NULL,
    country int NOT NULL,

    FOREIGN KEY (movie) REFERENCES movie(id),
    FOREIGN KEY (country) REFERENCES country(id)
);

DROP TABLE IF EXISTS poster;
CREATE TABLE poster (
    id int NOT NULL AUTO_INCREMENT KEY,
    movie int NOT NULL,
    image varchar(200) NOT NULL,

    FOREIGN KEY (movie) REFERENCES movie(id)
);

