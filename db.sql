SET FOREIGN_KEY_CHECKS=0;

DROP TABLE IF EXISTS country;
CREATE TABLE country (
    id int NOT NULL AUTO_INCREMENT KEY,
    name varchar(100) NOT NULL,

    UNIQUE(name)
);

DROP TABLE IF EXISTS language;
CREATE TABLE language (
    id int NOT NULL AUTO_INCREMENT KEY,
    name varchar(100) NOT NULL,

    UNIQUE (name)
);

DROP TABLE IF EXISTS person;
CREATE TABLE person (
    id int NOT NULL AUTO_INCREMENT KEY,
    name varchar(100) NOT NULL,

    UNIQUE(name)
);

DROP TABLE IF EXISTS rating;
CREATE TABLE rating (
    id int NOT NULL AUTO_INCREMENT KEY,
    name varchar(20) NOT NULL,

    UNIQUE(name)
);

DROP TABLE IF EXISTS movie;
CREATE TABLE movie (
    id int NOT NULL AUTO_INCREMENT KEY,
    title varchar(50) NOT NULL,
    release_year varchar(4),
    rating int NOT NULL,
    duration varchar(7),
    description varchar(1000) NOT NULL,
    stars varchar(8) NOT NULL,

    FOREIGN KEY (rating) REFERENCES rating(id),

    UNIQUE(title)
);

DROP TABLE IF EXISTS genre;
CREATE TABLE genre (
    id int NOT NULL AUTO_INCREMENT KEY,
    name varchar(30) NOT NULL,

    UNIQUE(name)
);

DROP TABLE IF EXISTS movie_genre;
CREATE TABLE movie_genre (
    id int NOT NULL AUTO_INCREMENT KEY,
    movie int NOT NULL,
    genre int NOT NULL,

    FOREIGN KEY (movie) REFERENCES movie(id),
    FOREIGN KEY (genre) REFERENCES genre(id),

    UNIQUE(movie, genre)
);

DROP TABLE IF EXISTS actor;
CREATE TABLE actor (
    id int NOT NULL AUTO_INCREMENT KEY,
    movie int NOT NULL,
    person int NOT NULL,

    FOREIGN KEY (movie) REFERENCES movie(id),
    FOREIGN KEY (person) REFERENCES person(id),

    UNIQUE(movie, person)
);

DROP TABLE IF EXISTS director;
CREATE TABLE director (
    id int NOT NULL AUTO_INCREMENT KEY,
    movie int NOT NULL,
    person int NOT NULL,

    FOREIGN KEY (movie) REFERENCES movie(id),
    FOREIGN KEY (person) REFERENCES person(id),

    UNIQUE(movie, person)
);

DROP TABLE IF EXISTS dialogue;
CREATE TABLE dialogue (
    id int NOT NULL AUTO_INCREMENT KEY,
    movie int NOT NULL,
    language int NOT NULL,

    FOREIGN KEY (movie) REFERENCES movie(id),
    FOREIGN KEY (language) REFERENCES language(id),

    UNIQUE(movie, language)
);

DROP TABLE IF EXISTS subtitle;
CREATE TABLE subtitle (
    id int NOT NULL AUTO_INCREMENT KEY,
    movie int NOT NULL,
    language int NOT NULL,

    FOREIGN KEY (movie) REFERENCES movie(id),
    FOREIGN KEY (language) REFERENCES language(id),

    UNIQUE(movie, language)
);

DROP TABLE IF EXISTS production_country;
CREATE TABLE production_country (
    id int NOT NULL AUTO_INCREMENT KEY,
    movie int NOT NULL,
    country int NOT NULL,

    FOREIGN KEY (movie) REFERENCES movie(id),

    UNIQUE(movie, country)
);

DROP TABLE IF EXISTS actor;
CREATE TABLE actor (
    id int NOT NULL AUTO_INCREMENT KEY,
    movie int NOT NULL,
    person int NOT NULL,

    FOREIGN KEY (movie) REFERENCES movie(id),
    FOREIGN KEY (person) REFERENCES person(id),

    UNIQUE(movie, person)
);

DROP TABLE IF EXISTS dialogue;
CREATE TABLE dialogue (
    id int NOT NULL AUTO_INCREMENT KEY,
    movie int NOT NULL,
    language int NOT NULL,

    FOREIGN KEY (movie) REFERENCES movie(id),
    FOREIGN KEY (language) REFERENCES language(id),

    UNIQUE(movie, language)
);

