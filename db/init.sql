use test;

create table urls(
    id int NOT NULL auto_increment,
    url varchar(100),
    primary key (id)
) engine=InnoDB default charset=utf8;
