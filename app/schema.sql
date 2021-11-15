create table users (
    id integer primary key autoincrement not null,
    username varchar(255) not null,
    password varchar(255) not null
);

create table recipes (
    id integer primary key autoincrement not null,
    creator_id integer,
    recipe_name varchar(255) not null unique,
    foreign key (creator_id) references users (id)
);

create table ingredients (
    id integer primary key autoincrement not null,
    ingredient_name varchar(255) not null
);

create table recipe_ingredients (
    id integer primary key autoincrement not null,
    recipe_id integer,
    ingredient_id integer,
    foreign key (recipe_id) references recipes (id),
    foreign key (ingredient_id) references ingredients (id)
);