DROP TABLE IF EXISTS subtitle;
CREATE TABLE subtitle (
    id int NOT NULL AUTO_INCREMENT KEY,
    movie int NOT NULL,
    language int NOT NULL,

    FOREIGN KEY (movie) REFERENCES movie(id),
    FOREIGN KEY (language) REFERENCES language(id),

    UNIQUE(movie, language)
);

DROP TABLE IF EXISTS production_country;
CREATE TABLE production_country (
    id int NOT NULL AUTO_INCREMENT KEY,
    movie int NOT NULL,
    country int NOT NULL,

    FOREIGN KEY (movie) REFERENCES movie(id),
    FOREIGN KEY (country) REFERENCES country(id),

    UNIQUE(movie, country)
);

DROP TABLE IF EXISTS poster;
CREATE TABLE poster (
    id int NOT NULL AUTO_INCREMENT KEY,
    movie int NOT NULL,
    image varchar(200) NOT NULL,

    FOREIGN KEY (movie) REFERENCES movie(id),

    UNIQUE(movie, image)
);

-- VIEWING STUFF STARTS HERE --
DROP TABLE IF EXISTS theatre;
CREATE TABLE theatre (
    id int NOT NULL AUTO_INCREMENT KEY,
    name varchar(50) NOT NULL,

    UNIQUE(name)
);

DROP TABLE IF EXISTS seat;
CREATE TABLE seat (
    id int NOT NULL AUTO_INCREMENT KEY,
    theatre int NOT NULL,
    `row` int NOT NULL,
    `col` int NOT NULL,
    
    FOREIGN KEY (theatre) REFERENCES theatre(id),

    UNIQUE(theatre,`row`, `col`)
);

DROP TABLE IF EXISTS viewing;
CREATE TABLE viewing (
    id int NOT NULL AUTO_INCREMENT KEY,
    movie int NOT NULL,
    theatre int NOT NULL,
    starts datetime NOT NULL,
    ends datetime NOT NULL,

    FOREIGN KEY (movie) REFERENCES movie(id),
    FOREIGN KEY (theatre) REFERENCES theatre(id),

    UNIQUE(theatre, starts),
    UNIQUE(theatre, ends)
);

DROP TABLE IF EXISTS ticket;
CREATE TABLE ticket (
    id int NOT NULL AUTO_INCREMENT KEY,
    name varchar(20) NOT NULL,
    price decimal NOT NULL,

    UNIQUE(name)
);

DROP TABLE IF EXISTS booking;
CREATE TABLE booking (
    id int NOT NULL AUTO_INCREMENT KEY,
    viewing int NOT NULL,
    email varchar(100) NOT NULL,
    ticket int NOT NULL,

    FOREIGN KEY (ticket) REFERENCES ticket(id)
    -- don't think there is a possible unique constraint here
);

DROP TABLE IF EXISTS booked_seat;
CREATE TABLE booked_seat (
    id int NOT NULL AUTO_INCREMENT KEY,
    booking int NOT NULL,
    seat int NOT NULL,

    FOREIGN KEY (booking) REFERENCES booking(id),
    FOREIGN KEY (seat) REFERENCES seat(id),

    UNIQUE(booking, seat)
);

DROP VIEW IF EXISTS viewingXseat;
CREATE VIEW viewingXseat AS
SELECT 
    viewing.id AS "viewing", 
    seat.id AS "seat"
FROM
    viewing
INNER JOIN
    theatre 
ON
    theatre.id = viewing.theatre
INNER JOIN
    seat
ON
    seat.theatre = theatre.id;

DROP VIEW IF EXISTS booked_viewingXseat;
CREATE VIEW booked_viewingXseat AS 
SELECT 
    viewing.id AS "viewing", 
    seat.id AS "seat"
FROM 
    booked_seat 
INNER JOIN 
    booking 
ON 
    booking.id = booked_seat.booking
INNER JOIN 
    viewing 
ON
    viewing.id = booking.viewing
INNER JOIN 
    theatre
ON
    theatre.id = viewing.theatre
INNER JOIN 
    seat 
ON
    seat.id = booked_seat.id;

DROP VIEW IF EXISTS vacant_viewingXseat;
CREATE VIEW vacant_viewingXseat AS
SELECT
    *
FROM
    viewingXseat
WHERE NOT EXISTS (
    SELECT 
        *
    FROM
        booked_viewingXseat
    WHERE
        viewingXseat.viewing
            =
        booked_viewingXseat.viewing
        AND
        viewingXseat.seat 
            =
        booked_viewingXseat.seat
    LIMIT 1
);



SET FOREIGN_KEY_CHECKS=1;


