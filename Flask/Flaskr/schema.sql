drop table if exists entries ;
create table entries (
    id integer primary key autoincrement,
    title string not null,
    text string not null,
    abstract string not null,
    c_time string not null,
    renew_time string,
    page_view integer,
    user_view integer
);
